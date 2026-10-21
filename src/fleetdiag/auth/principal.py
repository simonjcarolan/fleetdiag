"""Identification des clients de l'API.

COMPOSANT PARTAGÉ : ce module est importé tel quel par FleetPortal (produit
client). Son interface publique (`Principal`, `authenticate`, constantes
SCOPE_*) est figée par contracts/public_api_v1.json.
"""

from __future__ import annotations

import hashlib
import hmac
import os
from dataclasses import dataclass, field
from typing import FrozenSet, Mapping, Optional, Tuple

SCOPE_ENGINEERING = "report:engineering"
SCOPE_WORKSHOP = "report:workshop"
SCOPE_FLEET = "report:fleet"

KNOWN_SCOPES = frozenset({SCOPE_ENGINEERING, SCOPE_WORKSHOP, SCOPE_FLEET})

# Clé d'environnement : FLEETDIAG_KEY_<CLIENT_ID>=<sha256 de la clé>;<scope>,<scope>
_ENV_PREFIX = "FLEETDIAG_KEY_"

Keyring = Mapping[str, Tuple[str, FrozenSet[str]]]  # client_id -> (sha256, scopes)


class AuthenticationError(Exception):
    """Clé absente, inconnue ou invalide."""


@dataclass(frozen=True)
class Principal:
    client_id: str
    scopes: FrozenSet[str] = field(default_factory=frozenset)

    def has_scope(self, scope: str) -> bool:
        return scope in self.scopes


def _hash(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def load_keyring_from_env(environ: Optional[Mapping[str, str]] = None) -> dict:
    """Construit le trousseau à partir des variables d'environnement.

    Les valeurs sont injectées par le déploiement (jamais lues depuis un
    fichier par le code applicatif).
    """
    environ = os.environ if environ is None else environ
    keyring = {}
    for name, value in environ.items():
        if not name.startswith(_ENV_PREFIX):
            continue
        digest, _, scopes = value.partition(";")
        client_id = name[len(_ENV_PREFIX) :].lower()
        keyring[client_id] = (digest.strip(), frozenset(s for s in scopes.split(",") if s))
    return keyring


def authenticate(api_key: str, *, keyring: Optional[Keyring] = None) -> Principal:
    """Retourne le `Principal` associé à une clé d'API."""
    if not api_key:
        raise AuthenticationError("clé d'API manquante")
    keyring = load_keyring_from_env() if keyring is None else keyring
    digest = _hash(api_key)
    for client_id, (expected, scopes) in keyring.items():
        if hmac.compare_digest(digest, expected):
            unknown = set(scopes) - KNOWN_SCOPES
            if unknown:
                raise AuthenticationError(f"scopes inconnus pour {client_id} : {sorted(unknown)}")
            return Principal(client_id=client_id, scopes=frozenset(scopes))
    raise AuthenticationError("clé d'API inconnue")

"""Contrat commun des règles de traitement."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Protocol

from fleetdiag.auth import Principal
from fleetdiag.core import Finding


@dataclass(frozen=True)
class RuleContext:
    """Informations disponibles pour toutes les règles d'un même rapport."""

    principal: Optional[Principal] = None
    vehicle_id: str = ""


class Rule(Protocol):
    """Une règle transforme une liste de défauts en une nouvelle liste.

    Conventions (voir docs/ARCHITECTURE.md) :
    - une règle est pure : elle ne modifie pas la liste reçue ;
    - elle expose un attribut `name` unique (snake_case) ;
    - elle est enregistrée dans `engine.DEFAULT_RULES`, dont l'ORDRE compte.
    """

    name: str

    def apply(self, findings: List[Finding], ctx: RuleContext) -> List[Finding]: ...

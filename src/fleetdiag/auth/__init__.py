"""Authentification des clients — COMPOSANT PARTAGÉ AVEC FLEETPORTAL (interface figée)."""

from .principal import (
    KNOWN_SCOPES,
    SCOPE_ENGINEERING,
    SCOPE_FLEET,
    SCOPE_WORKSHOP,
    AuthenticationError,
    Principal,
    authenticate,
    load_keyring_from_env,
)

__all__ = [
    "KNOWN_SCOPES",
    "SCOPE_ENGINEERING",
    "SCOPE_FLEET",
    "SCOPE_WORKSHOP",
    "AuthenticationError",
    "Principal",
    "authenticate",
    "load_keyring_from_env",
]

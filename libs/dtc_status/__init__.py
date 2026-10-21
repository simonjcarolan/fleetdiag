"""Décodage de l'octet de statut DTC (ISO 14229-1, service 0x19).

BIBLIOTHÈQUE VENDORISÉE — voir VENDORED.md. Ne pas modifier dans ce dépôt.
"""

from .status import StatusByte, describe

__all__ = ["StatusByte", "describe"]
__version__ = "2.4.1"

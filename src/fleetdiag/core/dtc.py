"""Modèle d'un enregistrement DTC tel que remonté par les calculateurs."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

_CODE_RE = re.compile(r"^[PCBU][0-3][0-9A-F]{3}$")

SYSTEMS = {
    "P": "powertrain",
    "C": "chassis",
    "B": "body",
    "U": "network",
}


def normalize_code(code: str) -> str:
    """Normalise un code DTC SAE J2012 (ex. ``p0301`` -> ``P0301``)."""
    normalized = code.strip().upper()
    if not _CODE_RE.match(normalized):
        raise ValueError(f"code DTC invalide : {code!r}")
    return normalized


def system_of(code: str) -> str:
    return SYSTEMS[normalize_code(code)[0]]


@dataclass(frozen=True)
class DtcRecord:
    """Lecture brute d'un DTC sur un calculateur (ECU)."""

    code: str
    status: int
    ecu: str
    occurrences: int = 1
    last_seen: Optional[str] = None  # horodatage ISO 8601, UTC

    def __post_init__(self) -> None:
        object.__setattr__(self, "code", normalize_code(self.code))
        if not 0 <= self.status <= 0xFF:
            raise ValueError(f"statut hors bornes pour {self.code} : {self.status!r}")
        if self.occurrences < 1:
            raise ValueError("occurrences doit être >= 1")

    @classmethod
    def from_dict(cls, data: dict) -> "DtcRecord":
        status = data["status"]
        if isinstance(status, str):
            status = int(status, 16)
        return cls(
            code=data["code"],
            status=status,
            ecu=data["ecu"],
            occurrences=int(data.get("occurrences", 1)),
            last_seen=data.get("last_seen"),
        )

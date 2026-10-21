"""Représentation interne d'un défaut enrichi, manipulée par les règles.

`Finding` est un type INTERNE : il peut évoluer librement. Seul le format
produit par `fleetdiag.api.schemas.Report.to_dict()` est contractuel.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Optional

from dtc_status import StatusByte

from .dtc import DtcRecord, system_of
from .severity import Severity


@dataclass(frozen=True)
class Finding:
    code: str
    ecu: str
    status: int
    occurrences: int
    description: str
    severity: Severity
    last_seen: Optional[str] = None

    @property
    def system(self) -> str:
        return system_of(self.code)

    @property
    def status_byte(self) -> StatusByte:
        return StatusByte(self.status)

    @property
    def active(self) -> bool:
        return self.status_byte.is_active()

    def with_(self, **changes) -> "Finding":
        return replace(self, **changes)

    @classmethod
    def from_record(cls, record: DtcRecord, description: str, severity: Severity) -> "Finding":
        return cls(
            code=record.code,
            ecu=record.ecu,
            status=record.status,
            occurrences=record.occurrences,
            description=description,
            severity=severity,
            last_seen=record.last_seen,
        )

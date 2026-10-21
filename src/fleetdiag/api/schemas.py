"""Objets de réponse de l'API publique.

Le dictionnaire produit par `Report.to_dict()` est le CONTRAT v1 consommé par
FleetPortal : voir contracts/report_v1.schema.json. FleetPortal valide ce
format de manière stricte (aucun champ supplémentaire accepté).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from fleetdiag.core import Finding, Severity

SCHEMA_VERSION = "1.2"


@dataclass(frozen=True)
class ReportEntry:
    code: str
    ecu: str
    system: str
    description: str
    severity: Severity
    status: str  # ex. "0x2F"
    active: bool
    occurrences: int
    last_seen: Optional[str] = None

    @classmethod
    def from_finding(cls, f: Finding) -> "ReportEntry":
        return cls(
            code=f.code,
            ecu=f.ecu,
            system=f.system,
            description=f.description,
            severity=f.severity,
            status=f.status_byte.to_hex(),
            active=f.active,
            occurrences=f.occurrences,
            last_seen=f.last_seen,
        )

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "ecu": self.ecu,
            "system": self.system,
            "description": self.description,
            "severity": self.severity.name,
            "status": self.status,
            "active": self.active,
            "occurrences": self.occurrences,
            "last_seen": self.last_seen,
        }


@dataclass(frozen=True)
class Report:
    vehicle_id: str
    generated_at: str
    entries: List[ReportEntry] = field(default_factory=list)

    @property
    def summary(self) -> Dict[str, object]:
        by_severity = {s.name: 0 for s in Severity}
        for e in self.entries:
            by_severity[e.severity.name] += 1
        return {
            "total": len(self.entries),
            "active": sum(1 for e in self.entries if e.active),
            "critical": sum(1 for e in self.entries if e.severity.is_critical),
            "by_severity": by_severity,
        }

    def to_dict(self) -> dict:
        return {
            "schema_version": SCHEMA_VERSION,
            "vehicle_id": self.vehicle_id,
            "generated_at": self.generated_at,
            "entries": [e.to_dict() for e in self.entries],
            "summary": self.summary,
        }

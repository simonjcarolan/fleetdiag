"""Point d'entrée de l'API publique de fleetdiag.

INTERFACE PUBLIQUE : la signature de `DiagnosticService.build_report` est
figée par contracts/public_api_v1.json (utilisée par FleetPortal et par
l'outil atelier).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, Iterable, Optional

from fleetdiag.auth import Principal
from fleetdiag.core import Catalog, DtcRecord, Finding
from fleetdiag.rules import RuleContext, RuleEngine

from .schemas import Report, ReportEntry


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class DiagnosticService:
    def __init__(
        self,
        catalog: Optional[Catalog] = None,
        engine: Optional[RuleEngine] = None,
        clock: Callable[[], str] = _utc_now,
    ):
        self.catalog = catalog or Catalog.load()
        self.engine = engine or RuleEngine()
        self._clock = clock

    def build_report(
        self,
        records: Iterable[DtcRecord],
        *,
        principal: Optional[Principal] = None,
        vehicle_id: str = "",
    ) -> Report:
        """Construit le rapport de diagnostic d'un véhicule.

        `principal` identifie le client appelant (None pour un appel interne).
        Les règles de traitement peuvent adapter le contenu selon ses scopes.
        """
        findings = []
        for record in records:
            entry = self.catalog.lookup(record.code)
            findings.append(Finding.from_record(record, entry.description, entry.severity))

        ctx = RuleContext(principal=principal, vehicle_id=vehicle_id)
        processed = self.engine.run(findings, ctx)

        return Report(
            vehicle_id=vehicle_id,
            generated_at=self._clock(),
            entries=[ReportEntry.from_finding(f) for f in processed],
        )

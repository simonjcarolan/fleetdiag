"""Fabriques de données de test."""

from __future__ import annotations

import json

from fleetdiag.api import DiagnosticService
from fleetdiag.auth import SCOPE_ENGINEERING, SCOPE_FLEET, SCOPE_WORKSHOP, Principal
from fleetdiag.core import DtcRecord, Finding, Severity
from tests import ROOT

SAMPLE = ROOT / "samples" / "vehicle_VF1-TLS-0042.json"

ENGINEERING = Principal("eng", frozenset({SCOPE_ENGINEERING}))
WORKSHOP = Principal("garage", frozenset({SCOPE_WORKSHOP}))
FLEET = Principal("fleet", frozenset({SCOPE_FLEET}))


def finding(
    code="P0301", ecu="ECM", status=0x2F, occurrences=1, severity=Severity.MAJOR, last_seen=None
) -> Finding:
    return Finding(
        code=code,
        ecu=ecu,
        status=status,
        occurrences=occurrences,
        description=f"desc {code}",
        severity=severity,
        last_seen=last_seen,
    )


def sample_records():
    payload = json.loads(SAMPLE.read_text(encoding="utf-8"))
    return [DtcRecord.from_dict(r) for r in payload["records"]]


def service() -> DiagnosticService:
    return DiagnosticService(clock=lambda: "2026-10-14T08:15:00Z")

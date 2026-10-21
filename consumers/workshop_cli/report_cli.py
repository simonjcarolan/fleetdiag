"""Outil atelier : affiche le rapport de diagnostic d'un véhicule.

Usage :
    python3 consumers/workshop_cli/report_cli.py samples/vehicle_VF1-TLS-0042.json
    python3 consumers/workshop_cli/report_cli.py samples/vehicle_VF1-TLS-0042.json --as workshop
    python3 consumers/workshop_cli/report_cli.py samples/vehicle_VF1-TLS-0042.json --json

`--as` simule le profil du client appelant (aucune clé réelle n'est utilisée).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for extra in (ROOT / "src", ROOT / "libs"):
    if str(extra) not in sys.path:
        sys.path.insert(0, str(extra))

from fleetdiag.api import DiagnosticService  # noqa: E402
from fleetdiag.auth import SCOPE_ENGINEERING, SCOPE_FLEET, SCOPE_WORKSHOP, Principal  # noqa: E402
from fleetdiag.core import DtcRecord  # noqa: E402

PROFILES = {
    "internal": None,
    "engineering": Principal("demo-engineering", frozenset({SCOPE_ENGINEERING})),
    "workshop": Principal("demo-garage", frozenset({SCOPE_WORKSHOP})),
    "fleet": Principal("demo-fleet", frozenset({SCOPE_FLEET})),
}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("input", type=Path, help="fichier JSON de lectures DTC")
    parser.add_argument("--as", dest="profile", choices=sorted(PROFILES), default="internal")
    parser.add_argument("--json", action="store_true", help="sortie JSON (format contractuel)")
    args = parser.parse_args(argv)

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    records = [DtcRecord.from_dict(item) for item in payload["records"]]
    report = DiagnosticService().build_report(
        records, principal=PROFILES[args.profile], vehicle_id=payload["vehicle_id"]
    )

    if args.json:
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
        return 0

    s = report.summary
    print(f"Véhicule {report.vehicle_id} — profil {args.profile}")
    print(f"{s['total']} défaut(s), {s['active']} actif(s), {s['critical']} critique(s)")
    print("-" * 78)
    for e in report.entries:
        flag = "ACTIF " if e.active else "      "
        line = f"{flag}{e.severity.name:<9}{e.code}  {e.ecu:<5} {e.status}  x{e.occurrences:<3}"
        print(f"{line} {e.description}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

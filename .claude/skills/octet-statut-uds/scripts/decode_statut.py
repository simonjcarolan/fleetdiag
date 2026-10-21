"""Décode des octets de statut DTC (ISO 14229-1) avec la bibliothèque vendorisée.

Script de la Skill `octet-statut-uds`. Lecture seule : il n'écrit rien et
n'importe que `libs/dtc_status`. Exemples, depuis la racine du dépôt :

    python3 .claude/skills/octet-statut-uds/scripts/decode_statut.py 0x28 0x2C
    python3 .claude/skills/octet-statut-uds/scripts/decode_statut.py \
        --echantillon samples/vehicle_VF1-TLS-0042.json

Il décrit les bits et les propriétés techniques de `StatusByte`. Il ne qualifie
PAS un défaut au sens métier (intermittent, critique…) : cette définition vient
des tickets et des décisions, pas de la bibliothèque.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[4])
sys.path.insert(0, str(ROOT / "libs"))

from dtc_status import StatusByte  # noqa: E402

AVERTISSEMENT = (
    "Note : description technique (ISO 14229-1). La qualification métier "
    "(intermittent, critique, visible atelier) n'est pas déduite ici."
)


def ligne(value: int, prefixe: str = "") -> str:
    sb = StatusByte(value)
    bits = ", ".join(sb.set_bits()) or "aucun bit"
    return (
        f"{prefixe}{sb.to_hex()}  bits=[{bits}]  "
        f"is_active={sb.is_active()}  has_failure_evidence={sb.has_failure_evidence()}"
    )


def parse(texte: str) -> int:
    value = int(texte, 16) if texte.lower().startswith("0x") else int(texte)
    if not 0 <= value <= 0xFF:
        raise ValueError(f"octet hors bornes : {texte}")
    return value


def main(argv: list[str]) -> int:
    if not argv or argv[0] in {"-h", "--help"}:
        print(__doc__)
        return 0
    if argv[0] == "--echantillon":
        if len(argv) != 2:
            print("usage : --echantillon <fichier.json>", file=sys.stderr)
            return 2
        payload = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
        for rec in payload.get("records", []):
            prefixe = f"{rec['code']:<6} {rec['ecu']:<4} "
            print(ligne(parse(rec["status"]), prefixe))
    else:
        for texte in argv:
            try:
                print(ligne(parse(texte)))
            except ValueError as exc:
                print(f"{texte} : {exc}", file=sys.stderr)
                return 2
    print(AVERTISSEMENT)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

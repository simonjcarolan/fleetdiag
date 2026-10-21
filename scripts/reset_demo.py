"""Remet le dépôt dans l'état initial de la formation (tag `formation-baseline`).

    python3 scripts/reset_demo.py          # affiche ce qui serait perdu
    python3 scripts/reset_demo.py --yes    # réinitialise (DESTRUCTIF)

Conserve .claude/settings.local.json (préférences personnelles).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAG = "formation-baseline"


def git(*args, check=True) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=check, capture_output=True, text=True
    ).stdout


def main(argv) -> int:
    status = git("status", "--porcelain")
    print("Modifications locales :\n" + (status or "  (aucune)"))
    if "--yes" not in argv:
        print(f"\nRelancer avec --yes pour revenir au tag {TAG}.")
        return 0
    git("checkout", "-f", "main")
    git("reset", "--hard", TAG)
    git("clean", "-fd", "-e", ".claude/settings.local.json")
    print(f"Dépôt réinitialisé sur {TAG} : {git('log', '--oneline', '-1').strip()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

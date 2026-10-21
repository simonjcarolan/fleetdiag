"""Initialise le chemin d'import pour `python3 -m unittest` lancé depuis la racine."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for extra in (ROOT / "src", ROOT / "libs", ROOT):
    if str(extra) not in sys.path:
        sys.path.insert(0, str(extra))

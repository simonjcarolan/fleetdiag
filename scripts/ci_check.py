"""Pipeline de contrôle (identique en local et en CI).

    python3 scripts/ci_check.py              # toutes les étapes
    python3 scripts/ci_check.py build tests  # étapes choisies

Étapes : build, tests, critical, deps, lint (lint ignoré si ruff absent).
Code de sortie != 0 si une étape échoue.
"""

from __future__ import annotations

import compileall
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(cmd) -> bool:
    print(f"$ {' '.join(cmd)}", flush=True)
    return subprocess.run(cmd, cwd=ROOT).returncode == 0


def step_build() -> bool:
    ok = True
    for folder in ("src", "libs", "consumers", "scripts", "tests"):
        ok &= compileall.compile_dir(str(ROOT / folder), quiet=1, force=True)
    return bool(ok)


def step_tests() -> bool:
    return _run([sys.executable, "-m", "unittest", "-q"])


def step_critical() -> bool:
    return _run([sys.executable, "-m", "unittest", "discover", "-s", "tests/compat", "-t", "."])


def _declared_dependencies() -> set:
    deps = set()
    for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            deps.add(re.split(r"[<>=!~\[ ;]", line, maxsplit=1)[0].lower())
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r"^dependencies\s*=\s*\[(.*?)\]", pyproject, re.S | re.M)
    if match:
        for item in re.findall(r"['\"]([^'\"]+)['\"]", match.group(1)):
            deps.add(re.split(r"[<>=!~\[ ;]", item, maxsplit=1)[0].lower())
    return deps


def step_deps() -> bool:
    approved = {
        line.strip().lower()
        for line in (ROOT / "contracts" / "approved_dependencies.txt")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip() and not line.startswith("#")
    }
    unapproved = sorted(_declared_dependencies() - approved)
    if unapproved:
        print(f"Dépendances NON approuvées : {unapproved} (validation humaine requise)")
        return False
    print("Dépendances : conformes (aucune dépendance non approuvée).")
    return True


def step_lint() -> bool:
    if shutil.which("ruff") is None:
        print("ruff absent : étape lint ignorée (facultative).")
        return True
    return _run(["ruff", "check", "."])


STEPS = {
    "build": step_build,
    "tests": step_tests,
    "critical": step_critical,
    "deps": step_deps,
    "lint": step_lint,
}


def main(argv) -> int:
    selected = argv or list(STEPS)
    unknown = [s for s in selected if s not in STEPS]
    if unknown:
        print(f"Étapes inconnues : {unknown}. Disponibles : {list(STEPS)}")
        return 2
    results = {}
    for name in selected:
        print(f"\n=== {name} ===", flush=True)
        results[name] = STEPS[name]()
    print("\n=== Résultat ===")
    for name, ok in results.items():
        print(f"  {'OK  ' if ok else 'ÉCHEC'} {name}")
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

"""Calcule l'empreinte de l'interface publique figée.

    python3 scripts/public_api.py            # affiche l'empreinte courante
    python3 scripts/public_api.py --diff     # compare avec contracts/public_api_v1.json

La mise à jour de contracts/public_api_v1.json est une décision humaine
(changement de contrat avec FleetPortal) : ce script ne l'écrit jamais.
"""

from __future__ import annotations

import dataclasses
import inspect
import json
import sys

import _paths  # noqa: F401

from fleetdiag import api, auth

CONTRACT = _paths.ROOT / "contracts" / "public_api_v1.json"


def _sig(func) -> list:
    params = []
    for p in inspect.signature(func).parameters.values():
        default = None if p.default is inspect.Parameter.empty else repr(p.default)
        if callable(p.default) and not isinstance(p.default, type):
            default = "<callable>"
        params.append({"name": p.name, "kind": p.kind.name, "default": default})
    return params


def fingerprint() -> dict:
    return {
        "fleetdiag.api.DiagnosticService.__init__": _sig(api.DiagnosticService.__init__),
        "fleetdiag.api.DiagnosticService.build_report": _sig(api.DiagnosticService.build_report),
        "fleetdiag.api.Report.to_dict": _sig(api.Report.to_dict),
        "fleetdiag.auth.authenticate": _sig(auth.authenticate),
        "fleetdiag.auth.load_keyring_from_env": _sig(auth.load_keyring_from_env),
        "fleetdiag.auth.Principal.fields": [f.name for f in dataclasses.fields(auth.Principal)],
        "fleetdiag.auth.Principal.has_scope": _sig(auth.Principal.has_scope),
        "fleetdiag.auth.scopes": {
            "SCOPE_ENGINEERING": auth.SCOPE_ENGINEERING,
            "SCOPE_WORKSHOP": auth.SCOPE_WORKSHOP,
            "SCOPE_FLEET": auth.SCOPE_FLEET,
        },
        "fleetdiag.auth.__all__": sorted(auth.__all__),
    }


def diff(expected: dict, current: dict) -> list:
    problems = []
    for key in sorted(set(expected) | set(current)):
        if expected.get(key) != current.get(key):
            problems.append(
                f"{key}\n  attendu : {json.dumps(expected.get(key), ensure_ascii=False)}"
                f"\n  obtenu  : {json.dumps(current.get(key), ensure_ascii=False)}"
            )
    return problems


def main(argv) -> int:
    current = fingerprint()
    if "--diff" in argv:
        expected = json.loads(CONTRACT.read_text(encoding="utf-8"))["symbols"]
        problems = diff(expected, current)
        print("\n".join(problems) if problems else "Interface publique conforme au contrat v1.")
        return 1 if problems else 0
    print(json.dumps({"symbols": current}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

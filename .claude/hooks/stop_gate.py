"""Hook Stop : interdit de terminer tant que les tests CRITIQUES échouent.

Déclenché quand Claude s'apprête à rendre la main. S'il y a des modifications
dans le code ou les tests, lance tests/compat (FleetPortal + interface
publique). En cas d'échec : code 2 → Claude reçoit le rapport et doit
continuer (corriger, ou déclarer explicitement l'échec).

Garde-fou anti-boucle : au second arrêt consécutif (`stop_hook_active`), le
hook laisse passer — Claude doit alors avoir signalé l'échec à l'humain.
"""

from __future__ import annotations

import subprocess
import sys

from _common import PROJECT_DIR, audit, read_event

HOOK = "stop_gate"
WATCHED = ["src", "libs", "tests", "consumers", "contracts"]


def has_changes() -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain", "--", *WATCHED],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0 and bool(result.stdout.strip())


def main() -> None:
    event = read_event()
    if event.get("stop_hook_active"):
        audit(HOOK, "PASS_SECOND_STOP", "")
        return
    if not has_changes():
        return

    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests/compat", "-t", "."],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if result.returncode == 0:
        audit(HOOK, "PASS", "tests critiques OK")
        return

    tail = "\n".join((result.stdout + result.stderr).strip().splitlines()[-40:])
    audit(HOOK, "BLOCK", "tests critiques en échec")
    print(
        "ARRÊT REFUSÉ par le hook stop_gate : les tests CRITIQUES (tests/compat) échouent.\n"
        "Règle du projet : un test critique en échec interdit de déclarer la tâche terminée.\n"
        "Corrige la cause, OU indique clairement à l'humain que la tâche N'EST PAS terminée "
        "et pourquoi. Ne modifie pas les tests critiques ni les contrats pour les faire passer.\n\n"
        f"{tail}",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    main()

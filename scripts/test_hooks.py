"""Démonstration déterministe des hooks, SANS lancer Claude Code.

    python3 scripts/test_hooks.py

Envoie aux hooks de .claude/hooks/ des événements simulés (ceux que Claude
Code leur transmettrait) et affiche la décision. Sert de démonstration en
séquence 4/7 et de solution de repli si Claude Code n'est pas disponible.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / ".claude" / "hooks"

CASES = [
    ("protect_paths.py", "Edit", {"file_path": "libs/dtc_status/status.py"}),
    ("protect_paths.py", "Edit", {"file_path": "src/fleetdiag/auth/principal.py"}),
    ("protect_paths.py", "Edit", {"file_path": "requirements.txt"}),
    ("protect_paths.py", "Write", {"file_path": "src/fleetdiag/rules/intermittent.py"}),
    ("protect_paths.py", "Edit", {"file_path": ".claude/hooks/guard_bash.py"}),
    ("protect_paths.py", "Edit", {"file_path": ".claude/skills/revue-diff/SKILL.md"}),
    ("guard_bash.py", "Bash", {"command": "cat config/secrets.env"}),
    (
        "guard_bash.py",
        "Bash",
        {"command": "python3 -c \"print(open('config/secrets.env').read())\""},
    ),
    ("guard_bash.py", "Bash", {"command": "pip install requests"}),
    ("guard_bash.py", "Bash", {"command": "git push origin main"}),
    ("guard_bash.py", "Bash", {"command": "grep -rn FLEETDIAG_KEY ."}),
    ("guard_bash.py", "Bash", {"command": "python3 -m unittest"}),
    # Faux positif instructif : la commande EXCLUT le fichier, mais le mentionne.
    (
        "guard_bash.py",
        "Bash",
        {"command": "git ls-files | grep -v config/secrets.env | xargs wc -l"},
    ),
    # Limite instructive : contournement NON reconnu par les motifs du hook
    # (et la règle permissions.deny Read(...) ne couvre pas Bash) → un hook à
    # motifs n'est pas une frontière de sécurité : voir le sandbox Bash.
    ("guard_bash.py", "Bash", {"command": "cat config/secr*.env"}),
]


def run(hook: str, tool: str, tool_input: dict) -> str:
    event = {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": tool_input}
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(ROOT))
    proc = subprocess.run(
        [sys.executable, str(HOOKS / hook)],
        input=json.dumps(event),
        capture_output=True,
        text=True,
        env=env,
    )
    if proc.returncode == 2:
        return "REFUS   (code 2) " + proc.stderr.strip().splitlines()[0][:110]
    if proc.stdout.strip():
        out = json.loads(proc.stdout)["hookSpecificOutput"]
        return f"{out['permissionDecision'].upper():<7} {out['permissionDecisionReason'][:110]}"
    return "laisse passer"


def stop_gate() -> str:
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(ROOT))
    proc = subprocess.run(
        [sys.executable, str(HOOKS / "stop_gate.py")],
        input=json.dumps({"hook_event_name": "Stop", "stop_hook_active": False}),
        capture_output=True,
        text=True,
        env=env,
    )
    if proc.returncode == 2:
        return "REFUS   (code 2) arrêt refusé : tests critiques en échec"
    return "laisse passer (aucune modification, ou tests critiques OK)"


def main() -> int:
    for hook, tool, tool_input in CASES:
        target = tool_input.get("file_path") or tool_input.get("command")
        print(f"[{hook:<17}] {tool:<5} {target[:58]:<58} → {run(hook, tool, tool_input)}")
    print(f"[{'stop_gate.py':<17}] Stop  {'(fin de tour)':<58} → {stop_gate()}")
    print("\nJournal : .claude/hooks/audit.log")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Utilitaires partagés par les hooks de formation (bibliothèque standard uniquement)."""

from __future__ import annotations

import datetime as _dt
import json
import os
import sys
from fnmatch import fnmatch
from pathlib import Path

PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2])
AUDIT_LOG = PROJECT_DIR / ".claude" / "hooks" / "audit.log"


def read_event() -> dict:
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}


def rel_path(path: str) -> str:
    """Chemin relatif au projet, en notation POSIX (fonctionne aussi sous Windows)."""
    if not path:
        return ""
    p = Path(path)
    if not p.is_absolute():
        p = PROJECT_DIR / p
    try:
        return p.resolve().relative_to(PROJECT_DIR.resolve()).as_posix()
    except ValueError:
        return p.as_posix()  # hors projet : chemin absolu


def matches(path: str, patterns) -> str:
    for pattern in patterns:
        if fnmatch(path, pattern) or path == pattern.rstrip("/*"):
            return pattern
    return ""


def audit(hook: str, decision: str, detail: str) -> None:
    try:
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        stamp = _dt.datetime.now().isoformat(timespec="seconds")
        with AUDIT_LOG.open("a", encoding="utf-8") as fh:
            fh.write(f"{stamp}\t{hook}\t{decision}\t{detail}\n")
    except OSError:
        pass


def block(hook: str, detail: str, message: str) -> None:
    """Refus déterministe : code 2, le message (stderr) est renvoyé à Claude."""
    audit(hook, "DENY", detail)
    print(message, file=sys.stderr)
    sys.exit(2)


def ask(hook: str, detail: str, reason: str) -> None:
    """Demande une validation humaine explicite (boîte de dialogue de permission)."""
    audit(hook, "ASK", detail)
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "ask",
                    "permissionDecisionReason": reason,
                }
            },
            ensure_ascii=False,
        )
    )
    sys.exit(0)

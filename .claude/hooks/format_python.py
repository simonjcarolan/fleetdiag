"""Hook PostToolUse (Edit|Write|MultiEdit) : formate et vérifie les fichiers Python modifiés.

1. `ruff format` si ruff est installé (sinon étape ignorée silencieusement) ;
2. compilation du fichier : en cas d'erreur de syntaxe, code 2 → Claude reçoit
   l'erreur immédiatement (le fichier est déjà écrit, il doit le corriger).
"""

from __future__ import annotations

import py_compile
import shutil
import subprocess
import sys

from _common import PROJECT_DIR, audit, read_event, rel_path

HOOK = "format_python"


def main() -> None:
    event = read_event()
    path = rel_path((event.get("tool_input") or {}).get("file_path", ""))
    if not path.endswith(".py") or path.startswith("/"):
        return  # pas un fichier Python du projet (ex. brouillon hors dépôt)
    target = PROJECT_DIR / path
    if not target.exists():
        return

    ruff = shutil.which("ruff")
    if ruff:
        subprocess.run([ruff, "format", "--quiet", str(target)], cwd=PROJECT_DIR, check=False)
        audit(HOOK, "FORMAT", path)

    try:
        py_compile.compile(str(target), doraise=True)
    except py_compile.PyCompileError as exc:
        audit(HOOK, "SYNTAX_ERROR", path)
        print(f"Erreur de syntaxe dans {path} après modification :\n{exc.msg}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()

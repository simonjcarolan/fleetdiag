"""Hook PreToolUse (Bash) : filtre les commandes shell.

Pourquoi un hook en plus des règles `permissions.deny` ? Une règle
`Read(./config/secrets.env)` bloque l'outil Read, mais pas `cat`, `grep`,
`python -c open(...)`… exécutés via Bash. Ce hook inspecte la commande.
"""

from __future__ import annotations

import re

from _common import ask, block, read_event

HOOK = "guard_bash"

DENY = [
    (r"secrets\.env|(^|[\s/'\"])\.env\b", "accès au fichier de secrets"),
    (r"\bgit\s+push\b", "publication vers le dépôt distant"),
    (r"\bgit\s+(reset\s+--hard|clean\s+-[a-z]*f)", "opération git destructive"),
    (r"\brm\s+-[a-z]*r[a-z]*f|\brm\s+-[a-z]*f[a-z]*r", "suppression récursive"),
    (
        r"(^|[;&|]\s*)(printenv|env)\s*($|[;&|])",
        "affichage de toutes les variables d'environnement",
    ),
    (r"\bsudo\b|\bchmod\s+777\b", "élévation de droits"),
]

ASK = [
    (r"\b(pip|pip3|uv|poetry|npm|pnpm|yarn)\s+(install|add)\b", "installation de paquet"),
    (r"\b(curl|wget|Invoke-WebRequest)\b", "accès réseau externe"),
    (r"\bgit\s+(commit|checkout|switch|rebase|merge|stash)\b", "modification de l'historique git"),
    (
        r"\b(grep|rg|ag)\b[^|]*\s-[a-zA-Z]*[rR]",
        "recherche récursive pouvant traverser config/ (préférer l'outil Grep, filtré par les "
        "règles de permission)",
    ),
]


def main() -> None:
    event = read_event()
    command = (event.get("tool_input") or {}).get("command", "")
    if not command:
        return
    for pattern, reason in DENY:
        if re.search(pattern, command, re.IGNORECASE):
            block(
                HOOK,
                command,
                f"BLOQUÉ par le hook guard_bash ({reason}). Commande refusée : {command!r}. "
                "Ne cherche pas de variante : explique à l'humain ce dont tu as besoin.",
            )
    for pattern, reason in ASK:
        if re.search(pattern, command, re.IGNORECASE):
            ask(HOOK, command, f"Validation humaine requise ({reason}) : {command}")


if __name__ == "__main__":
    main()

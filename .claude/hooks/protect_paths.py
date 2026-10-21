"""Hook PreToolUse (Edit|Write|MultiEdit|NotebookEdit) : protège les fichiers sensibles.

- REFUS (code 2)       : fichiers que l'agent ne doit jamais modifier.
- VALIDATION HUMAINE   : fichiers modifiables seulement après accord explicite.

Contrôle déterministe : il s'applique quoi que dise le prompt ou le modèle.
"""

from __future__ import annotations

from _common import ask, block, matches, read_event, rel_path

HOOK = "protect_paths"

DENY = {
    "libs/dtc_status/*": "bibliothèque vendorisée (équipe Plateforme) : corriger en amont, pas ici",
    "config/secrets.env": "fichier de secrets",
    ".github/workflows/*": "pipeline de contrôle : modification réservée aux mainteneurs",
    ".claude/hooks/*": "un agent ne modifie pas ses propres garde-fous",
    ".claude/settings.json": "configuration partagée de l'équipe",
}

ASK = {
    "src/fleetdiag/auth/*": "module partagé avec FleetPortal (interface figée, FD-120)",
    "tests/compat/*": "tests CRITIQUES de compatibilité : les modifier change le contrat vérifié",
    "requirements*.txt": "ajout ou modification de dépendance",
    "pyproject.toml": "dépendances / configuration du projet",
    "CLAUDE.md": "instructions permanentes de l'agent : changement proposé, validé par un humain",
    ".claude/rules/*": "instructions de l'agent (règles ciblées)",
    ".claude/skills/*": "procédures de l'agent (Skills)",
    ".claude/agents/*": "définition des sous-agents (outils, permissions)",
}


def main() -> None:
    event = read_event()
    tool_input = event.get("tool_input") or {}
    path = rel_path(tool_input.get("file_path") or tool_input.get("notebook_path") or "")
    if not path:
        return

    pattern = matches(path, DENY)
    if pattern:
        block(
            HOOK,
            path,
            f"BLOQUÉ par le hook protect_paths : « {path} » est protégé ({DENY[pattern]}). "
            "Ne contourne pas ce blocage (pas de copie, pas de Bash). Si la modification te "
            "semble nécessaire, arrête-toi et explique pourquoi à l'humain.",
        )

    pattern = matches(path, ASK)
    if pattern:
        ask(HOOK, path, f"Validation humaine requise : {path} — {ASK[pattern]}.")


if __name__ == "__main__":
    main()

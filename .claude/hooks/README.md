# Hooks du dépôt fleetdiag

Les hooks sont la partie **déterministe** du harnais : du code qui s'exécute à
des moments précis de la boucle de Claude Code, quoi que dise le prompt ou le
modèle. Ils sont déclarés dans `.claude/settings.json` (clé `hooks`) et
visibles en session avec `/hooks`.

Démonstration sans modèle : `python3 scripts/test_hooks.py`.

## Les quatre hooks

| Événement | Matcher | Script | Rôle | Décision possible |
|---|---|---|---|---|
| `PreToolUse` | `Edit\|Write\|MultiEdit\|NotebookEdit` | `protect_paths.py` | Fichiers interdits ou soumis à validation | refus (code 2) ou `ask` |
| `PreToolUse` | `Bash` | `guard_bash.py` | Commandes shell dangereuses ou sensibles | refus (code 2) ou `ask` |
| `PostToolUse` | `Edit\|Write\|MultiEdit` | `format_python.py` | Reformate le `.py` modifié (si `ruff` est installé) et le compile | code 2 si erreur de syntaxe : l'erreur est renvoyée à Claude, mais le fichier est déjà écrit |
| `Stop` | — | `stop_gate.py` | Refuse la fin du tour si les tests critiques échouent | refus de s'arrêter (code 2) |

`_common.py` regroupe la lecture de l'événement, le journal et les deux façons
de décider (`block`, `ask`).

## Contrat d'un hook `command`

**Entrée** : un objet JSON sur l'entrée standard. Champs communs (extrait) :
`session_id`, `transcript_path`, `cwd`, `permission_mode`, `hook_event_name`.
Les événements d'outil ajoutent `tool_name`, `tool_input`, `tool_use_id`.

```json
{"hook_event_name": "PreToolUse", "tool_name": "Bash",
 "tool_input": {"command": "cat config/secrets.env"}, "cwd": "/…/fleetdiag"}
```

**Sortie** : le code de retour, et éventuellement du JSON sur la sortie standard.

| Code | Effet |
|---|---|
| `0` | Succès. Si la sortie standard est un objet JSON unique, il est interprété. |
| `2` | Erreur **bloquante** sur les événements qui peuvent bloquer. Le texte de la sortie d'erreur est renvoyé comme raison. `PreToolUse` : l'appel d'outil est annulé. `Stop` : Claude ne s'arrête pas et continue. `PostToolUse` : le texte est montré à Claude, mais l'outil a déjà agi. |
| autre (dont `1`) | Erreur **non bloquante** : l'action continue, l'utilisateur voit une erreur de hook. Un hook qui plante ne protège donc rien. |

**Demander une validation humaine** (`ask`, utilisé par `_common.ask`) : code 0
et ce JSON. Les autres valeurs possibles sont `allow`, `deny` et `defer`.

```json
{"hookSpecificOutput": {"hookEventName": "PreToolUse",
  "permissionDecision": "ask", "permissionDecisionReason": "…"}}
```

## Choix de conception (et pourquoi)

- **Refus par code 2 plutôt que `deny` en JSON** : plus simple à écrire et à
  tester ; le message d'erreur explique à Claude ce qu'il doit faire à la place
  (« Ne cherche pas de variante : explique à l'humain ce dont tu as besoin »).
  Sans cette phrase, le modèle a tendance à essayer une autre commande.
- **Anti-boucle du `Stop`** : l'événement contient `stop_hook_active`, vrai si
  Claude continue déjà à cause d'un hook Stop. Au second arrêt, `stop_gate`
  laisse passer : sinon un test impossible à corriger bloquerait la session.
  Contrepartie : l'humain doit **lire** la réponse, qui doit dire « non terminé ».
- **`stop_gate` ne lance que `tests/compat`** et seulement s'il y a des
  modifications : un hook lent ralentit chaque fin de tour (timeout 150 s).
- **Journal** `.claude/hooks/audit.log` (ignoré par git) : chaque décision est
  tracée, ce qui permet de rejouer ce qu'il s'est passé après coup.
- **Un agent ne modifie pas ses propres garde-fous** : `protect_paths` refuse
  toute édition de `.claude/hooks/` et de `.claude/settings.json`, et demande
  une validation pour `CLAUDE.md`, `.claude/rules/`, `.claude/skills/`,
  `.claude/agents/`.

## Limites connues (laissées volontairement)

- `guard_bash` repose sur des motifs : `cat config/secr*.env` passe. La règle
  `permissions.deny` `Read(./config/secrets.env)` ne couvre que l'outil Read,
  pas une commande shell. **Un hook à motifs n'est pas une frontière de
  sécurité** : pour une vraie isolation, il faut un bac à sable (sandbox) ou
  ne pas avoir le fichier sur le poste.
- Faux positif : `git ls-files | grep -v config/secrets.env` est refusé parce
  qu'il **mentionne** le fichier.
- Les hooks utilisent `python3`. Sous Windows, si seul `python` existe, le hook
  sort en erreur non bloquante : la protection disparaît sans bruit. Vérifier
  avec `python3 scripts/test_hooks.py` avant toute séance.

## Autres événements (non utilisés ici)

Exemples d'usages possibles pour ce dépôt, à évaluer :

| Événement | Usage possible |
|---|---|
| `SessionStart` (matcher `compact`) | Réinjecter un rappel (`additionalContext`) après une compaction |
| `UserPromptSubmit` | Ajouter du contexte à chaque demande, ou bloquer une demande |
| `PostToolUseFailure` | Tracer les échecs d'outils |
| `SubagentStop` | Exiger un format de sortie avant qu'un sous-agent rende la main |
| `InstructionsLoaded` | Tracer quels fichiers d'instructions ont été chargés |

Référence : documentation Claude Code, page « Hooks ».

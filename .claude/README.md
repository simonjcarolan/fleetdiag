# Le harnais de fleetdiag

Le **harnais** (*agentic harness*) est la couche qui entoure le modèle : elle
lui fournit ses outils et décide de ce qu'il voit dans son contexte. Claude
Code est un harnais ; ce dossier `.claude/` (avec `CLAUDE.md` et `.mcp.json`)
est la **configuration de ce harnais pour ce dépôt**.

Ne pas confondre avec un *test harness* (banc de test) : ici, il s'agit de
l'environnement de travail de l'agent, pas de l'exécution des tests.

## Où chaque élément agit dans la boucle

```
 demande ─▶ [ contexte ] ─▶ modèle ─▶ appel d'outil ─▶ [ permissions ] ─▶ [ PreToolUse ] ─▶ outil
              ▲                ▲                                                          │
              │                │                                     [ PostToolUse ] ◀────┘
   CLAUDE.md, rules,      sous-agents                                       │
   descriptions de        (contexte séparé,              résultat ──────────┘──▶ modèle ─▶ … ─▶ fin du tour
   Skills, MCP            outils restreints)                                                  │
                                                                                     [ Stop ] ◀┘
```

| Élément | Fichier | Quand il agit | Coût en contexte | Nature | Garantit | Ne garantit pas |
|---|---|---|---|---|---|---|
| Instructions permanentes | `CLAUDE.md` | Chargé en entier à chaque session, rechargé après `/compact` | Permanent | Probabiliste (le modèle lit) | Que le modèle **connaît** la règle | Qu'il la respecte |
| Règles ciblées | `.claude/rules/*.md` (`paths:`) | Quand un fichier correspondant est lu ou modifié | À la demande | Probabiliste | Contexte pertinent au bon moment | Qu'elles soient chargées si aucun fichier ne correspond |
| Skill manuelle | `skills/context-brief`, `revue-diff`, `compte-rendu` | Seulement sur `/nom` (`disable-model-invocation: true`) | Nul avant l'appel ; le corps reste ensuite dans la conversation | Probabiliste | Une procédure identique à chaque appel | Que le résultat soit juste |
| Skill automatique | `skills/octet-statut-uds` | Quand la description correspond à la tâche, ou sur `/octet-statut-uds` | Description permanente ; corps et `reference.md` à la demande | Probabiliste | Connaissance disponible sans y penser | Qu'elle se déclenche (dépend de la description) |
| Sous-agent | `agents/explorateur.md`, `agents/relecteur.md` | Sur délégation (`Utilise le sous-agent…`, `@agent-…`, ou `context: fork` d'une Skill) | Fenêtre séparée ; seul le résumé revient | **Outils : déterministe.** Raisonnement : probabiliste | L'explorateur **ne peut pas** écrire ; le relecteur non plus | La qualité de l'exploration ou de la revue |
| Permissions | `settings.json` → `permissions` | À chaque appel d'outil | Nul | Déterministe | `deny` bloque l'outil visé ; `allow` évite les questions | Qu'une autre voie (Bash) ne contourne pas un `deny` sur Read |
| Hooks | `settings.json` → `hooks`, `hooks/*.py` | Avant/après un outil, en fin de tour | Nul, sauf les messages renvoyés | Déterministe | Refus et validations, quoi que dise le prompt | Plus que ce que leurs motifs reconnaissent |
| Serveur MCP | `.mcp.json` → `tools/jira_mock_mcp` | Quand Claude appelle un outil `mcp__jira__*` | Noms d'outils seulement, définitions chargées à la demande | Déterministe sur ce qui **existe** | Aucune écriture possible : il n'y a pas d'outil d'écriture | Que le contenu des tickets soit fiable (injection) |
| Point d'arrêt humain | Mode plan, validations `ask` | Quand le workflow l'impose | — | Humain | Une décision prise par la bonne personne | Rien si l'humain valide sans lire |

## Les trois questions à se poser pour chaque règle

1. **Doit-elle tenir quoi qu'il arrive ?** Oui → permission ou hook (déterministe),
   en plus de l'instruction. Non → instruction ou Skill suffit.
2. **Vaut-elle pour toutes les tâches ?** Oui → `CLAUDE.md`. Pour une partie du
   code → `.claude/rules/` avec `paths:`. Pour une procédure → Skill.
3. **Pollue-t-elle le contexte principal ?** Oui (exploration large, revue,
   logs) → sous-agent, qui ne renvoie qu'un résumé.

## Inspecter le harnais en session

| Commande | Ce qu'elle montre |
|---|---|
| `/context` | Ce qui occupe la fenêtre de contexte, dont les fichiers d'instructions chargés |
| `/memory` | Les fichiers `CLAUDE.md` pris en compte, et la mémoire automatique |
| `/hooks` | Les hooks actifs, leur source et leur commande |
| `/agents` | Les sous-agents disponibles |
| `/mcp` | Les serveurs MCP, leur état et leurs outils |
| `/permissions` | Les règles allow / ask / deny actives |
| `.claude/hooks/audit.log` | Chaque décision des hooks de ce dépôt |
| `~/.claude/projects/<projet>/*.jsonl` | Le transcript complet d'une session (messages, appels d'outils, résultats) |

## Le harnais appliqué au ticket FD-142

| Étape de la boucle | Éléments du harnais qui interviennent |
|---|---|
| Understand | `CLAUDE.md` ; `/context-brief` (Skill en lecture seule, Jira via MCP) |
| Explore | Mode plan ; sous-agent `explorateur` (sans Edit/Write) ; règles ciblées chargées à la lecture des fichiers ; `octet-statut-uds` si les statuts sont étudiés |
| Plan | Mode plan ; point d'arrêt humain |
| Implement | Permissions ; `protect_paths` (refus `libs/`, validation `auth/`, `tests/compat/`) ; `guard_bash` ; `format_python` |
| Test | Commandes autorisées dans `allow` ; hook `stop_gate` |
| Review | `/revue-diff` → sous-agent `relecteur` (contexte neuf, Skill `octet-statut-uds` préchargée) |
| Accept | `/compte-rendu` ; décision humaine |

## Confiance du dossier

Les règles `allow` de `settings.json` ne s'appliquent qu'après avoir accepté la
confiance du dossier au premier lancement. Sans elle, Claude demande une
autorisation pour chaque commande de test.

Détail des hooks : `hooks/README.md`.

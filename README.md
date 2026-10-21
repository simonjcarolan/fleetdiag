# fleetdiag — dépôt fil rouge « Claude Code avancé »

API interne (fictive) qui consolide les défauts de diagnostic véhicule — codes
DTC SAE J2012 et octet de statut UDS ISO 14229-1 — en un rapport consommé par
**FleetPortal** (produit client) et par l'**outil atelier**.

> Dépôt de formation : domaine, clients, tickets et secrets sont fictifs.

## Démarrage (2 minutes)

Prérequis : Python ≥ 3.9 et git. **Aucune installation de paquet requise.**
`ruff` est facultatif (formatage automatique par hook s'il est présent).

```bash
python3 scripts/ci_check.py          # build + tests + tests critiques + dépendances (+ lint)
claude                               # depuis la RACINE du dépôt
```

Au premier lancement, Claude Code demande :
1. de faire confiance au dossier → accepter ;
2. d'approuver le serveur MCP `jira` (déclaré dans `.mcp.json`) → accepter.

Vérifier ensuite avec `/mcp` (serveur `jira` connecté), `/agents` et `/hooks`.

> **Windows** : si `python3` n'existe pas, remplacer `python3` par `python`
> (ou `py`) dans `.claude/settings.json` et `.mcp.json`.

## Commandes

| Besoin | Commande |
|---|---|
| Tous les tests | `python3 -m unittest` |
| Tests **critiques** (FleetPortal + interface publique) | `python3 -m unittest discover -s tests/compat -t .` |
| Pipeline complet (= CI) | `python3 scripts/ci_check.py` |
| Écart d'interface publique | `python3 scripts/public_api.py --diff` |
| Rapport de démo, profil atelier | `python3 consumers/workshop_cli/report_cli.py samples/vehicle_VF1-TLS-0042.json --as workshop` |
| Revenir à l'état initial | `python3 scripts/reset_demo.py --yes` |

## Organisation

```
CLAUDE.md                     règles stables du projet (lues à chaque session)
.claude/
  settings.json               permissions + hooks (partagés)
  agents/explorateur.md       sous-agent lecture seule (code + Jira)
  agents/relecteur.md         sous-agent de revue, ne modifie jamais le code
  skills/context-brief/       /context-brief FD-142
  skills/revue-diff/          /revue-diff FD-142 (exécutée par le relecteur)
  skills/compte-rendu/        /compte-rendu FD-142
  hooks/                      contrôles déterministes (fichiers protégés, shell, format, arrêt)
.mcp.json                     serveur MCP « jira » simulé, LECTURE SEULE
src/fleetdiag/                api (public) · rules · auth (partagé) · core
libs/dtc_status/              dépendance partagée vendorisée (ne pas modifier)
consumers/                    outil atelier + bouchon FleetPortal
contracts/                    contrats publics (ne pas modifier)
config/                       settings.ini (lisible) · secrets.env (INTERDIT)
docs/                         documentation (à prendre avec recul…)
tickets/FD-142.md             copie hors ligne du ticket de l'atelier
samples/                      lectures DTC d'un véhicule de démonstration
tests/ · tests/compat/        tests unitaires · tests critiques
```

## Mission de l'atelier

Ticket **FD-142** (`tickets/FD-142.md`, ou via Jira : « lis FD-142 avec
l'outil jira »). Lisez-le d'un œil critique : il est volontairement ambigu.

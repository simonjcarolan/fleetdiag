---
paths:
  - "src/fleetdiag/rules/**"
  - "tests/test_rules_*.py"
---

# Règles de traitement (`src/fleetdiag/rules/`)

Chargé automatiquement quand un fichier de règles ou de tests de règles est lu
ou modifié. Complète `CLAUDE.md` et la recette de `docs/ARCHITECTURE.md`.

- Contrat d'une règle : un attribut `name` unique en snake_case et une méthode
  `apply(findings, ctx) -> list` (voir `rules/base.py`). La règle renvoie une
  **nouvelle** liste : ne jamais muter `findings` ni un `Finding` reçu.
- `ctx.principal` peut être `None` (appel interne) : toute règle qui dépend du
  profil appelant doit traiter ce cas explicitement, et un test doit le couvrir.
- Le profil de l'appelant se lit avec l'API existante de `fleetdiag.auth`.
  `auth` est partagé avec FleetPortal : n'y ajoute rien sans validation humaine.
- Position dans `engine.DEFAULT_RULES` : fusion des doublons, puis filtres,
  puis tri. Un filtre placé avant la fusion travaille sur des statuts partiels
  et donne un résultat faux sans qu'aucun test existant n'échoue.
- Un prédicat sur l'octet de statut s'écrit côté `fleetdiag`, à partir des
  propriétés de `StatusByte` (bibliothèque vendorisée, non modifiable). Le sens
  **métier** d'un prédicat (« intermittent », « critique »…) vient d'une source
  citée (ticket, décision), jamais du nom d'une méthode existante.
- Tests attendus pour une nouvelle règle : cas nominal, cas limite par bit de
  statut concerné, `principal=None`, pureté (liste d'entrée inchangée), et un
  test de position dans `DEFAULT_RULES` si l'ordre a un effet.

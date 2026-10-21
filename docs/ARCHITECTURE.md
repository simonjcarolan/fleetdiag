# Architecture

```
                 ┌──────────────────────────┐
  FleetPortal ──▶│  fleetdiag.api (public)  │◀── outil atelier (consumers/workshop_cli)
  (produit client)│  DiagnosticService       │
        │        └────────────┬─────────────┘
        │                     │ Finding (interne)
        │        ┌────────────▼─────────────┐
        │        │  fleetdiag.rules          │  RuleEngine + DEFAULT_RULES (ordre significatif)
        │        └────────────┬─────────────┘
        │        ┌────────────▼─────────────┐
        └───────▶│  fleetdiag.auth (partagé) │  Principal, scopes — interface figée
                 └────────────┬─────────────┘
                 ┌────────────▼─────────────┐
                 │  fleetdiag.core           │  DtcRecord, Finding, Severity, Catalog
                 └────────────┬─────────────┘
                 ┌────────────▼─────────────┐
                 │  libs/dtc_status (vendor) │  StatusByte ISO 14229-1 — ne pas modifier
                 └──────────────────────────┘
```

## Responsabilités

| Module | Rôle | Modifiable dans un ticket fonctionnel ? |
|---|---|---|
| `src/fleetdiag/api` | Façade publique, construction du `Report` | Implémentation oui, **signatures non** |
| `src/fleetdiag/rules` | Règles de traitement (filtrage, fusion, tri) | Oui |
| `src/fleetdiag/auth` | Identification des clients (partagé avec FleetPortal) | **Non sans validation** |
| `src/fleetdiag/core` | Modèles et catalogue | Oui, avec prudence (utilisé partout) |
| `libs/dtc_status` | Décodage de l'octet de statut UDS (vendorisé) | **Non** |
| `contracts/` | Contrats consommateurs | **Non** (décision d'architecture) |

## Ajouter une règle de traitement

1. Créer `src/fleetdiag/rules/<nom>.py` avec une classe exposant `name` et
   `apply(findings, ctx)` (voir `rules/base.py`). Une règle est **pure**.
2. L'enregistrer dans `DEFAULT_RULES` (`rules/engine.py`) **à la bonne
   position** : après la fusion des doublons, avant le tri.
3. L'exporter dans `rules/__init__.py`.
4. Ajouter `tests/test_rules_<nom>.py` + un test de bout en bout dans
   `tests/test_service.py`.
5. Vérifier les tests critiques `tests/compat/`.

Le profil de l'appelant est disponible dans `ctx.principal` (peut être `None`
pour un appel interne).

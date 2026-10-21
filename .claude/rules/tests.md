---
paths:
  - "tests/**"
---

# Tests

- Framework : `unittest` uniquement (pas de pytest : dépendance non approuvée).
- Données : fabriques de `tests/factories.py` (`finding(...)`, `sample_records()`,
  `service()`, profils `ENGINEERING` / `WORKSHOP` / `FLEET`). Ne pas recréer
  d'objets à la main quand une fabrique existe.
- `tests/compat/` = tests **critiques** (contrat FleetPortal, interface
  publique). On ne les modifie jamais pour faire passer un changement : un
  échec y signifie que le changement casse un consommateur.
- Un test existant qui échoue après ton changement se qualifie avant toute
  modification : régression, test obsolète (intention à conserver), problème
  d'environnement. Un test obsolète ne s'adapte qu'après accord humain.
- Les tests marqués `skip` ou `TODO` existants appartiennent à d'autres tickets :
  les signaler, ne pas les traiter hors périmètre.
- Nom des tests : `test_<comportement_attendu>` en anglais, docstring en français
  si le cas métier n'est pas évident.

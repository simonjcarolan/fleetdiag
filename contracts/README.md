# Contrats publics

Ce répertoire décrit ce que les produits consommateurs (FleetPortal, outil
atelier) considèrent comme stable. **Il ne se modifie pas dans le cadre d'un
ticket fonctionnel** : une évolution de contrat passe par une décision
d'architecture et l'accord des équipes consommatrices.

| Fichier | Rôle |
|---|---|
| `public_api_v1.json` | Signatures Python figées (`build_report`, `authenticate`, `Principal`…) |
| `report_v1.schema.json` | Format JSON du rapport, validé strictement par FleetPortal |
| `approved_dependencies.txt` | Dépendances d'exécution autorisées |

Vérification : `python3 -m unittest discover -s tests/compat -t .` (tests **critiques**).

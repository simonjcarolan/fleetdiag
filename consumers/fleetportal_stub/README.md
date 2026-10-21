# FleetPortal (bouchon)

FleetPortal est le produit client qui consomme le rapport `fleetdiag` et
réutilise le module `fleetdiag.auth`. Ce répertoire n'en contient qu'un
bouchon : le validateur strict du format v1, utilisé par les tests de
compatibilité (`tests/compat/`).

Point d'attention historique (FD-120) : FleetPortal **rejette** tout rapport
contenant un champ non déclaré dans `contracts/report_v1.schema.json`.

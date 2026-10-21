# dtc_status — bibliothèque vendorisée

- Source : dépôt `platform-libs`, équipe Plateforme
- Version : 2.4.1
- Utilisée aussi par : FleetPortal, outil de flash atelier

**Ne pas modifier ce répertoire dans `fleetdiag`.** Une correction doit être
proposée en amont (merge request sur `platform-libs`), puis resynchronisée
avec `scripts/sync_vendored.sh` (hors périmètre de ce dépôt de formation).

Si une fonction manque (par exemple un prédicat métier), il faut l'implémenter
côté `fleetdiag` en s'appuyant sur les propriétés existantes de `StatusByte`.

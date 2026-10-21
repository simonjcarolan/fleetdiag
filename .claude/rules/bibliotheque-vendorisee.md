---
paths:
  - "libs/dtc_status/**"
---

# Bibliothèque vendorisée `libs/dtc_status`

Copie d'une bibliothèque de l'équipe Plateforme (`platform-libs`), utilisée
aussi par FleetPortal et l'outil de flash atelier (voir `VENDORED.md`).

- Lecture seule : une modification ici serait écrasée à la prochaine
  synchronisation et divergerait des autres consommateurs. Le hook
  `protect_paths` refuse d'ailleurs toute édition de ce répertoire.
- Si une fonction manque, l'écrire côté `fleetdiag` à partir des propriétés
  existantes de `StatusByte`, et le signaler comme candidate à une remontée
  en amont.
- Les noms de méthodes reflètent le vocabulaire de la plateforme, pas
  forcément celui du métier : lire la docstring avant de réutiliser une méthode
  pour une définition métier.
- Pour décoder un octet de statut : Skill `octet-statut-uds`.

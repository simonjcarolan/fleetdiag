# Exemple de Context Brief rempli — FD-118

> Exemple de **niveau de détail attendu**, sur un autre ticket. Ne pas en
> recopier le contenu : seule la forme sert de modèle (sources citées,
> établi / supposé séparés, questions prêtes à envoyer).

# Context Brief — FD-118

## Objectif (résultat observable attendu)
Trois cas aujourd'hui non testés sont couverts par des tests unitaires qui
échoueraient si le comportement changeait. [établi : Jira FD-118, description]

## Périmètre
- Inclus : `tests/test_rules_dedupe.py`, `tests/test_rules_cleared.py`.
- Exclu explicitement : code de production (`src/`), tests critiques
  `tests/compat/`. [supposé : le ticket parle seulement de tests — à confirmer]

## Composants probablement concernés (fichier — raison — modifiable ?)
- `src/fleetdiag/rules/dedupe.py` — clé de fusion `(code, ecu)`, `last_seen` max — non (lecture)
- `src/fleetdiag/rules/cleared.py` — filtre `has_failure_evidence()` — non (lecture)
- `tests/test_rules_dedupe.py:30-31` — deux `TODO(FD-118)` — oui
- `tests/test_rules_cleared.py:17` — test `skip` FD-118 (statut 0x50) — oui

## Contraintes
- Règles permanentes (CLAUDE.md, contrats) : `unittest`, fabriques de
  `tests/factories.py`, changements minimaux.
- Spécifiques à la tâche : aucun changement de comportement attendu.

## Éléments à explorer
- `libs/dtc_status/status.py` : quels bits comptent comme preuve de défaut
  (pour vérifier l'attendu du cas 0x50).

## Éléments à NE PAS charger dans le contexte (et pourquoi)
- `api/`, `auth/`, `consumers/` : hors périmètre d'un ticket de tests de règles.
- `config/secrets.env` : interdit et inutile.

## Critères d'acceptation (reformulés pour être vérifiables)
1. Même code sur deux ECU différents → deux défauts distincts après fusion.
2. `last_seen` absent sur les deux lectures → fusion sans erreur, `last_seen` vaut `None`.
3. Statut `0x50` seul → défaut supprimé par `DropClearedRule` ; le `skip` est retiré.
4. `python3 -m unittest` et les tests critiques passent.

## Vérifications possibles (commandes, tests)
- `python3 -m unittest tests.test_rules_dedupe tests.test_rules_cleared -v`
- `python3 -m unittest discover -s tests/compat -t .`

## Informations manquantes / ambiguïtés
- Cas 3 : le comportement actuel (suppression) est-il le comportement **voulu**,
  ou seulement le comportement constaté ? [supposé : voulu]

## Conditions imposant une question au demandeur (questions prêtes à envoyer)
- « Pour un DTC au statut 0x50 (tests non terminés, aucun échec), confirmez-vous
  qu'il doit disparaître du rapport pour tous les profils ? »

Points à valider par un humain avant planification :
1. Périmètre limité aux tests (aucun changement de code de production).
2. Comportement attendu pour le statut 0x50.

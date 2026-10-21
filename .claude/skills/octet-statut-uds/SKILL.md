---
name: octet-statut-uds
description: Décode un octet de statut DTC UDS (ISO 14229-1) bit par bit avec la bibliothèque vendorisée dtc_status, sans en tirer de qualification métier. À utiliser dès qu'il faut lire, comparer ou tester des valeurs de statut comme 0x28, 0x2C ou 0xA8.
when_to_use: Quand une tâche, un test ou un échantillon manipule le champ status d'un DtcRecord ou d'un Finding, ou cite testFailed, pendingDTC, confirmedDTC, warningIndicatorRequested.
argument-hint: "[octet(s) ex. 0x28 0x2C | --echantillon samples/<fichier>.json]"
allowed-tools: Read, Grep, Glob, Bash(python3 .claude/skills/octet-statut-uds/scripts/decode_statut.py *)
---

# Octet de statut DTC (UDS, ISO 14229-1)

Octets à décoder : $ARGUMENTS
(si la liste est vide, prends les valeurs de statut citées dans la tâche en cours).

## Méthode

1. Décode avec le script, jamais de tête : une erreur de bit inverse un résultat
   sans qu'aucun test ne le signale.
   `python3 .claude/skills/octet-statut-uds/scripts/decode_statut.py <octets>`
   ou `... decode_statut.py --echantillon <fichier.json>` pour tout un véhicule.
2. Cite les bits par leur nom ISO (`confirmedDTC`, bit 3) et par la propriété
   `StatusByte` correspondante. Table complète et pièges : [reference.md](reference.md).
3. Pour un défaut présent plusieurs fois (même code, même ECU), raisonne sur
   les statuts **après** fusion par `MergeDuplicatesRule` (OU binaire), pas sur
   chaque lecture isolée.

## Limite à respecter

Ce décodage est **technique**. Les termes métier (« intermittent », « critique »,
« visible atelier ») ont une définition décidée ailleurs : cite le ticket ou la
décision qui la donne. Si tu ne la trouves pas, écris « définition métier non
trouvée » et pose la question, au lieu de la déduire d'un nom de méthode
(`is_historical()` décrit la vue de la plateforme, pas forcément celle du métier).

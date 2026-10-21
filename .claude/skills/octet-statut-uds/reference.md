# Référence : octet de statut DTC (ISO 14229-1, tableau D.13)

Chargé seulement quand la Skill `octet-statut-uds` y renvoie. Source de vérité
dans le code : `libs/dtc_status/status.py` (bibliothèque vendorisée).

## Les 8 bits

| Bit | Masque | Nom ISO | Propriété / constante `dtc_status` | Lecture |
|---|---|---|---|---|
| 0 | `0x01` | testFailed | `StatusByte.test_failed`, `is_active()` | Le test échoue au moment de la lecture |
| 1 | `0x02` | testFailedThisOperationCycle | `TEST_FAILED_THIS_OPERATION_CYCLE` | Échec pendant le cycle de fonctionnement en cours |
| 2 | `0x04` | pendingDTC | `StatusByte.pending` | Échec sur le cycle courant ou précédent, pas encore confirmé |
| 3 | `0x08` | confirmedDTC | `StatusByte.confirmed` | Défaut confirmé selon les critères de maturation de l'ECU |
| 4 | `0x10` | testNotCompletedSinceLastClear | `TEST_NOT_COMPLETED_SINCE_LAST_CLEAR` | Test pas encore exécuté jusqu'au bout depuis l'effacement |
| 5 | `0x20` | testFailedSinceLastClear | `StatusByte.failed_since_last_clear` | Au moins un échec depuis le dernier effacement |
| 6 | `0x40` | testNotCompletedThisOperationCycle | `TEST_NOT_COMPLETED_THIS_OPERATION_CYCLE` | Test pas terminé sur le cycle en cours |
| 7 | `0x80` | warningIndicatorRequested | `StatusByte.warning_indicator` | L'ECU demande l'allumage du voyant |

Prédicats techniques de `StatusByte` :
- `is_active()` = bit 0.
- `has_failure_evidence()` = au moins un des bits 0, 1, 2, 3, 5. Les bits 4 et 6
  disent seulement qu'un test n'a pas été terminé : ce n'est pas une preuve de défaut.
- `is_historical()` = bit 5 et pas bit 0. **Vocabulaire plateforme** : la docstring
  précise que ce n'est pas nécessairement la définition métier d'« intermittent ».

## Valeurs de l'échantillon `samples/vehicle_VF1-TLS-0042.json`

Produit par `decode_statut.py --echantillon` (décodage technique uniquement) :

| Statut | Bits à 1 | Remarque technique |
|---|---|---|
| `0x2F` | 0, 1, 2, 3, 5 | actif |
| `0x28` | 3, 5 | confirmé, non actif |
| `0x24` | 2, 5 | pending, **non confirmé**, non actif |
| `0x2C` | 2, 3, 5 | pending et confirmé, non actif |
| `0x09` | 0, 3 | actif et confirmé |
| `0x01` | 0 | actif, non confirmé |
| `0xA8` | 3, 5, 7 | confirmé, non actif, **voyant demandé** |
| `0x50` | 4, 6 | aucune preuve de défaut (tests non terminés) |

Fusion de doublons : `MergeDuplicatesRule` cumule les bits (OU binaire).
Exemple générique : `0x24 | 0x01 = 0x25` → bits 0, 2, 5 : une lecture non active
et une lecture active donnent un défaut actif une fois fusionnées.

## Pièges fréquents

- Confondre « confirmé » (bit 3) et « actif » (bit 0) : un défaut peut être
  confirmé sans être présent au moment de la lecture.
- Tester un prédicat sur une seule lecture alors que le moteur fusionne d'abord
  les doublons : le résultat dépend de la **position** de la règle.
- Écrire les masques en décimal dans les tests : utiliser l'hexadécimal
  (`0x28`), comme les outils de diagnostic et l'échantillon.
- Oublier `0x00` (aucun bit) et `0x50` (bits 4 et 6 seuls) dans les cas limites.

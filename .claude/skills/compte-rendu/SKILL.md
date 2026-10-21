---
name: compte-rendu
description: Produit la synthèse finale d'une tâche, exploitable par un développeur qui n'a pas suivi la session (ce qui a changé, pourquoi, preuves, limites).
argument-hint: "[clé-ticket]"
disable-model-invocation: true
---

Rédige le compte rendu de la tâche $ARGUMENTS pour un développeur qui reprend
le sujet sans avoir suivi la session. Pas d'historique d'exploration, pas de
narration : des faits vérifiables.

État du dépôt au moment de l'appel :

```!
git status --short
git diff --stat
```

Avant d'écrire, relance les vérifications et utilise leurs résultats réels :
`python3 -m unittest`, `python3 -m unittest discover -s tests/compat -t .`,
`python3 scripts/public_api.py --diff`.

Gabarit (une page maximum) :

```
# Compte rendu — $ARGUMENTS

## Résultat en une phrase
## Décisions prises (et par qui : agent / humain) — avec la source
## Changements
| Fichier | Nature | Raison (critère traité) |
## Preuves
| Critère d'acceptation | Preuve (test / commande) | Résultat |
## Tests modifiés ou supprimés (justification, validation)
## Non vérifié / risques résiduels
## Suites proposées (tickets à créer, docs à mettre à jour)
```

Si un test critique échoue : le titre devient « TÂCHE NON TERMINÉE » et la
cause est placée en tête.

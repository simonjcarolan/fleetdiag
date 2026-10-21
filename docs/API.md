# API fleetdiag — guide d'intégration

> Dernière mise à jour : mars 2025 (v1.1)

## Construire un rapport

```python
from fleetdiag.api import DiagnosticService

service = DiagnosticService()
report = service.build_report(records, include_history=False)
print(report.to_dict())
```

- `records` : itérable de `DtcRecord` (code SAE J2012, octet de statut, ECU).
- `include_history` : si `False` (défaut), les défauts historiques sont exclus
  du rapport.

## Format du rapport

Chaque entrée contient : `code`, `ecu`, `description`, `severity`, `status`,
`active`, `occurrences`.

### Sévérité

La sévérité est un niveau de 1 à 3 :

| Niveau | Signification |
|---|---|
| 1 | Information |
| 2 | Mineur |
| 3 | **Critique** — intervention immédiate |

Le résumé (`summary`) indique le nombre total de défauts et le nombre de
défauts critiques (niveau 3).

## Glossaire

- **Actif** : le bit `testFailed` (bit 0) est positionné.
- **Intermittent** : DTC en statut *pending* (bit 2) non encore confirmé
  (bit 3 à 0).
- **Historique** : défaut ayant échoué depuis le dernier effacement mais plus
  actif.

## Authentification

Les clients s'authentifient avec une clé d'API. Pour tester localement, les
clés de démonstration sont dans `config/secrets.env`.

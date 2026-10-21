# Changelog

## 1.3.2 — 2026-09-18
- Catalogue DTC 2026.09 (ajout U0121, U0155).

## 1.3.0 — 2026-05-06
- **Nouvelle échelle de sévérité à 4 niveaux** : ajout de `CRITICAL` (4) pour
  les défauts sécurité (freinage, airbag). `MAJOR` (3) n'est plus critique.
- Le résumé `summary.critical` compte désormais uniquement `CRITICAL`.
- Schéma de rapport 1.2 : ajout de `system`, `last_seen`, `summary.active`,
  `summary.by_severity` (validé avec FleetPortal, FD-120).

## 1.2.0 — 2025-11-03
- Suppression du paramètre `include_history` de `build_report` (jamais utilisé
  par FleetPortal). Les défauts historiques sont toujours inclus.
- FD-101 : correction — les ateliers voyaient moins de codes que l'ingénierie.

## 1.1.0 — 2025-03-12
- Authentification par clé d'API et scopes.

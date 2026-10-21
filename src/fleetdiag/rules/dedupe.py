"""Fusion des défauts identiques remontés plusieurs fois par le même ECU."""

from __future__ import annotations

from typing import Dict, List, Tuple

from fleetdiag.core import Finding

from .base import RuleContext


class MergeDuplicatesRule:
    name = "merge_duplicates"

    def apply(self, findings: List[Finding], ctx: RuleContext) -> List[Finding]:
        merged: Dict[Tuple[str, str], Finding] = {}
        for finding in findings:
            key = (finding.code, finding.ecu)
            previous = merged.get(key)
            if previous is None:
                merged[key] = finding
                continue
            merged[key] = previous.with_(
                # Les bits de statut sont cumulés : si une des lectures est active,
                # le défaut fusionné est actif.
                status=previous.status | finding.status,
                occurrences=previous.occurrences + finding.occurrences,
                last_seen=max(
                    (d for d in (previous.last_seen, finding.last_seen) if d), default=None
                ),
            )
        return list(merged.values())

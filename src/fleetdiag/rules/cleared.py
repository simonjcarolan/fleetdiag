"""Suppression des DTC sans aucune trace de défaut (effacés ou jamais testés)."""

from __future__ import annotations

from typing import List

from fleetdiag.core import Finding

from .base import RuleContext


class DropClearedRule:
    name = "drop_cleared"

    def apply(self, findings: List[Finding], ctx: RuleContext) -> List[Finding]:
        return [f for f in findings if f.status_byte.has_failure_evidence()]

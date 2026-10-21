"""Tri final : sévérité décroissante, puis défauts actifs, puis code."""

from __future__ import annotations

from typing import List

from fleetdiag.core import Finding

from .base import RuleContext


class SortBySeverityRule:
    name = "sort_by_severity"

    def apply(self, findings: List[Finding], ctx: RuleContext) -> List[Finding]:
        return sorted(findings, key=lambda f: (-int(f.severity), not f.active, f.code, f.ecu))

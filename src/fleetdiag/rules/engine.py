"""Moteur d'application des règles."""

from __future__ import annotations

import logging
from typing import List, Optional, Sequence

from fleetdiag.core import Finding

from .base import Rule, RuleContext
from .cleared import DropClearedRule
from .dedupe import MergeDuplicatesRule
from .ordering import SortBySeverityRule

log = logging.getLogger(__name__)

# L'ordre compte :
# 1. fusion des doublons (cumule les bits de statut) ;
# 2. filtres (travaillent sur les statuts fusionnés) ;
# 3. tri (toujours en dernier).
DEFAULT_RULES: Sequence[Rule] = (
    MergeDuplicatesRule(),
    DropClearedRule(),
    SortBySeverityRule(),
)


class RuleEngine:
    def __init__(self, rules: Optional[Sequence[Rule]] = None):
        self.rules = tuple(DEFAULT_RULES if rules is None else rules)
        names = [r.name for r in self.rules]
        if len(names) != len(set(names)):
            raise ValueError(f"noms de règles dupliqués : {names}")

    def run(self, findings: List[Finding], ctx: RuleContext) -> List[Finding]:
        current = list(findings)
        for rule in self.rules:
            before = len(current)
            current = rule.apply(current, ctx)
            log.debug("règle %s : %d -> %d défauts", rule.name, before, len(current))
        return current

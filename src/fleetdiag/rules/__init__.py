"""Règles de traitement appliquées aux défauts avant production du rapport."""

from .base import Rule, RuleContext
from .cleared import DropClearedRule
from .dedupe import MergeDuplicatesRule
from .engine import DEFAULT_RULES, RuleEngine
from .ordering import SortBySeverityRule

__all__ = [
    "DEFAULT_RULES",
    "DropClearedRule",
    "MergeDuplicatesRule",
    "Rule",
    "RuleContext",
    "RuleEngine",
    "SortBySeverityRule",
]

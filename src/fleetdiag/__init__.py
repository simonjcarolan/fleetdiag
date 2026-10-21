"""fleetdiag — API interne de consolidation des défauts de diagnostic véhicule.

Dépôt de FORMATION (Claude Code avancé). Domaine, données et clients fictifs.
"""

from .api import DiagnosticService, Report
from .core import DtcRecord, Severity

__all__ = ["DiagnosticService", "DtcRecord", "Report", "Severity"]
__version__ = "1.3.2"

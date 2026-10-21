"""API publique de fleetdiag (interface figée — voir contracts/)."""

from .schemas import SCHEMA_VERSION, Report, ReportEntry
from .service import DiagnosticService

__all__ = ["SCHEMA_VERSION", "DiagnosticService", "Report", "ReportEntry"]

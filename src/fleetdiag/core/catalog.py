"""Catalogue des DTC connus : libellé et sévérité par code."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from .dtc import normalize_code
from .severity import Severity

_DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "dtc_catalog.json"

UNKNOWN_DESCRIPTION = "Code non référencé dans le catalogue"
UNKNOWN_SEVERITY = Severity.MINOR


@dataclass(frozen=True)
class CatalogEntry:
    description: str
    severity: Severity


class Catalog:
    def __init__(self, entries: Dict[str, CatalogEntry]):
        self._entries = {normalize_code(code): entry for code, entry in entries.items()}

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "Catalog":
        raw = json.loads(Path(path or _DEFAULT_PATH).read_text(encoding="utf-8"))
        return cls(
            {
                code: CatalogEntry(item["description"], Severity.parse(item["severity"]))
                for code, item in raw["codes"].items()
            }
        )

    def lookup(self, code: str) -> CatalogEntry:
        return self._entries.get(
            normalize_code(code), CatalogEntry(UNKNOWN_DESCRIPTION, UNKNOWN_SEVERITY)
        )

    def __len__(self) -> int:
        return len(self._entries)

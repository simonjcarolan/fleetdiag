"""Bouchon du validateur FleetPortal (produit client).

Reproduit le comportement réel de FleetPortal : validation STRICTE du rapport
contre contracts/report_v1.schema.json. Tout champ non déclaré est rejeté.
Sous-ensemble JSON Schema suffisant pour le contrat : type, enum, required,
properties, additionalProperties, items.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "contracts" / "report_v1.schema.json"

_TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "integer": int,
    "boolean": bool,
    "null": type(None),
}


def _type_ok(value: Any, expected) -> bool:
    names = expected if isinstance(expected, list) else [expected]
    for name in names:
        py = _TYPES[name]
        if name == "integer" and isinstance(value, bool):
            continue
        if isinstance(value, py):
            return True
    return False


def _validate(value: Any, schema: dict, path: str, errors: List[str]) -> None:
    if "type" in schema and not _type_ok(value, schema["type"]):
        errors.append(f"{path}: type attendu {schema['type']}, reçu {type(value).__name__}")
        return
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: valeur {value!r} hors énumération {schema['enum']}")
    if isinstance(value, dict):
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: champ requis manquant '{key}'")
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in props:
                    errors.append(f"{path}: champ non déclaré '{key}' (rejeté par FleetPortal)")
        for key, sub in props.items():
            if key in value:
                _validate(value[key], sub, f"{path}.{key}", errors)
    if isinstance(value, list) and "items" in schema:
        for i, item in enumerate(value):
            _validate(item, schema["items"], f"{path}[{i}]", errors)


def validate_report(report: dict, schema_path: Path = SCHEMA_PATH) -> List[str]:
    """Retourne la liste des violations (vide si le rapport est accepté)."""
    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    errors: List[str] = []
    _validate(report, schema, "$", errors)
    return errors

"""Échelle de sévérité des défauts.

Historique : l'échelle comptait 3 niveaux jusqu'à la v1.2 (3 = critique).
Le niveau CRITICAL (4) a été ajouté en v1.3 pour isoler les défauts liés à la
sécurité (freinage, airbag) ; MAJOR (3) n'est donc plus « critique ».
"""

from __future__ import annotations

from enum import IntEnum


class Severity(IntEnum):
    INFO = 1
    MINOR = 2
    MAJOR = 3
    CRITICAL = 4

    @classmethod
    def parse(cls, value: str | int) -> "Severity":
        if isinstance(value, int):
            return cls(value)
        try:
            return cls[value.strip().upper()]
        except KeyError as exc:
            raise ValueError(f"sévérité inconnue : {value!r}") from exc

    @property
    def is_critical(self) -> bool:
        return self >= Severity.CRITICAL

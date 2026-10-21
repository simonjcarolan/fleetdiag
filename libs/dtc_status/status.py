"""Octet de statut DTC selon ISO 14229-1 (UDS), annexe D.

BIBLIOTHÈQUE VENDORISÉE depuis le dépôt `platform-libs` (équipe Plateforme).
Toute modification doit être faite en amont puis resynchronisée.
"""

from __future__ import annotations

from dataclasses import dataclass

# Masques de bits (ISO 14229-1, tableau D.13)
TEST_FAILED = 0x01
TEST_FAILED_THIS_OPERATION_CYCLE = 0x02
PENDING_DTC = 0x04
CONFIRMED_DTC = 0x08
TEST_NOT_COMPLETED_SINCE_LAST_CLEAR = 0x10
TEST_FAILED_SINCE_LAST_CLEAR = 0x20
TEST_NOT_COMPLETED_THIS_OPERATION_CYCLE = 0x40
WARNING_INDICATOR_REQUESTED = 0x80

_BIT_NAMES = {
    TEST_FAILED: "testFailed",
    TEST_FAILED_THIS_OPERATION_CYCLE: "testFailedThisOperationCycle",
    PENDING_DTC: "pendingDTC",
    CONFIRMED_DTC: "confirmedDTC",
    TEST_NOT_COMPLETED_SINCE_LAST_CLEAR: "testNotCompletedSinceLastClear",
    TEST_FAILED_SINCE_LAST_CLEAR: "testFailedSinceLastClear",
    TEST_NOT_COMPLETED_THIS_OPERATION_CYCLE: "testNotCompletedThisOperationCycle",
    WARNING_INDICATOR_REQUESTED: "warningIndicatorRequested",
}

# Bits qui indiquent qu'un défaut a réellement été observé.
_FAILURE_EVIDENCE = (
    TEST_FAILED
    | TEST_FAILED_THIS_OPERATION_CYCLE
    | PENDING_DTC
    | CONFIRMED_DTC
    | TEST_FAILED_SINCE_LAST_CLEAR
)


@dataclass(frozen=True)
class StatusByte:
    """Vue en lecture seule d'un octet de statut DTC."""

    value: int

    def __post_init__(self) -> None:
        if not 0 <= self.value <= 0xFF:
            raise ValueError(f"octet de statut hors bornes : {self.value!r}")

    def _bit(self, mask: int) -> bool:
        return bool(self.value & mask)

    @property
    def test_failed(self) -> bool:
        return self._bit(TEST_FAILED)

    @property
    def pending(self) -> bool:
        return self._bit(PENDING_DTC)

    @property
    def confirmed(self) -> bool:
        return self._bit(CONFIRMED_DTC)

    @property
    def failed_since_last_clear(self) -> bool:
        return self._bit(TEST_FAILED_SINCE_LAST_CLEAR)

    @property
    def warning_indicator(self) -> bool:
        return self._bit(WARNING_INDICATOR_REQUESTED)

    def is_active(self) -> bool:
        """Le défaut est présent au moment de la lecture."""
        return self.test_failed

    def has_failure_evidence(self) -> bool:
        """Au moins un bit atteste qu'un défaut a été observé."""
        return bool(self.value & _FAILURE_EVIDENCE)

    def is_historical(self) -> bool:
        """Défaut observé depuis le dernier effacement mais plus actif.

        Attention : « historique » au sens de la plateforme, ce qui n'est pas
        nécessairement la définition métier d'un défaut « intermittent ».
        """
        return self.failed_since_last_clear and not self.test_failed

    def set_bits(self) -> list[str]:
        return [name for mask, name in _BIT_NAMES.items() if self.value & mask]

    def to_hex(self) -> str:
        return f"0x{self.value:02X}"


def describe(value: int) -> str:
    """Représentation lisible, ex. ``0x2C [pendingDTC, confirmedDTC, ...]``."""
    sb = StatusByte(value)
    return f"{sb.to_hex()} [{', '.join(sb.set_bits()) or 'aucun bit'}]"

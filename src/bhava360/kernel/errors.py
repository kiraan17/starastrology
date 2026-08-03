from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class KernelErrorCode(str, Enum):
    INVALID_DATETIME = "INVALID_DATETIME"
    INVALID_TIMEZONE = "INVALID_TIMEZONE"
    INVALID_LOCATION = "INVALID_LOCATION"
    UNSUPPORTED_PLANET = "UNSUPPORTED_PLANET"
    UNSUPPORTED_CONFIG = "UNSUPPORTED_CONFIG"
    EPHEMERIS_UNAVAILABLE = "EPHEMERIS_UNAVAILABLE"
    CALCULATION_FAILED = "CALCULATION_FAILED"
    LICENSE_GATE_BLOCKED = "LICENSE_GATE_BLOCKED"
    CORPUS_GATE_BLOCKED = "CORPUS_GATE_BLOCKED"


@dataclass(slots=True)
class KernelError(Exception):
    code: KernelErrorCode
    message: str
    details: dict[str, Any] | None = None

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.code.value}: {self.message}"

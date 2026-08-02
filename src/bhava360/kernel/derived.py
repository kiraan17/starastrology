from __future__ import annotations

from bhava360.kernel.models import NAKSHATRAS_VEDASTRO, SIGNS


NAKSHATRA_SPAN = 360.0 / 27.0  # 13°20'
PADA_SPAN = NAKSHATRA_SPAN / 4.0  # 3°20'


def normalize_longitude(lon: float) -> float:
    return lon % 360.0


def sign_from_longitude(lon: float) -> tuple[str, float]:
    lon = normalize_longitude(lon)
    idx = int(lon // 30.0)
    return SIGNS[idx], lon - idx * 30.0


def nakshatra_from_longitude(lon: float) -> tuple[str, int, str]:
    lon = normalize_longitude(lon)
    idx = int(lon // NAKSHATRA_SPAN) % 27
    within = lon - idx * NAKSHATRA_SPAN
    pada = int(within // PADA_SPAN) + 1
    name = NAKSHATRAS_VEDASTRO[idx]
    return name, pada, f"{name} - {pada}"

"""Tithi Pravesh helpers (TEC-079) — Candidate."""

from __future__ import annotations

from typing import Any

import swisseph as swe

from bhava360.kernel.derived import normalize_longitude
from bhava360.kernel.errors import KernelError, KernelErrorCode
from bhava360.timing.panchanga import compute_tithi

TITHI_PRAVESH_VARIANT = "tithi_pravesh_candidate_v1"


def moon_sun_elongation(jd_ut: float, sidereal_flags: int) -> float:
    moon, _ = swe.calc_ut(jd_ut, swe.MOON, sidereal_flags)
    sun, _ = swe.calc_ut(jd_ut, swe.SUN, sidereal_flags)
    return normalize_longitude(float(moon[0]) - float(sun[0]))


def _lon_delta(a: float, b: float) -> float:
    return (a - b + 180.0) % 360.0 - 180.0


def natal_tithi_from_longitudes(*, sun_lon: float, moon_lon: float) -> dict[str, Any]:
    return compute_tithi(sun_lon, moon_lon)


def find_tithi_pravesh_jd(
    *,
    natal_elongation_deg: float,
    center_jd_ut: float,
    sidereal_flags: int,
    window_days: float = 20.0,
    step_hours: float = 6.0,
) -> float:
    """
    Find JD when Moon−Sun elongation returns to natal value nearest ``center_jd_ut``.

    Candidate annual rule: choose the elongation return closest to the solar-return
    (or anniversary) instant within ±window_days.
    """
    target = normalize_longitude(natal_elongation_deg)
    step = step_hours / 24.0
    start = center_jd_ut - window_days
    end = center_jd_ut + window_days

    jd = start
    prev_jd = jd
    prev_delta = _lon_delta(moon_sun_elongation(jd, sidereal_flags), target)
    brackets: list[tuple[float, float]] = []

    while jd <= end:
        jd += step
        cur = _lon_delta(moon_sun_elongation(jd, sidereal_flags), target)
        if prev_delta < 0 <= cur:
            brackets.append((prev_jd, jd))
        prev_jd, prev_delta = jd, cur

    if not brackets:
        raise KernelError(
            KernelErrorCode.CALCULATION_FAILED,
            "tithi pravesh not found in search window",
            {
                "center_jd_ut": center_jd_ut,
                "window_days": window_days,
                "natal_elongation": target,
            },
        )

    refined: list[float] = []
    for lo, hi in brackets:
        a, b = lo, hi
        for _ in range(40):
            mid = (a + b) / 2.0
            d = _lon_delta(moon_sun_elongation(mid, sidereal_flags), target)
            if d < 0:
                a = mid
            else:
                b = mid
        refined.append((a + b) / 2.0)

    return min(refined, key=lambda x: abs(x - center_jd_ut))


__all__ = [
    "TITHI_PRAVESH_VARIANT",
    "find_tithi_pravesh_jd",
    "moon_sun_elongation",
    "natal_tithi_from_longitudes",
]

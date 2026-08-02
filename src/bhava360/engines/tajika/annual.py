"""Annual / Tajika helpers: solar return and Muntha (P17a)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import swisseph as swe

from bhava360.chart.dignity import sign_lord
from bhava360.kernel.derived import normalize_longitude, sign_from_longitude
from bhava360.kernel.errors import KernelError, KernelErrorCode
from bhava360.kernel.models import SIGNS
from bhava360.kernel.timeutil import julian_day_to_utc

ANNUAL_VARIANT = "tajika_thin_candidate_v1"
LOCATION_RULES = ("birth_place", "residence", "event_location")


def _sun_sidereal_lon(jd_ut: float, sidereal_flags: int) -> float:
    xx, _ret = swe.calc_ut(jd_ut, swe.SUN, sidereal_flags)
    return float(xx[0]) % 360.0


def _lon_delta(a: float, b: float) -> float:
    """Signed shortest delta a-b in (-180, 180]."""
    return (a - b + 180.0) % 360.0 - 180.0


def find_solar_return_jd(
    *,
    natal_sun_longitude_sidereal: float,
    search_start_jd: float,
    sidereal_flags: int,
    search_days: float = 400.0,
) -> float:
    """
    Find next JD (UT) when sidereal Sun returns to natal longitude after search_start_jd.

    Uses coarse scan + bisection. Candidate thin-slice (Moshier/Lahiri path).
    """
    target = normalize_longitude(natal_sun_longitude_sidereal)
    step = 1.0  # day
    jd = search_start_jd + 0.5
    end = search_start_jd + search_days
    prev_jd = jd
    prev_delta = _lon_delta(_sun_sidereal_lon(jd, sidereal_flags), target)

    found_bracket = None
    while jd <= end:
        jd += step
        cur = _lon_delta(_sun_sidereal_lon(jd, sidereal_flags), target)
        # Crossing from negative to positive (Sun catching up to target from behind)
        if prev_delta < 0 <= cur or prev_delta > 0 >= cur and abs(prev_delta) + abs(cur) < 20:
            # Prefer crossing through zero with small span
            if prev_delta < 0 <= cur:
                found_bracket = (prev_jd, jd)
                break
        prev_jd, prev_delta = jd, cur

    if found_bracket is None:
        raise KernelError(
            KernelErrorCode.CALCULATION_FAILED,
            "solar return not found in search window",
            {
                "search_start_jd": search_start_jd,
                "search_days": search_days,
                "natal_sun": target,
            },
        )

    lo, hi = found_bracket
    for _ in range(48):
        mid = (lo + hi) / 2.0
        d = _lon_delta(_sun_sidereal_lon(mid, sidereal_flags), target)
        if d < 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def compute_muntha(
    *,
    natal_lagna_sign: str,
    completed_years: int,
) -> dict[str, Any]:
    """Muntha advances one sign per completed year from natal Lagna."""
    if completed_years < 0:
        raise KernelError(
            KernelErrorCode.UNSUPPORTED_CONFIG,
            "completed_years must be >= 0",
            {"completed_years": completed_years},
        )
    base = SIGNS.index(natal_lagna_sign)
    idx = (base + completed_years) % 12
    sign = SIGNS[idx]
    lord = sign_lord(sign)
    return {
        "sign": sign,
        "sign_index": idx,
        "completed_years": completed_years,
        "lord": lord.value if lord else None,
        "notes": [
            "Muntha = natal Lagna sign + completed_years (mod 12).",
            "Muntha lord is a year-lord *candidate* only — full Tajika Varshesh deferred.",
        ],
    }


def completed_years_at(birth_utc: datetime, at_utc: datetime) -> int:
    """Whole years completed between birth and instant (UTC)."""
    if birth_utc.tzinfo is None:
        birth_utc = birth_utc.replace(tzinfo=timezone.utc)
    if at_utc.tzinfo is None:
        at_utc = at_utc.replace(tzinfo=timezone.utc)
    years = at_utc.year - birth_utc.year
    try:
        anniversary = birth_utc.replace(year=at_utc.year)
    except ValueError:
        anniversary = birth_utc.replace(year=at_utc.year, month=3, day=1)
    if at_utc < anniversary:
        years -= 1
    return max(0, years)


def resolve_annual_location(
    *,
    location_rule: str,
    natal_lat: float,
    natal_lon: float,
    residence_lat: float | None = None,
    residence_lon: float | None = None,
    event_lat: float | None = None,
    event_lon: float | None = None,
) -> dict[str, Any]:
    rule = location_rule.strip()
    if rule not in LOCATION_RULES:
        raise KernelError(
            KernelErrorCode.UNSUPPORTED_CONFIG,
            "annual.location_rule must be birth_place|residence|event_location",
            {"location_rule": location_rule},
        )
    if rule == "birth_place":
        return {"location_rule": rule, "latitude": natal_lat, "longitude": natal_lon}
    if rule == "residence":
        if residence_lat is None or residence_lon is None:
            raise KernelError(
                KernelErrorCode.INVALID_LOCATION,
                "residence coordinates required for annual.location_rule=residence",
            )
        return {"location_rule": rule, "latitude": residence_lat, "longitude": residence_lon}
    if event_lat is None or event_lon is None:
        raise KernelError(
            KernelErrorCode.INVALID_LOCATION,
            "event coordinates required for annual.location_rule=event_location",
        )
    return {"location_rule": rule, "latitude": event_lat, "longitude": event_lon}

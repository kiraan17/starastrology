"""Tajika Sahams (Arabic parts style) — Candidate thin slice (TEC-078)."""

from __future__ import annotations

from typing import Any

from bhava360.chart.dignity import sign_lord
from bhava360.kernel.derived import (
    house_index_for_longitude,
    normalize_longitude,
    sign_from_longitude,
    whole_sign_cusp_longitudes,
)

SAHAM_VARIANT = "tajika_saham_candidate_v1"

# Point ids used in formulas (must exist in lon map or be "Asc").
Point = str


def saham_longitude(*, asc: float, plus: float, minus: float) -> float:
    """Classic Saham: Ascendant + A − B (mod 360)."""
    return normalize_longitude(asc + plus - minus)


def is_day_chart(
    *,
    local_iso: str,
    sunrise_local: str,
    sunset_local: str,
) -> bool:
    """True when civil local time is within sunrise–sunset (inclusive of sunrise)."""
    return sunrise_local <= local_iso <= sunset_local


def _lon_map(planets: list[dict[str, Any]], asc: float) -> dict[str, float]:
    out = {"Asc": float(asc)}
    for p in planets:
        out[str(p["planet"])] = float(p["longitude_sidereal_deg"])
    return out


def _resolve(lons: dict[str, float], key: Point) -> float:
    if key not in lons:
        raise KeyError(key)
    return lons[key]


# Candidate formula table. Day: Asc + A − B; night_reverse=True swaps A/B at night.
# Sources: SRC-012 still Candidate — these are provisional computational defaults.
SAHAM_DEFS: tuple[dict[str, Any], ...] = (
    {
        "id": "punya",
        "name": "Punya",
        "plus_day": "Moon",
        "minus_day": "Sun",
        "night_reverse": True,
        "notes": "Part of Fortune analogue; day Asc+Moon−Sun, night Asc+Sun−Moon.",
    },
    {
        "id": "vidya",
        "name": "Vidya",
        "plus_day": "Jupiter",
        "minus_day": "Moon",
        "night_reverse": True,
        "notes": "Knowledge/learning Saham Candidate formula.",
    },
    {
        "id": "yasya",
        "name": "Yasya",
        "plus_day": "Jupiter",
        "minus_day": "Sun",
        "night_reverse": True,
        "notes": "Fame/reputation Saham Candidate formula.",
    },
    {
        "id": "mitra",
        "name": "Mitra",
        "plus_day": "Jupiter",
        "minus_day": "Venus",
        "night_reverse": True,
        "notes": "Friends/allies Saham Candidate formula.",
    },
    {
        "id": "rajya",
        "name": "Rajya",
        "plus_day": "Mars",
        "minus_day": "Saturn",
        "night_reverse": True,
        "notes": "Status/authority Saham Candidate formula.",
    },
)


def compute_sahams(
    *,
    ascendant_longitude: float,
    planets: list[dict[str, Any]],
    is_day: bool,
) -> dict[str, Any]:
    """
    Compute Candidate Saham longitudes for the Varsha (or natal) chart.

    Requires Sun/Moon/Mars/Jupiter/Venus/Saturn among planets.
    """
    lons = _lon_map(planets, ascendant_longitude)
    required = {"Sun", "Moon", "Mars", "Jupiter", "Venus", "Saturn"}
    missing = sorted(required - set(lons))
    if missing:
        return {
            "variant": SAHAM_VARIANT,
            "is_day": is_day,
            "error": f"missing planets for Sahams: {missing}",
            "sahams": [],
        }

    cusps = whole_sign_cusp_longitudes(ascendant_longitude)
    rows: list[dict[str, Any]] = []
    for defn in SAHAM_DEFS:
        plus_key = defn["plus_day"]
        minus_key = defn["minus_day"]
        if not is_day and defn["night_reverse"]:
            plus_key, minus_key = minus_key, plus_key
        lon = saham_longitude(
            asc=ascendant_longitude,
            plus=_resolve(lons, plus_key),
            minus=_resolve(lons, minus_key),
        )
        sign, sign_deg = sign_from_longitude(lon)
        lord = sign_lord(sign)
        house = house_index_for_longitude(lon, cusps)
        rows.append(
            {
                "id": defn["id"],
                "name": defn["name"],
                "longitude_sidereal_deg": lon,
                "sign": sign,
                "sign_degree": sign_deg,
                "sign_lord": lord.value if lord else None,
                "house": house,
                "formula": {
                    "expression": f"Asc + {plus_key} - {minus_key}",
                    "is_day": is_day,
                    "night_reverse_applied": (not is_day) and bool(defn["night_reverse"]),
                },
                "notes": defn["notes"],
            }
        )

    return {
        "variant": SAHAM_VARIANT,
        "status": "Candidate",
        "is_day": is_day,
        "source_note": "SRC-012 edition citation pending; formulas are Candidate defaults.",
        "sahams": rows,
    }


__all__ = [
    "SAHAM_DEFS",
    "SAHAM_VARIANT",
    "compute_sahams",
    "is_day_chart",
    "saham_longitude",
]

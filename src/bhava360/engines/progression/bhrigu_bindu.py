"""Bhrigu Bindu primitives — Candidate (TEC-081)."""

from __future__ import annotations

from typing import Any

from bhava360.kernel.derived import (
    house_index_for_longitude,
    nakshatra_from_longitude,
    normalize_longitude,
    sign_from_longitude,
    whole_sign_cusp_longitudes,
)

BHRIGU_BINDU_VARIANT = "bhrigu_bindu_candidate_v1"
DEFAULT_CONJUNCTION_ORB_DEG = 1.0


def circular_midpoint(lon_a: float, lon_b: float) -> float:
    """Midpoint along the shorter arc from A to B."""
    a = normalize_longitude(lon_a)
    diff = (normalize_longitude(lon_b) - a + 180.0) % 360.0 - 180.0
    return normalize_longitude(a + diff / 2.0)


def compute_bhrigu_bindu(
    *,
    moon_longitude: float,
    rahu_longitude: float,
    lagna_longitude: float | None = None,
    conjunction_orb_deg: float = DEFAULT_CONJUNCTION_ORB_DEG,
    planet_longitudes: dict[str, float] | None = None,
) -> dict[str, Any]:
    """
    Bhrigu Bindu = shorter-arc midpoint of Moon and Rahu (Candidate).

    Optionally lists natal planets within ``conjunction_orb_deg`` of the bindu.
    """
    lon = circular_midpoint(moon_longitude, rahu_longitude)
    sign, sign_deg = sign_from_longitude(lon)
    nak, pada, nak_label = nakshatra_from_longitude(lon)

    house = None
    if lagna_longitude is not None:
        cusps = whole_sign_cusp_longitudes(lagna_longitude)
        house = house_index_for_longitude(lon, cusps)

    arc = abs((normalize_longitude(rahu_longitude) - normalize_longitude(moon_longitude) + 180.0) % 360.0 - 180.0)

    natal_hits: list[dict[str, Any]] = []
    if planet_longitudes:
        orb = float(conjunction_orb_deg)
        for name, plon in planet_longitudes.items():
            if name in {"Moon", "Rahu"}:
                # Still report if tightly on BB, but skip defining bodies optionally?
                # Include all planets including Moon/Rahu for transparency.
                pass
            sep = abs((normalize_longitude(plon) - lon + 180.0) % 360.0 - 180.0)
            if sep <= orb:
                natal_hits.append(
                    {
                        "planet": name,
                        "longitude_sidereal_deg": float(plon),
                        "separation_deg": round(sep, 6),
                        "orb_deg": orb,
                    }
                )
        natal_hits.sort(key=lambda r: r["separation_deg"])

    return {
        "variant": BHRIGU_BINDU_VARIANT,
        "longitude_sidereal_deg": lon,
        "sign": sign,
        "sign_degree": sign_deg,
        "nakshatra": nak,
        "pada": pada,
        "nakshatra_label": nak_label,
        "house_from_lagna": house,
        "moon_rahu_arc_deg": round(arc, 6),
        "formula": {
            "expression": "shorter_arc_midpoint(Moon, Rahu)",
            "moon_longitude_sidereal_deg": float(moon_longitude),
            "rahu_longitude_sidereal_deg": float(rahu_longitude),
        },
        "natal_conjunctions": natal_hits,
        "notes": [
            "Candidate midpoint rule: shorter arc between Moon and Rahu.",
            "Transit trigger scan is separate (see transit_hits_on_bindu).",
        ],
    }


def transit_hits_on_bindu(
    *,
    bindu_longitude: float,
    transit_longitudes: dict[str, float],
    orb_deg: float = DEFAULT_CONJUNCTION_ORB_DEG,
) -> list[dict[str, Any]]:
    """Planets whose transit longitude lies within orb of Bhrigu Bindu."""
    hits: list[dict[str, Any]] = []
    orb = float(orb_deg)
    bb = normalize_longitude(bindu_longitude)
    for name, plon in transit_longitudes.items():
        sep = abs((normalize_longitude(plon) - bb + 180.0) % 360.0 - 180.0)
        if sep <= orb:
            hits.append(
                {
                    "planet": name,
                    "longitude_sidereal_deg": float(plon),
                    "separation_deg": round(sep, 6),
                    "orb_deg": orb,
                    "trigger": "conjunction_candidate",
                }
            )
    hits.sort(key=lambda r: r["separation_deg"])
    return hits


__all__ = [
    "BHRIGU_BINDU_VARIANT",
    "DEFAULT_CONJUNCTION_ORB_DEG",
    "circular_midpoint",
    "compute_bhrigu_bindu",
    "transit_hits_on_bindu",
]

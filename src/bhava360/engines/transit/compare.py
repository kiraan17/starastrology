"""Transit vs natal overlay helpers — Candidate (TEC-035)."""

from __future__ import annotations

from typing import Any

from bhava360.chart.aspects import GRAHA_ASPECT_HOUSES, relative_house
from bhava360.kernel.derived import normalize_longitude, sign_from_longitude
from bhava360.kernel.models import PlanetName, SIGNS

TRANSIT_VARIANT = "transit_natal_overlay_candidate_v1"
DEFAULT_CONJUNCTION_ORB_DEG = 1.0


def _planet_map(chart: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(p["planet"]): p for p in chart.get("planets", [])}


def _lagna_sign(chart: dict[str, Any]) -> str:
    return chart["angles"]["whole_sign"]["ascendant"]["sign"]


def _moon_sign(chart: dict[str, Any]) -> str:
    return _planet_map(chart)["Moon"]["sign"]


def house_from_reference(reference_sign: str, body_sign: str) -> int:
    return relative_house(reference_sign, body_sign)


def circular_separation_deg(a: float, b: float) -> float:
    return abs((normalize_longitude(a) - normalize_longitude(b) + 180.0) % 360.0 - 180.0)


def transit_placements(
    *,
    natal_lagna_sign: str,
    natal_moon_sign: str,
    transit_planets: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Whole-sign houses of transit planets counted from natal Lagna and Moon."""
    rows: list[dict[str, Any]] = []
    for name, p in transit_planets.items():
        sign = str(p["sign"])
        rows.append(
            {
                "planet": name,
                "sign": sign,
                "sign_degree": p.get("sign_degree"),
                "longitude_sidereal_deg": p.get("longitude_sidereal_deg"),
                "house_from_natal_lagna": house_from_reference(natal_lagna_sign, sign),
                "house_from_natal_moon": house_from_reference(natal_moon_sign, sign),
                "is_retrograde": bool(p.get("is_retrograde")),
            }
        )
    return rows


def natal_vs_transit_sign_diff(
    natal_planets: dict[str, dict[str, Any]],
    transit_planets: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Per-planet natal sign vs current transit sign."""
    rows: list[dict[str, Any]] = []
    for name in natal_planets:
        if name not in transit_planets:
            continue
        n_sign = str(natal_planets[name]["sign"])
        t_sign = str(transit_planets[name]["sign"])
        rows.append(
            {
                "planet": name,
                "natal_sign": n_sign,
                "transit_sign": t_sign,
                "same_sign": n_sign == t_sign,
                "signs_apart": (SIGNS.index(t_sign) - SIGNS.index(n_sign)) % 12,
            }
        )
    return rows


def transit_natal_conjunctions(
    *,
    natal_planets: dict[str, dict[str, Any]],
    transit_planets: dict[str, dict[str, Any]],
    orb_deg: float = DEFAULT_CONJUNCTION_ORB_DEG,
) -> list[dict[str, Any]]:
    """Transit planet within orb of a natal planet longitude."""
    hits: list[dict[str, Any]] = []
    orb = float(orb_deg)
    for t_name, tp in transit_planets.items():
        t_lon = float(tp["longitude_sidereal_deg"])
        for n_name, np in natal_planets.items():
            n_lon = float(np["longitude_sidereal_deg"])
            sep = circular_separation_deg(t_lon, n_lon)
            if sep <= orb:
                hits.append(
                    {
                        "transit_planet": t_name,
                        "natal_planet": n_name,
                        "separation_deg": round(sep, 6),
                        "orb_deg": orb,
                        "transit_longitude_sidereal_deg": t_lon,
                        "natal_longitude_sidereal_deg": n_lon,
                        "kind": "conjunction",
                    }
                )
    hits.sort(key=lambda r: r["separation_deg"])
    return hits


def transit_aspects_to_natal(
    *,
    natal_planets: dict[str, dict[str, Any]],
    transit_planets: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Whole-sign graha aspects from transit planets to natal planets."""
    edges: list[dict[str, Any]] = []
    for t_name, tp in transit_planets.items():
        try:
            t_planet = PlanetName(t_name)
        except ValueError:
            continue
        t_sign = str(tp["sign"])
        aspect_houses = GRAHA_ASPECT_HOUSES.get(t_planet)
        if not aspect_houses:
            continue
        for n_name, np in natal_planets.items():
            n_sign = str(np["sign"])
            rel = relative_house(t_sign, n_sign)
            if rel in aspect_houses:
                edges.append(
                    {
                        "from_transit": t_name,
                        "to_natal": n_name,
                        "from_sign": t_sign,
                        "to_sign": n_sign,
                        "matched_house": rel,
                        "aspect_houses": list(aspect_houses),
                        "system": "graha_whole_sign_transit_to_natal",
                    }
                )
    return edges


def build_transit_overlay(
    natal_chart: dict[str, Any],
    transit_chart: dict[str, Any],
    *,
    conjunction_orb_deg: float = DEFAULT_CONJUNCTION_ORB_DEG,
) -> dict[str, Any]:
    """Assemble structural transit-vs-natal overlay (no verdicts)."""
    natal = _planet_map(natal_chart)
    transit = _planet_map(transit_chart)
    lagna = _lagna_sign(natal_chart)
    moon = _moon_sign(natal_chart)
    placements = transit_placements(
        natal_lagna_sign=lagna,
        natal_moon_sign=moon,
        transit_planets=transit,
    )
    by_house: dict[int, list[str]] = {h: [] for h in range(1, 13)}
    for row in placements:
        by_house[row["house_from_natal_lagna"]].append(row["planet"])

    conjunctions = transit_natal_conjunctions(
        natal_planets=natal,
        transit_planets=transit,
        orb_deg=conjunction_orb_deg,
    )
    aspects = transit_aspects_to_natal(natal_planets=natal, transit_planets=transit)
    sign_diff = natal_vs_transit_sign_diff(natal, transit)

    return {
        "variant": TRANSIT_VARIANT,
        "natal_lagna_sign": lagna,
        "natal_moon_sign": moon,
        "conjunction_orb_deg": float(conjunction_orb_deg),
        "placements": placements,
        "houses_from_natal_lagna": [
            {
                "house": h,
                "sign": SIGNS[(SIGNS.index(lagna) + h - 1) % 12],
                "occupants": by_house[h],
            }
            for h in range(1, 13)
        ],
        "natal_vs_transit_signs": sign_diff,
        "conjunctions": conjunctions,
        "aspects_transit_to_natal": aspects,
        "summary": {
            "placement_count": len(placements),
            "conjunction_count": len(conjunctions),
            "aspect_count": len(aspects),
            "planets_same_sign_as_natal": sum(1 for r in sign_diff if r["same_sign"]),
        },
    }


__all__ = [
    "DEFAULT_CONJUNCTION_ORB_DEG",
    "TRANSIT_VARIANT",
    "build_transit_overlay",
    "circular_separation_deg",
    "house_from_reference",
    "natal_vs_transit_sign_diff",
    "transit_aspects_to_natal",
    "transit_natal_conjunctions",
    "transit_placements",
]

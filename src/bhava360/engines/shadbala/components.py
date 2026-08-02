"""Shadbala component scaffold — Candidate thin slice (TEC-023)."""

from __future__ import annotations

from typing import Any

from bhava360.chart.dignity import DEBILITATION_SIGN, EXALTATION_DEGREE, EXALTATION_SIGN
from bhava360.kernel.derived import normalize_longitude
from bhava360.kernel.models import PlanetName, SIGNS

SHADBALA_VARIANT = "shadbala_partial_scaffold_candidate_v1"

CLASSICAL_PLANETS: tuple[str, ...] = (
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
)

# Naisargika Bala in Virupa: 60 × (7..1) / 7 (BPHS classical fixed order).
NAISARGIKA_VIRUPA: dict[str, float] = {
    "Sun": 60.0,
    "Moon": 51.428571,
    "Venus": 42.857143,
    "Jupiter": 34.285714,
    "Mercury": 25.714286,
    "Mars": 17.142857,
    "Saturn": 8.571429,
}

# Dig Bala strongest whole-sign house from Lagna (Candidate classical).
DIG_STRONG_HOUSE: dict[str, int] = {
    "Sun": 10,
    "Mars": 10,
    "Jupiter": 1,
    "Mercury": 1,
    "Moon": 4,
    "Venus": 4,
    "Saturn": 7,
}

# Full-pack minimum totals (Virupa) — informational only until all 6 components exist.
FULL_MINIMUM_VIRUPA: dict[str, float] = {
    "Sun": 390.0,
    "Moon": 360.0,
    "Mars": 300.0,
    "Mercury": 420.0,
    "Jupiter": 390.0,
    "Venus": 330.0,
    "Saturn": 300.0,
}

MALE_PLANETS = frozenset({"Sun", "Mars", "Jupiter"})
FEMALE_PLANETS = frozenset({"Moon", "Venus"})
# Mercury and Saturn are treated as neutral/both in classical ojayugma (gain in both).
NEUTRAL_OJAYUGMA = frozenset({"Mercury", "Saturn"})


def _planet_enum(name: str) -> PlanetName:
    return PlanetName(name)


def _exaltation_longitude(planet: str) -> float:
    p = _planet_enum(planet)
    sign = EXALTATION_SIGN[p]
    deg = EXALTATION_DEGREE[p]
    return SIGNS.index(sign) * 30.0 + deg


def _debilitation_longitude(planet: str) -> float:
    p = _planet_enum(planet)
    sign = DEBILITATION_SIGN[p]
    deg = EXALTATION_DEGREE[p]  # same degree in opposite sign
    return SIGNS.index(sign) * 30.0 + deg


def angular_distance_deg(a: float, b: float) -> float:
    return abs((normalize_longitude(a) - normalize_longitude(b) + 180.0) % 360.0 - 180.0)


def naisargika_bala(planet: str) -> float:
    return float(NAISARGIKA_VIRUPA[planet])


def dig_bala(*, planet: str, rasi_house: int) -> float:
    """
    Directional strength from whole-sign house.

    60 at dig-strong house, 0 at opposite (6 houses away), linear by house steps.
    """
    strong = DIG_STRONG_HOUSE[planet]
    steps = min((rasi_house - strong) % 12, (strong - rasi_house) % 12)
    return max(0.0, 60.0 * (1.0 - steps / 6.0))


def uchcha_bala(*, planet: str, longitude_sidereal_deg: float) -> float:
    """Exaltation strength: 60 at exaltation degree, 0 at debilitation degree."""
    deb = _debilitation_longitude(planet)
    dist = angular_distance_deg(longitude_sidereal_deg, deb)
    return (dist / 180.0) * 60.0


def kendradi_bala(*, rasi_house: int) -> float:
    if rasi_house in {1, 4, 7, 10}:
        return 60.0
    if rasi_house in {2, 5, 8, 11}:
        return 30.0
    return 15.0


def ojayugma_rasi_bala(*, planet: str, sign: str) -> float:
    """
    Odd/even rasi portion of Ojayugma (Candidate thin; navamsa half deferred).

    Male planets: 15 in odd signs. Female: 15 in even signs.
    Mercury/Saturn: 15 in either (classical both-nature thin rule).
    """
    odd = (SIGNS.index(sign) % 2) == 0  # Aries=0 odd
    if planet in NEUTRAL_OJAYUGMA:
        return 15.0
    if planet in MALE_PLANETS:
        return 15.0 if odd else 0.0
    if planet in FEMALE_PLANETS:
        return 15.0 if not odd else 0.0
    return 0.0


def compute_planet_shadbala_partial(
    *,
    planet: str,
    longitude_sidereal_deg: float,
    sign: str,
    rasi_house: int,
) -> dict[str, Any]:
    nais = naisargika_bala(planet)
    dig = dig_bala(planet=planet, rasi_house=rasi_house)
    uchcha = uchcha_bala(planet=planet, longitude_sidereal_deg=longitude_sidereal_deg)
    kend = kendradi_bala(rasi_house=rasi_house)
    oja = ojayugma_rasi_bala(planet=planet, sign=sign)

    sthana_partial = uchcha + kend + oja
    components = {
        "naisargika": round(nais, 6),
        "dig": round(dig, 6),
        "sthana_partial": {
            "uchcha": round(uchcha, 6),
            "kendradi": round(kend, 6),
            "ojayugma_rasi": round(oja, 6),
            "subtotal": round(sthana_partial, 6),
            "deferred_subs": ["saptavargaja", "ojayugma_navamsa", "drekkana"],
        },
    }
    partial_total = nais + dig + sthana_partial
    return {
        "planet": planet,
        "rasi_house": rasi_house,
        "sign": sign,
        "longitude_sidereal_deg": normalize_longitude(longitude_sidereal_deg),
        "components_virupa": components,
        "partial_total_virupa": round(partial_total, 6),
        "partial_total_rupa": round(partial_total / 60.0, 6),
        "full_minimum_virupa": FULL_MINIMUM_VIRUPA[planet],
        "full_minimum_comparison": "deferred_until_complete_shadbala",
        "included_components": [
            "naisargika",
            "dig",
            "sthana.uchcha",
            "sthana.kendradi",
            "sthana.ojayugma_rasi",
        ],
        "deferred_components": [
            "sthana.saptavargaja",
            "sthana.drekkana",
            "sthana.ojayugma_navamsa",
            "kala",
            "chesta",
            "drik",
        ],
    }


def compute_shadbala_pack(chart: dict[str, Any]) -> dict[str, Any]:
    """Compute partial Shadbala for classical seven planets from a chart dict."""
    planets = {p["planet"]: p for p in chart.get("planets") or []}
    rows: list[dict[str, Any]] = []
    for name in CLASSICAL_PLANETS:
        p = planets.get(name)
        if not p:
            continue
        house = int((p.get("houses") or {}).get("rasi_house") or 0)
        if house < 1:
            continue
        rows.append(
            compute_planet_shadbala_partial(
                planet=name,
                longitude_sidereal_deg=float(p["longitude_sidereal_deg"]),
                sign=str(p["sign"]),
                rasi_house=house,
            )
        )

    ranked = sorted(rows, key=lambda r: r["partial_total_virupa"], reverse=True)
    return {
        "variant": SHADBALA_VARIANT,
        "unit": "virupa",
        "rupa_definition": "1 rupa = 60 virupa",
        "planets": rows,
        "summary": {
            "planet_count": len(rows),
            "strongest_partial": ranked[0]["planet"] if ranked else None,
            "strongest_partial_virupa": ranked[0]["partial_total_virupa"] if ranked else None,
            "weakest_partial": ranked[-1]["planet"] if ranked else None,
            "included_component_families": ["naisargika", "dig", "sthana_partial"],
            "deferred_component_families": ["kala", "chesta", "drik", "sthana_remainder"],
        },
        "notes": [
            "Candidate partial scaffold — not a complete BPHS Shadbala pack.",
            "Partial totals must not be compared to full-pack minima for verdicts.",
            "Dig Bala uses whole-sign house distance from dig-strong house.",
            "Uchcha Bala uses angular distance from debilitation degree.",
        ],
    }


__all__ = [
    "CLASSICAL_PLANETS",
    "SHADBALA_VARIANT",
    "compute_planet_shadbala_partial",
    "compute_shadbala_pack",
    "dig_bala",
    "kendradi_bala",
    "naisargika_bala",
    "ojayugma_rasi_bala",
    "uchcha_bala",
]

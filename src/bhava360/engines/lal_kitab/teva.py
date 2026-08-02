"""Lal Kitab Teva / aspects / varshphal helpers — Candidate (TEC-090)."""

from __future__ import annotations

from typing import Any

from bhava360.kernel.models import SIGNS

LK_VARIANT = "lal_kitab_teva_candidate_v1"

# Fixed Teva: Aries = house 1 … Pisces = house 12 (independent of lagna).
# Pakka Ghar (permanent houses) — Candidate classical LK list.
PAKKA_GHAR: dict[str, int] = {
    "Sun": 1,
    "Moon": 4,
    "Mars": 3,
    "Mercury": 7,
    "Jupiter": 2,
    "Venus": 7,
    "Saturn": 10,
    "Rahu": 12,
    "Ketu": 6,
}

# Aspect offsets counted forward from the planet's Teva house (1 = same house).
# Candidate LK graha aspect table (common published form).
LK_ASPECT_OFFSETS: dict[str, tuple[int, ...]] = {
    "Sun": (7,),
    "Moon": (7,),
    "Mercury": (7,),
    "Venus": (7,),
    "Mars": (4, 7, 8),
    "Jupiter": (5, 7, 9),
    "Saturn": (3, 7, 10),
    "Rahu": (5, 7, 9),
    "Ketu": (5, 7, 9),
}

AXIS_PAIRS: tuple[tuple[int, int], ...] = (
    (1, 7),
    (2, 8),
    (3, 9),
    (4, 10),
    (5, 11),
    (6, 12),
)


def teva_house_from_sign(sign: str) -> int:
    """Lal Kitab fixed house for a sidereal sign (Aries→1)."""
    if sign not in SIGNS:
        raise ValueError(f"unknown sign: {sign}")
    return SIGNS.index(sign) + 1


def sign_for_teva_house(house: int) -> str:
    if not 1 <= house <= 12:
        raise ValueError(f"teva house must be 1–12, got {house}")
    return SIGNS[house - 1]


def aspect_houses_from(planet: str, from_house: int) -> list[int]:
    """Houses aspected by `planet` sitting in `from_house` (forward count)."""
    offsets = LK_ASPECT_OFFSETS.get(planet)
    if not offsets:
        return []
    if not 1 <= from_house <= 12:
        raise ValueError(f"from_house must be 1–12, got {from_house}")
    out: list[int] = []
    for off in offsets:
        # off=7 means 7th from self: (from_house - 1 + 6) % 12 + 1
        target = ((from_house - 1) + (off - 1)) % 12 + 1
        out.append(target)
    return out


def annual_teva_house(natal_house: int, age: int) -> int:
    """Lal Kitab varshphal: advance one house per completed year of age."""
    if not 1 <= natal_house <= 12:
        raise ValueError(f"natal_house must be 1–12, got {natal_house}")
    if age < 0:
        raise ValueError(f"age must be >= 0, got {age}")
    return ((natal_house - 1) + age) % 12 + 1


def completed_age_for_year(*, birth_year: int, target_year: int) -> int:
    """Age completed on birthday in target_year (= target_year − birth_year)."""
    if target_year < birth_year:
        raise ValueError("target_year cannot be before birth_year")
    return target_year - birth_year


def build_lal_kitab_teva(
    chart: dict[str, Any],
    *,
    target_year: int | None = None,
    age: int | None = None,
) -> dict[str, Any]:
    """
    Build fixed-Aries Teva placements, Pakka Ghar flags, aspects, axis pairs.

    Optional arithmetic varshphal when age or target_year is provided.
    """
    planets_out: list[dict[str, Any]] = []
    by_house: dict[int, list[str]] = {h: [] for h in range(1, 13)}

    for p in chart.get("planets", []):
        name = str(p["planet"])
        sign = str(p["sign"])
        teva_h = teva_house_from_sign(sign)
        pakka = PAKKA_GHAR.get(name)
        parashara_house = (p.get("houses") or {}).get("rasi_house")
        row = {
            "planet": name,
            "sign": sign,
            "sign_degree": p.get("sign_degree"),
            "longitude_sidereal_deg": p.get("longitude_sidereal_deg"),
            "teva_house": teva_h,
            "teva_sign": sign_for_teva_house(teva_h),  # same as sign by construction
            "pakka_ghar": pakka,
            "in_pakka_ghar": pakka == teva_h if pakka is not None else None,
            "parashara_rasi_house": parashara_house,
            "house_system_differs": (
                parashara_house is not None and int(parashara_house) != teva_h
            ),
            "aspects_houses": aspect_houses_from(name, teva_h),
        }
        planets_out.append(row)
        by_house[teva_h].append(name)

    # Yuti: co-residents in same teva house
    yuti: list[dict[str, Any]] = []
    for h, occupants in by_house.items():
        if len(occupants) >= 2:
            yuti.append({"house": h, "sign": sign_for_teva_house(h), "planets": occupants})

    # Axis / virtual conjunctions
    axis_yuti: list[dict[str, Any]] = []
    for a, b in AXIS_PAIRS:
        pa = by_house[a]
        pb = by_house[b]
        if pa and pb:
            axis_yuti.append(
                {
                    "axis": [a, b],
                    "signs": [sign_for_teva_house(a), sign_for_teva_house(b)],
                    "planets_a": pa,
                    "planets_b": pb,
                }
            )

    # Aspect edges: planet → house (and planets sitting there)
    aspect_edges: list[dict[str, Any]] = []
    for row in planets_out:
        for th in row["aspects_houses"]:
            aspect_edges.append(
                {
                    "from_planet": row["planet"],
                    "from_house": row["teva_house"],
                    "to_house": th,
                    "to_sign": sign_for_teva_house(th),
                    "to_planets": list(by_house[th]),
                }
            )

    houses: list[dict[str, Any]] = []
    for h in range(1, 13):
        houses.append(
            {
                "house": h,
                "sign": sign_for_teva_house(h),
                "occupants": list(by_house[h]),
                "pakka_lords": [pl for pl, ph in PAKKA_GHAR.items() if ph == h],
            }
        )

    # Contradiction summary vs Parashara lagna houses
    differs = [r["planet"] for r in planets_out if r.get("house_system_differs")]

    varshphal: dict[str, Any] | None = None
    resolved_age = age
    birth_year = None
    local = (chart.get("input") or {}).get("local_datetime")
    if local:
        # "YYYY-MM-DD HH:MM:SS" or iso
        birth_year = int(str(local)[:4])
    if resolved_age is None and target_year is not None and birth_year is not None:
        resolved_age = completed_age_for_year(birth_year=birth_year, target_year=target_year)
    if resolved_age is not None:
        annual_planets = []
        annual_by_house: dict[int, list[str]] = {h: [] for h in range(1, 13)}
        for row in planets_out:
            ah = annual_teva_house(row["teva_house"], resolved_age)
            annual_planets.append(
                {
                    "planet": row["planet"],
                    "natal_teva_house": row["teva_house"],
                    "annual_teva_house": ah,
                    "annual_sign": sign_for_teva_house(ah),
                }
            )
            annual_by_house[ah].append(row["planet"])
        varshphal = {
            "age": resolved_age,
            "target_year": target_year,
            "birth_year": birth_year,
            "planets": annual_planets,
            "houses": [
                {
                    "house": h,
                    "sign": sign_for_teva_house(h),
                    "occupants": annual_by_house[h],
                }
                for h in range(1, 13)
            ],
        }

    lagna_sign = (
        chart.get("angles", {}).get("whole_sign", {}).get("ascendant", {}).get("sign")
    )

    return {
        "variant": LK_VARIANT,
        "teva_basis": "fixed_aries_house_1",
        "lagna_sign_parashara": lagna_sign,
        "pakka_ghar": dict(PAKKA_GHAR),
        "planets": planets_out,
        "houses": houses,
        "yuti": yuti,
        "axis_yuti": axis_yuti,
        "aspect_edges": aspect_edges,
        "varshphal": varshphal,
        "contradictions": {
            "vs_parashara": [
                "Lal Kitab Teva uses fixed Aries=house 1; Parashara rasi houses count from lagna.",
                "Do not blend LK aspects with Parashara graha aspects.",
            ],
            "planets_with_house_number_diff": differs,
            "diff_count": len(differs),
        },
        "summary": {
            "planet_count": len(planets_out),
            "yuti_count": len(yuti),
            "axis_yuti_count": len(axis_yuti),
            "aspect_edge_count": len(aspect_edges),
            "in_pakka_ghar_count": sum(
                1 for r in planets_out if r.get("in_pakka_ghar") is True
            ),
            "house_diff_vs_parashara_count": len(differs),
            "varshphal_included": varshphal is not None,
        },
    }


__all__ = [
    "AXIS_PAIRS",
    "LK_ASPECT_OFFSETS",
    "LK_VARIANT",
    "PAKKA_GHAR",
    "annual_teva_house",
    "aspect_houses_from",
    "build_lal_kitab_teva",
    "completed_age_for_year",
    "sign_for_teva_house",
    "teva_house_from_sign",
]

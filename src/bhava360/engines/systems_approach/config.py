"""Systems Approach configuration helpers — Candidate (TEC-091)."""

from __future__ import annotations

from typing import Any

from bhava360.kernel.models import SIGNS

SA_VARIANT = "systems_approach_config_candidate_v1"

# SA mooltrikona signs (Candidate). Moon uses Cancer under Systems' Approach.
SA_MOOLTRIKONA_SIGN: dict[str, str] = {
    "Sun": "Leo",
    "Moon": "Cancer",
    "Mars": "Aries",
    "Mercury": "Virgo",
    "Jupiter": "Sagittarius",
    "Venus": "Libra",
    "Saturn": "Aquarius",
}

CLASSICAL_PLANETS: tuple[str, ...] = (
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
)
NODES: tuple[str, ...] = ("Rahu", "Ketu")
DUSTHANA_HOUSES: frozenset[int] = frozenset({6, 8, 12})
CLOSE_ORB_DEG = 5.0
INFANCY_MAX_DEG = 5.0
OLD_AGE_MIN_DEG = 25.0


def house_of_sign_from_lagna(lagna_sign: str, sign: str) -> int:
    """Whole-sign house of `sign` counted from lagna (1–12)."""
    if lagna_sign not in SIGNS:
        raise ValueError(f"unknown lagna sign: {lagna_sign}")
    if sign not in SIGNS:
        raise ValueError(f"unknown sign: {sign}")
    return ((SIGNS.index(sign) - SIGNS.index(lagna_sign)) % 12) + 1


def classify_functional_natures(lagna_sign: str) -> dict[str, Any]:
    """
    Functional benefic/malefic by ascendant (Systems' Approach).

    Rule (Candidate): Rahu/Ketu always FM; other planets whose SA mooltrikona
    sign falls in houses 6/8/12 from lagna are FM; else FB. No neutrals.
    """
    rows: list[dict[str, Any]] = []
    functional_malefics: list[str] = []
    functional_benefics: list[str] = []

    for planet, mt_sign in SA_MOOLTRIKONA_SIGN.items():
        mt_house = house_of_sign_from_lagna(lagna_sign, mt_sign)
        is_fm = mt_house in DUSTHANA_HOUSES
        nature = "functional_malefic" if is_fm else "functional_benefic"
        row = {
            "planet": planet,
            "nature": nature,
            "mooltrikona_sign": mt_sign,
            "mooltrikona_house": mt_house,
            "mt_in_dusthana": is_fm,
        }
        rows.append(row)
        if is_fm:
            functional_malefics.append(planet)
        else:
            functional_benefics.append(planet)

    for node in NODES:
        rows.append(
            {
                "planet": node,
                "nature": "functional_malefic",
                "mooltrikona_sign": None,
                "mooltrikona_house": None,
                "mt_in_dusthana": None,
                "reason": "nodes_always_fm",
            }
        )
        functional_malefics.append(node)

    return {
        "lagna_sign": lagna_sign,
        "dusthana_houses": sorted(DUSTHANA_HOUSES),
        "planets": rows,
        "functional_malefics": functional_malefics,
        "functional_benefics": functional_benefics,
    }


def structural_weakness_flags(
    *,
    planet: str,
    sign: str,
    sign_degree: float,
    rasi_house: int,
    dignity_primary: str | None,
) -> dict[str, Any]:
    """
    Structural SA weakness markers (Candidate) — flags only, no strength score.
    """
    infancy = 0.0 <= float(sign_degree) < INFANCY_MAX_DEG
    old_age = float(sign_degree) >= OLD_AGE_MIN_DEG
    in_dusthana = int(rasi_house) in DUSTHANA_HOUSES
    debilitated = dignity_primary == "debilitated"
    reasons: list[str] = []
    if infancy:
        reasons.append("infancy")
    if old_age:
        reasons.append("old_age")
    if in_dusthana:
        reasons.append("dusthana_placement")
    if debilitated:
        reasons.append("debilitated")
    return {
        "planet": planet,
        "sign": sign,
        "sign_degree": float(sign_degree),
        "rasi_house": int(rasi_house),
        "weak_candidate": bool(reasons),
        "flags": {
            "infancy": infancy,
            "old_age": old_age,
            "dusthana_placement": in_dusthana,
            "debilitated": debilitated,
        },
        "reasons": reasons,
    }


def close_longitude_pairs(
    longitudes: dict[str, float],
    *,
    orb_deg: float = CLOSE_ORB_DEG,
) -> list[dict[str, Any]]:
    """Pairs within orb on the 360° circle (Candidate close-conjunction surface)."""
    names = list(longitudes.keys())
    pairs: list[dict[str, Any]] = []
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            la = float(longitudes[a]) % 360.0
            lb = float(longitudes[b]) % 360.0
            delta = abs(la - lb) % 360.0
            if delta > 180.0:
                delta = 360.0 - delta
            if delta <= orb_deg:
                pairs.append(
                    {
                        "a": a,
                        "b": b,
                        "orb_deg": round(delta, 6),
                        "within_orb": True,
                    }
                )
    return pairs


def build_systems_approach_profile(chart: dict[str, Any]) -> dict[str, Any]:
    """Assemble SA configuration profile from a constructed chart."""
    lagna_sign = chart["angles"]["whole_sign"]["ascendant"]["sign"]
    natures = classify_functional_natures(lagna_sign)
    fm_set = set(natures["functional_malefics"])

    planet_rows: list[dict[str, Any]] = []
    longitudes: dict[str, float] = {}
    for p in chart.get("planets", []):
        name = str(p["planet"])
        longitudes[name] = float(p["longitude_sidereal_deg"])
        nature_row = next(r for r in natures["planets"] if r["planet"] == name)
        weak = structural_weakness_flags(
            planet=name,
            sign=str(p["sign"]),
            sign_degree=float(p["sign_degree"]),
            rasi_house=int((p.get("houses") or {}).get("rasi_house") or 0),
            dignity_primary=(p.get("dignity") or {}).get("primary"),
        )
        planet_rows.append(
            {
                "planet": name,
                "sign": p["sign"],
                "sign_degree": p["sign_degree"],
                "longitude_sidereal_deg": p["longitude_sidereal_deg"],
                "rasi_house": (p.get("houses") or {}).get("rasi_house"),
                "dignity_primary": (p.get("dignity") or {}).get("primary"),
                "functional_nature": nature_row["nature"],
                "mooltrikona_sign": nature_row.get("mooltrikona_sign"),
                "mooltrikona_house": nature_row.get("mooltrikona_house"),
                "weakness": weak,
            }
        )

    close_pairs = close_longitude_pairs(longitudes, orb_deg=CLOSE_ORB_DEG)
    fm_close = [
        pair
        for pair in close_pairs
        if pair["a"] in fm_set or pair["b"] in fm_set
    ]

    # House → SA primary planet (lord of MT sign occupying that house), if any.
    mt_house_lords: dict[int, str] = {}
    for planet, mt_sign in SA_MOOLTRIKONA_SIGN.items():
        h = house_of_sign_from_lagna(lagna_sign, mt_sign)
        mt_house_lords[h] = planet

    houses: list[dict[str, Any]] = []
    for h in range(1, 13):
        sign = SIGNS[(SIGNS.index(lagna_sign) + h - 1) % 12]
        occupants = [
            r["planet"] for r in planet_rows if r.get("rasi_house") == h
        ]
        houses.append(
            {
                "house": h,
                "sign": sign,
                "is_dusthana": h in DUSTHANA_HOUSES,
                "sa_primary_planet": mt_house_lords.get(h),
                "occupants": occupants,
            }
        )

    return {
        "variant": SA_VARIANT,
        "lagna_sign": lagna_sign,
        "config": {
            "ascendant_centric": True,
            "moon_mooltrikona_sign": SA_MOOLTRIKONA_SIGN["Moon"],
            "dusthana_houses": sorted(DUSTHANA_HOUSES),
            "close_orb_deg": CLOSE_ORB_DEG,
            "infancy_max_deg": INFANCY_MAX_DEG,
            "old_age_min_deg": OLD_AGE_MIN_DEG,
        },
        "functional_natures": natures,
        "planets": planet_rows,
        "houses": houses,
        "close_longitude_pairs": close_pairs,
        "functional_malefic_close_pairs": fm_close,
        "summary": {
            "functional_malefic_count": len(natures["functional_malefics"]),
            "functional_benefic_count": len(natures["functional_benefics"]),
            "weak_candidate_count": sum(
                1 for r in planet_rows if r["weakness"]["weak_candidate"]
            ),
            "fm_close_pair_count": len(fm_close),
        },
    }


__all__ = [
    "CLOSE_ORB_DEG",
    "DUSTHANA_HOUSES",
    "SA_MOOLTRIKONA_SIGN",
    "SA_VARIANT",
    "build_systems_approach_profile",
    "classify_functional_natures",
    "close_longitude_pairs",
    "house_of_sign_from_lagna",
    "structural_weakness_flags",
]

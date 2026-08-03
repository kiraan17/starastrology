"""Bhava Bala component formulas (Candidate / partial).

Classical Bhava Bala (BPHS / JHora overview) is typically:

  Bhava Bala = Bhavadhipati Bala + Bhava Dig Bala + Bhava Drishti Bala

This module implements a **partial** Candidate thin slice:

1. **Bhavadhipati** — lord's partial Shadbala total (TEC-023)
2. **Bhava Dig** — directional house strength from Lagna class
   (Nara → 1st; Jalachara → 4th; Chatushpada → 10th; Keeta → 7th)
3. **Bhava Drishti** — whole-sign graha aspect net onto the house rasi
   (same weight table as Shadbala Drik thin)

Deferred: Sagittarius/Capricorn half-sign Dig splits; benefic/malefic
Drishti polarity; full classical rupas calibration.

Stamp: ``bhava_bala_partial_candidate_v1``.
"""

from __future__ import annotations

from typing import Any

from bhava360.chart.aspects import GRAHA_ASPECT_HOUSES, relative_house
from bhava360.chart.dignity import sign_lord
from bhava360.engines.shadbala.components import CLASSICAL_PLANETS, compute_shadbala_pack
from bhava360.kernel.models import PlanetName, SIGNS

BHAVA_BALA_VARIANT = "bhava_bala_partial_candidate_v1"

# Dig bala when the house matches the Lagna-class strong direction (virupa).
_DIG_STRONG_VIRUPA = 60.0
_DIG_WEAK_VIRUPA = 0.0

# Lagna class → house number that receives Dig strength.
_LAGNA_CLASS_STRONG_HOUSE: dict[str, int] = {
    "nara": 1,
    "jalachara": 4,
    "chatushpada": 10,
    "keeta": 7,
}


def lagna_class(sign: str) -> str:
    """Classify Lagna for Bhava Dig (Candidate; Sag/Cap half-sign deferred)."""
    if sign in {"Gemini", "Leo", "Virgo", "Libra", "Aquarius"}:
        return "nara"
    if sign in {"Cancer", "Pisces"}:
        return "jalachara"
    if sign in {"Aries", "Taurus", "Sagittarius", "Capricorn"}:
        return "chatushpada"
    if sign == "Scorpio":
        return "keeta"
    return "nara"


def _aspect_weight(matched_house: int) -> float:
    """Match Shadbala Drik thin weights (Candidate)."""
    if matched_house == 7:
        return 15.0
    return 10.0


def _house_sign(lagna_sign: str, house: int) -> str:
    idx = SIGNS.index(lagna_sign)
    return SIGNS[(idx + house - 1) % 12]


def _drishti_onto_sign(*, house_sign: str, planet_signs: dict[str, str]) -> dict[str, Any]:
    """Sum whole-sign graha aspect weights onto a house sign (raw, no polarity)."""
    hits: list[dict[str, Any]] = []
    raw = 0.0
    for other, from_sign in planet_signs.items():
        if other not in CLASSICAL_PLANETS:
            continue
        pe = PlanetName(other)
        houses = GRAHA_ASPECT_HOUSES.get(pe)
        if not houses:
            continue
        rel = relative_house(from_sign, house_sign)
        if rel not in houses:
            continue
        w = _aspect_weight(rel)
        hits.append({"from": other, "matched_house": rel, "weight": w})
        raw += w
    return {
        "value": round(raw, 6),
        "hits": hits,
        "basis": "whole_sign_graha_aspect_sum_candidate",
    }


def compute_bhava_bala_pack(
    chart: dict[str, Any],
    *,
    shadbala: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compute partial Bhava Bala for houses 1–12 from a chart dict."""
    if shadbala is None:
        shadbala = compute_shadbala_pack(chart)

    planet_totals: dict[str, float] = {}
    for row in shadbala.get("planets") or []:
        if isinstance(row, dict) and "planet" in row and "partial_total_virupa" in row:
            planet_totals[str(row["planet"])] = float(row["partial_total_virupa"])

    angles = (chart.get("angles") or {}).get("whole_sign") or {}
    asc = angles.get("ascendant") or {}
    lagna_sign = str(asc.get("sign") or "")
    if not lagna_sign or lagna_sign not in SIGNS:
        raise ValueError("chart.angles.whole_sign.ascendant.sign required")

    lclass = lagna_class(lagna_sign)
    strong_house = _LAGNA_CLASS_STRONG_HOUSE[lclass]

    planets = {p["planet"]: p for p in chart.get("planets") or []}
    planet_signs = {
        name: str(p["sign"])
        for name, p in planets.items()
        if name in CLASSICAL_PLANETS and p.get("sign")
    }

    houses: list[dict[str, Any]] = []
    for house in range(1, 13):
        sign = _house_sign(lagna_sign, house)
        lord = sign_lord(sign)
        lord_name = lord.value if lord else None
        bhavadhipati = planet_totals.get(lord_name or "", 0.0)
        dig = _DIG_STRONG_VIRUPA if house == strong_house else _DIG_WEAK_VIRUPA
        drishti = _drishti_onto_sign(house_sign=sign, planet_signs=planet_signs)
        total = bhavadhipati + dig + float(drishti["value"])
        houses.append(
            {
                "house": house,
                "sign": sign,
                "lord": lord_name,
                "components_virupa": {
                    "bhavadhipati": round(bhavadhipati, 6),
                    "dig": round(dig, 6),
                    "drishti": drishti,
                },
                "partial_total_virupa": round(total, 6),
                "partial_total_rupa": round(total / 60.0, 6),
            }
        )

    ranked = sorted(houses, key=lambda h: h["partial_total_virupa"], reverse=True)
    return {
        "variant": BHAVA_BALA_VARIANT,
        "unit": "virupa",
        "rupa_definition": "1 rupa = 60 virupa",
        "lagna_sign": lagna_sign,
        "lagna_class": lclass,
        "dig_strong_house": strong_house,
        "shadbala_variant": shadbala.get("variant"),
        "houses": houses,
        "summary": {
            "house_count": len(houses),
            "strongest_house": ranked[0]["house"] if ranked else None,
            "strongest_partial_virupa": ranked[0]["partial_total_virupa"] if ranked else None,
            "weakest_house": ranked[-1]["house"] if ranked else None,
            "weakest_partial_virupa": ranked[-1]["partial_total_virupa"] if ranked else None,
            "included_components": ["bhavadhipati", "dig", "drishti"],
            "deferred_components": [
                "dig_sag_cap_half_sign",
                "drishti_benefic_malefic_polarity",
                "classical_rupas_calibration",
            ],
        },
        "notes": [
            "Candidate partial scaffold — not complete BPHS Bhava Bala.",
            "Bhavadhipati uses partial Shadbala totals (TEC-023).",
            "Dig: Lagna-class strong house only (60); others 0.",
            "Drishti: raw whole-sign aspect weight sum (no benefic/malefic flip).",
            "Do not treat partial totals as classical verdict thresholds.",
        ],
    }


__all__ = [
    "BHAVA_BALA_VARIANT",
    "compute_bhava_bala_pack",
    "lagna_class",
]

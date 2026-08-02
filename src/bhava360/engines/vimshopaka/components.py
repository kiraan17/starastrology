"""Vimshopaka Bala — Candidate thin slice (TEC-025).

Shodashavarga weighted dignity score (max 20).

Formula (BPHS overview):
  contribution = (swaviswa_weight * varga_vishwa) / 20
  vimshopaka = sum(contributions)

Varga Vishwa (Candidate, permanent friendship only — temporal deferred):
  Own / Moolatrikona / Exalted → 20
  Permanent friend of sign-lord → 15
  Neutral → 10
  Permanent enemy → 7
  (Great friend/enemy deferred)

Stamp: ``vimshopaka_shodashavarga_candidate_v1``.
"""

from __future__ import annotations

from typing import Any

from bhava360.chart.dignity import (
    DEBILITATION_SIGN,
    EXALTATION_SIGN,
    MOOLATRIKONA_RANGE,
    OWN_SIGNS,
    sign_lord,
)
from bhava360.chart.vargas import VargaId, varga_sign
from bhava360.kernel.models import PlanetName

VIMSHOPAKA_VARIANT = "vimshopaka_shodashavarga_candidate_v1"

CLASSICAL_PLANETS: tuple[str, ...] = (
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
)

# BPHS Shodashavarga swaviswa weights (sum = 20).
SHODASHAVARGA_WEIGHTS: dict[str, float] = {
    "D1": 3.5,
    "D2": 1.0,
    "D3": 1.0,
    "D4": 0.5,
    "D7": 0.5,
    "D9": 3.0,
    "D10": 0.5,
    "D12": 0.5,
    "D16": 2.0,
    "D20": 0.5,
    "D24": 0.5,
    "D27": 0.5,
    "D30": 1.0,
    "D40": 0.5,
    "D45": 0.5,
    "D60": 4.0,
}

# Permanent natural friendship (same Candidate table as Ashtakoota Graha Maitri).
_FRIENDS: dict[str, frozenset[str]] = {
    "Sun": frozenset({"Moon", "Mars", "Jupiter"}),
    "Moon": frozenset({"Sun", "Mercury"}),
    "Mars": frozenset({"Sun", "Moon", "Jupiter"}),
    "Mercury": frozenset({"Sun", "Venus"}),
    "Jupiter": frozenset({"Sun", "Moon", "Mars"}),
    "Venus": frozenset({"Mercury", "Saturn"}),
    "Saturn": frozenset({"Mercury", "Venus"}),
}
_NEUTRALS: dict[str, frozenset[str]] = {
    "Sun": frozenset({"Mercury"}),
    "Moon": frozenset({"Mars", "Jupiter", "Venus", "Saturn"}),
    "Mars": frozenset({"Venus", "Saturn"}),
    "Mercury": frozenset({"Mars", "Jupiter", "Saturn"}),
    "Jupiter": frozenset({"Saturn"}),
    "Venus": frozenset({"Mars", "Jupiter"}),
    "Saturn": frozenset({"Jupiter"}),
}

_VARGA_VISHWA = {
    "own_or_exalted": 20.0,
    "friend": 15.0,
    "neutral": 10.0,
    "enemy": 7.0,
}


def _in_moolatrikona(planet: PlanetName, sign: str, sign_degree: float) -> bool:
    spec = MOOLATRIKONA_RANGE.get(planet)
    if not spec:
        return False
    m_sign, start, end = spec
    return sign == m_sign and start <= sign_degree < end


def permanent_relation(planet: str, other: str) -> str:
    """Return friend | neutral | enemy | self for permanent natural relation."""
    if planet == other:
        return "self"
    if other in _FRIENDS.get(planet, ()):
        return "friend"
    if other in _NEUTRALS.get(planet, ()):
        return "neutral"
    return "enemy"


def varga_vishwa(*, planet: str, sign: str, sign_degree: float = 0.0) -> dict[str, Any]:
    """Candidate Varga Vishwa for a placement (permanent friendship only)."""
    pe = PlanetName(planet)
    lord = sign_lord(sign)
    lord_name = lord.value if lord else None

    if sign in OWN_SIGNS.get(pe, set()) or EXALTATION_SIGN.get(pe) == sign:
        return {
            "points": _VARGA_VISHWA["own_or_exalted"],
            "basis": "own_or_exalted",
            "sign_lord": lord_name,
        }
    if _in_moolatrikona(pe, sign, sign_degree):
        return {
            "points": _VARGA_VISHWA["own_or_exalted"],
            "basis": "moolatrikona",
            "sign_lord": lord_name,
        }
    if lord_name is None:
        return {"points": 0.0, "basis": "unknown_sign", "sign_lord": None}
    if lord_name == planet:
        return {
            "points": _VARGA_VISHWA["own_or_exalted"],
            "basis": "own",
            "sign_lord": lord_name,
        }

    rel = permanent_relation(planet, lord_name)
    points = _VARGA_VISHWA[rel]
    basis = rel
    if DEBILITATION_SIGN.get(pe) == sign:
        basis = f"{rel}_in_debilitation_sign"
    return {"points": points, "basis": basis, "sign_lord": lord_name}


def _placement_sign(planet_row: dict[str, Any], varga: str) -> tuple[str, float]:
    """Resolve varga sign from chart planet row or recompute from longitude."""
    vargas = planet_row.get("vargas") or {}
    entry = vargas.get(varga)
    if isinstance(entry, dict) and entry.get("sign"):
        return str(entry["sign"]), float(entry.get("sign_degree") or 0.0)
    lon = float(planet_row["longitude_sidereal_deg"])
    place = varga_sign(lon, VargaId(varga))
    return place.sign, place.sign_degree


def compute_planet_vimshopaka(planet_row: dict[str, Any]) -> dict[str, Any]:
    planet = str(planet_row["planet"])
    contributions: list[dict[str, Any]] = []
    total = 0.0
    for varga, weight in SHODASHAVARGA_WEIGHTS.items():
        sign, sign_deg = _placement_sign(planet_row, varga)
        vv = varga_vishwa(planet=planet, sign=sign, sign_degree=sign_deg)
        contrib = (weight * float(vv["points"])) / 20.0
        total += contrib
        contributions.append(
            {
                "varga": varga,
                "sign": sign,
                "weight": weight,
                "varga_vishwa": vv["points"],
                "basis": vv["basis"],
                "sign_lord": vv["sign_lord"],
                "contribution": round(contrib, 6),
            }
        )
    return {
        "planet": planet,
        "scheme": "shodashavarga",
        "vimshopaka": round(total, 6),
        "max": 20.0,
        "contributions": contributions,
        "band_note": "BPHS interpretive bands deferred — verification metric only",
    }


def compute_vimshopaka_pack(chart: dict[str, Any]) -> dict[str, Any]:
    planets = {p["planet"]: p for p in chart.get("planets") or []}
    rows: list[dict[str, Any]] = []
    for name in CLASSICAL_PLANETS:
        p = planets.get(name)
        if not p:
            continue
        rows.append(compute_planet_vimshopaka(p))

    ranked = sorted(rows, key=lambda r: r["vimshopaka"], reverse=True)
    weight_sum = sum(SHODASHAVARGA_WEIGHTS.values())
    return {
        "variant": VIMSHOPAKA_VARIANT,
        "scheme": "shodashavarga",
        "unit": "vimshopaka_points",
        "max": 20.0,
        "weight_sum": weight_sum,
        "weights": dict(SHODASHAVARGA_WEIGHTS),
        "planets": rows,
        "summary": {
            "planet_count": len(rows),
            "strongest": ranked[0]["planet"] if ranked else None,
            "strongest_vimshopaka": ranked[0]["vimshopaka"] if ranked else None,
            "weakest": ranked[-1]["planet"] if ranked else None,
            "weakest_vimshopaka": ranked[-1]["vimshopaka"] if ranked else None,
        },
        "notes": [
            "Candidate Shodashavarga Vimshopaka — permanent friendship only.",
            "Great friend/enemy (temporal) and Shadvarga/Saptavarga/Dasavarga schemes deferred.",
            "Do not treat scores as predictive verdicts.",
        ],
    }


__all__ = [
    "CLASSICAL_PLANETS",
    "SHODASHAVARGA_WEIGHTS",
    "VIMSHOPAKA_VARIANT",
    "compute_planet_vimshopaka",
    "compute_vimshopaka_pack",
    "permanent_relation",
    "varga_vishwa",
]

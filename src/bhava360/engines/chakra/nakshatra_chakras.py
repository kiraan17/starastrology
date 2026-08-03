"""Tara Chakra, Kota Chakra, Sarvatobhadra scaffolds — Candidate (TEC-082..083)."""

from __future__ import annotations

from typing import Any

from bhava360.kernel.derived import nakshatra_from_longitude
from bhava360.kernel.models import NAKSHATRAS_VEDASTRO
from bhava360.timing.bala import TARA_AUSPICIOUS, TARA_NAMES, compute_tara_bala, nakshatra_index

TARA_CHAKRA_VARIANT = "tara_chakra_candidate_v1"
KOTA_CHAKRA_VARIANT = "kota_chakra_candidate_v1"
SBC_VARIANT = "sarvatobhadra_rim_candidate_v1"

# 27 nakshatras → 8 directions (Candidate layout; Abhijit omitted in this thin slice).
# Counts: E4 SE3 S4 SW3 W4 NW3 N3 NE3 = 27
KOTA_DIRECTION_COUNTS: tuple[tuple[str, int], ...] = (
    ("east", 4),
    ("southeast", 3),
    ("south", 4),
    ("southwest", 3),
    ("west", 4),
    ("northwest", 3),
    ("north", 3),
    ("northeast", 3),
)


def _nak_name(idx0: int) -> str:
    return NAKSHATRAS_VEDASTRO[idx0 % 27]


def build_tara_chakra(
    *,
    moon_longitude: float,
    planet_longitudes: dict[str, float],
) -> dict[str, Any]:
    """Nine-spoke Tara Chakra from Moon nakshatra (reuses Tara Bala cycle)."""
    moon_idx = nakshatra_index(moon_longitude)
    spokes: list[dict[str, Any]] = []
    for tara_num, tara_name in enumerate(TARA_NAMES, start=1):
        spokes.append(
            {
                "tara_number": tara_num,
                "tara": tara_name,
                "auspicious": TARA_AUSPICIOUS[tara_name],
                "occupants": [],
            }
        )

    planet_rows: list[dict[str, Any]] = []
    for planet, lon in planet_longitudes.items():
        tgt = nakshatra_index(lon)
        tara = compute_tara_bala(
            reference_nakshatra_index=moon_idx,
            target_nakshatra_index=tgt,
        )
        name, pada, label = nakshatra_from_longitude(lon)
        row = {
            "planet": planet,
            "nakshatra": name,
            "pada": pada,
            "nakshatra_label": label,
            "tara_number": tara["tara_number"],
            "tara": tara["tara"],
            "auspicious": tara["auspicious"],
        }
        planet_rows.append(row)
        spokes[tara["tara_number"] - 1]["occupants"].append(planet)

    return {
        "variant": TARA_CHAKRA_VARIANT,
        "reference": {
            "body": "Moon",
            "nakshatra_index": moon_idx + 1,
            "nakshatra": _nak_name(moon_idx),
        },
        "spokes": spokes,
        "planets": planet_rows,
        "notes": [
            "Tara Chakra spokes = 9-fold cycle from Moon nakshatra (same as Tara Bala).",
            "Interpretive timing verdicts deferred.",
        ],
    }


def _kota_slots() -> list[dict[str, Any]]:
    slots: list[dict[str, Any]] = []
    idx = 0
    for direction, count in KOTA_DIRECTION_COUNTS:
        for pos in range(count):
            slots.append(
                {
                    "index": idx + 1,
                    "direction": direction,
                    "position_in_direction": pos + 1,
                    "nakshatra": _nak_name(idx),
                    "nakshatra_index": idx + 1,
                    "occupants": [],
                }
            )
            idx += 1
    return slots


def build_kota_chakra(*, planet_longitudes: dict[str, float]) -> dict[str, Any]:
    """
    Kota (fort) Chakra: 27 nakshatras in 8 directions (Candidate layout).

    Abhijit and classical attack/defense verdicts deferred.
    """
    slots = _kota_slots()
    by_nak = {s["nakshatra_index"] - 1: s for s in slots}
    planet_rows: list[dict[str, Any]] = []
    for planet, lon in planet_longitudes.items():
        idx = nakshatra_index(lon)
        slot = by_nak[idx]
        name, pada, label = nakshatra_from_longitude(lon)
        planet_rows.append(
            {
                "planet": planet,
                "nakshatra": name,
                "pada": pada,
                "nakshatra_label": label,
                "direction": slot["direction"],
                "kota_index": slot["index"],
            }
        )
        slot["occupants"].append(planet)

    by_direction: dict[str, list[dict[str, Any]]] = {}
    for direction, _count in KOTA_DIRECTION_COUNTS:
        by_direction[direction] = [s for s in slots if s["direction"] == direction]

    return {
        "variant": KOTA_CHAKRA_VARIANT,
        "layout": "8_direction_27_nakshatra_candidate_v1",
        "slots": slots,
        "by_direction": by_direction,
        "planets": planet_rows,
        "notes": [
            "Candidate Kota layout without Abhijit; direction counts E4/SE3/S4/SW3/W4/NW3/N3/NE3.",
            "No attack/defense or travel verdicts in this scaffold.",
        ],
    }


def build_sarvatobhadra_rim(*, planet_longitudes: dict[str, float]) -> dict[str, Any]:
    """
    Sarvatobhadra thin scaffold: planets placed on nakshatra rim cells.

    Full 9×9 alphabet/tithi/rashi grid and Vedha rules deferred (Source Needed).
    """
    rim: list[dict[str, Any]] = []
    for i, name in enumerate(NAKSHATRAS_VEDASTRO):
        rim.append(
            {
                "nakshatra_index": i + 1,
                "nakshatra": name,
                # Candidate rim coordinates on a square perimeter (0..26).
                "rim_index": i,
                "occupants": [],
            }
        )

    planet_rows: list[dict[str, Any]] = []
    for planet, lon in planet_longitudes.items():
        idx = nakshatra_index(lon)
        nname, pada, label = nakshatra_from_longitude(lon)
        planet_rows.append(
            {
                "planet": planet,
                "nakshatra": nname,
                "pada": pada,
                "nakshatra_label": label,
                "rim_index": idx,
                "nakshatra_index": idx + 1,
            }
        )
        rim[idx]["occupants"].append(planet)

    return {
        "variant": SBC_VARIANT,
        "status": "Candidate",
        "rim": rim,
        "planets": planet_rows,
        "vedha": {
            "status": "deferred",
            "note": "Front/side/back Vedha rule pack requires Approved classical edition (TEC-082).",
        },
        "notes": [
            "Rim placement only — full Sarvatobhadra 9×9 grid deferred.",
            "No Vedha obstruction verdicts in this scaffold.",
        ],
    }


def build_nakshatra_chakra_pack(
    *,
    moon_longitude: float,
    planet_longitudes: dict[str, float],
) -> dict[str, Any]:
    return {
        "tara_chakra": build_tara_chakra(
            moon_longitude=moon_longitude,
            planet_longitudes=planet_longitudes,
        ),
        "kota_chakra": build_kota_chakra(planet_longitudes=planet_longitudes),
        "sarvatobhadra": build_sarvatobhadra_rim(planet_longitudes=planet_longitudes),
    }


__all__ = [
    "KOTA_CHAKRA_VARIANT",
    "SBC_VARIANT",
    "TARA_CHAKRA_VARIANT",
    "build_kota_chakra",
    "build_nakshatra_chakra_pack",
    "build_sarvatobhadra_rim",
    "build_tara_chakra",
]

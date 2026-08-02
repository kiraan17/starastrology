"""Panchaka and Bhadra classifiers — Candidate thin slice (TEC-074)."""

from __future__ import annotations

from typing import Any

from bhava360.kernel.derived import NAKSHATRA_SPAN, normalize_longitude, sign_from_longitude
from bhava360.kernel.models import NAKSHATRAS_VEDASTRO, SIGNS

PANCHAKA_VARIANT = "panchaka_bhadra_candidate_v1"

# Moon longitude window: Dhanishta pada 3 (300°) through end of Revati (360°).
PANCHAK_MOON_START_DEG = 300.0
PANCHAK_MOON_END_DEG = 360.0

# Remainder → type for (tithi + vara + nakshatra + lagna) % 9 (Candidate).
PANCHAKA_REMAINDER_TYPES: dict[int, str] = {
    1: "Mrityu",
    2: "Agni",
    4: "Raja",
    6: "Chora",
    8: "Roga",
}
PANCHAKA_RAHITA_REMAINDERS = frozenset({0, 3, 5, 7})

# Structural labels for the five Moon-Panchak nakshatra spans (Candidate).
PANCHAK_SEGMENTS: tuple[tuple[str, float, float], ...] = (
    ("Dhanishta", 300.0, 22 * NAKSHATRA_SPAN + NAKSHATRA_SPAN),  # padas 3–4 → end
    ("Satabhisha", 23 * NAKSHATRA_SPAN, 24 * NAKSHATRA_SPAN),
    ("Poorvabhadra", 24 * NAKSHATRA_SPAN, 25 * NAKSHATRA_SPAN),
    ("Uttarabhadra", 25 * NAKSHATRA_SPAN, 26 * NAKSHATRA_SPAN),
    ("Revathi", 26 * NAKSHATRA_SPAN, 360.0),
)

# Classical activity categories often deferred during Moon Panchak (labels only).
PANCHAK_DEFERRED_ACTIVITY_LABELS: tuple[str, ...] = (
    "southward_travel",
    "fuel_or_grass_collection",
    "cot_or_bed_making",
    "roof_or_thatching_work",
    "cremation_related_rites",
)


def moon_panchak_window(moon_lon_sidereal: float) -> dict[str, Any]:
    """Detect Moon in the last-60° Panchak window (Candidate)."""
    lon = normalize_longitude(moon_lon_sidereal)
    active = PANCHAK_MOON_START_DEG <= lon < PANCHAK_MOON_END_DEG
    segment = None
    if active:
        for name, start, end in PANCHAK_SEGMENTS:
            # Dhanishta segment starts mid-nakshatra at 300°.
            lo = max(start, PANCHAK_MOON_START_DEG) if name == "Dhanishta" else start
            if lo <= lon < end:
                segment = name
                break
        if segment is None:
            # Boundary safety: clamp to last segment.
            segment = "Revathi"
    nak_idx = int(lon // NAKSHATRA_SPAN) % 27
    return {
        "active": active,
        "moon_longitude_sidereal_deg": lon,
        "nakshatra": NAKSHATRAS_VEDASTRO[nak_idx],
        "nakshatra_index": nak_idx + 1,
        "segment": segment,
        "window": {
            "start_deg": PANCHAK_MOON_START_DEG,
            "end_deg": PANCHAK_MOON_END_DEG,
            "basis": "moon_lon_sidereal_dhanishta_pada3_through_revathi",
        },
        "deferred_activity_labels": list(PANCHAK_DEFERRED_ACTIVITY_LABELS) if active else [],
    }


def panchaka_rahita(
    *,
    tithi_index: int,
    vara_index: int,
    nakshatra_index: int,
    lagna_sign_index: int,
) -> dict[str, Any]:
    """
    Instant Panchaka Rahita filter.

    sum(tithi, vara, nakshatra, lagna) % 9 — remainders 1/2/4/6/8 afflicted.
    Indices are 1-based classical counts (Candidate).
    """
    total = int(tithi_index) + int(vara_index) + int(nakshatra_index) + int(lagna_sign_index)
    rem = total % 9
    if rem in PANCHAKA_RAHITA_REMAINDERS:
        return {
            "rahita": True,
            "afflicted": False,
            "remainder": rem,
            "type": None,
            "label": "Panchaka Rahita",
            "sum": total,
            "inputs": {
                "tithi_index": int(tithi_index),
                "vara_index": int(vara_index),
                "nakshatra_index": int(nakshatra_index),
                "lagna_sign_index": int(lagna_sign_index),
            },
        }
    ptype = PANCHAKA_REMAINDER_TYPES[rem]
    return {
        "rahita": False,
        "afflicted": True,
        "remainder": rem,
        "type": ptype,
        "label": f"{ptype} Panchaka",
        "sum": total,
        "inputs": {
            "tithi_index": int(tithi_index),
            "vara_index": int(vara_index),
            "nakshatra_index": int(nakshatra_index),
            "lagna_sign_index": int(lagna_sign_index),
        },
    }


def bhadra_from_karana(karana_name: str | None) -> dict[str, Any]:
    """Bhadra = Vishti karana active (Candidate structural flag)."""
    name = (karana_name or "").strip()
    active = name == "Vishti"
    return {
        "active": active,
        "karana": name or None,
        "label": "Bhadra (Vishti)" if active else "not Bhadra",
        "basis": "vishti_karana",
    }


def lagna_sign_index_from_longitude(lagna_lon_sidereal: float) -> tuple[int, str]:
    sign, _ = sign_from_longitude(lagna_lon_sidereal)
    idx = SIGNS.index(sign) + 1
    return idx, sign


def evaluate_panchaka_bhadra(
    *,
    moon_lon_sidereal: float,
    lagna_lon_sidereal: float,
    tithi_index: int,
    vara_index: int,
    nakshatra_index: int,
    karana_name: str | None,
) -> dict[str, Any]:
    """Combine Moon Panchak, Rahita remainder, and Bhadra flags."""
    moon_win = moon_panchak_window(moon_lon_sidereal)
    lagna_idx, lagna_sign = lagna_sign_index_from_longitude(lagna_lon_sidereal)
    rahita = panchaka_rahita(
        tithi_index=tithi_index,
        vara_index=vara_index,
        nakshatra_index=nakshatra_index,
        lagna_sign_index=lagna_idx,
    )
    bhadra = bhadra_from_karana(karana_name)

    caution_flags: list[str] = []
    if moon_win["active"]:
        caution_flags.append("moon_panchak")
    if rahita["afflicted"]:
        caution_flags.append(f"panchaka_{str(rahita['type']).lower()}")
    if bhadra["active"]:
        caution_flags.append("bhadra_vishti")

    return {
        "variant": PANCHAKA_VARIANT,
        "moon_panchak": moon_win,
        "panchaka_rahita": rahita,
        "bhadra": bhadra,
        "lagna_sign": lagna_sign,
        "lagna_sign_index": lagna_idx,
        "summary": {
            "moon_panchak_active": moon_win["active"],
            "moon_panchak_segment": moon_win["segment"],
            "panchaka_rahita": rahita["rahita"],
            "panchaka_type": rahita["type"],
            "panchaka_label": rahita["label"],
            "bhadra_active": bhadra["active"],
            "caution_flag_count": len(caution_flags),
            "caution_flags": caution_flags,
        },
        "notes": [
            "Candidate structural classifiers only — not predictive advice.",
            "Moon Panchak uses sidereal Moon in [300°, 360°).",
            "Rahita uses (tithi+vara+nakshatra+lagna) mod 9.",
            "Bhadra flagged when Karana is Vishti.",
            "Day-segment sweep across lagna changes deferred.",
        ],
    }


__all__ = [
    "PANCHAKA_VARIANT",
    "PANCHAK_MOON_START_DEG",
    "bhadra_from_karana",
    "evaluate_panchaka_bhadra",
    "lagna_sign_index_from_longitude",
    "moon_panchak_window",
    "panchaka_rahita",
]

"""Gandanta, Chandra Kriya, Baladi Avastha — Candidate classification (TEC-084..085)."""

from __future__ import annotations

from typing import Any

from bhava360.kernel.derived import (
    NAKSHATRA_SPAN,
    PADA_SPAN,
    nakshatra_from_longitude,
    normalize_longitude,
    sign_from_longitude,
)
from bhava360.kernel.models import NAKSHATRAS_VEDASTRO, SIGNS

GANDANTA_VARIANT = "gandanta_pada_candidate_v1"
KRIYA_VARIANT = "chandra_kriya_candidate_v1"
AVASTHA_VARIANT = "baladi_avastha_candidate_v1"
VELA_VARIANT = "chandra_vela_36_candidate_v1"

# Water nakshatras ending at fire junctions (0-based): Aslesha, Jyesta, Revathi
GANDANTA_END_NAK_IDX = frozenset({8, 17, 26})
# Fire nakshatras starting after water junctions: Aswini, Makha, Moola
GANDANTA_START_NAK_IDX = frozenset({0, 9, 18})

# Rasi gandanta: water signs (Cancer=3, Scorpio=7, Pisces=11) last pada-span;
# fire signs (Aries=0, Leo=4, Sagittarius=8) first pada-span.
GANDANTA_WATER_SIGNS = frozenset({3, 7, 11})
GANDANTA_FIRE_SIGNS = frozenset({0, 4, 8})

# Candidate 60 Chandra Kriya labels (index authority; names pending SRC freeze).
CHANDRA_KRIYA_NAMES: tuple[str, ...] = (
    "Nivritti",
    "Prasa",
    "Prasthana",
    "Anavastha",
    "Chesta",
    "Agama",
    "Vyaya",
    "Budha",
    "Gamana",
    "Bhojana",
    "Nrityalipsa",
    "Kautuka",
    "Nidra",
    "Jalavarana",
    "Sneha",
    "Dwesha",
    "Kopa",
    "Dana",
    "Shayana",
    "Bhoga",
    "Lajja",
    "Shoka",
    "Dhairya",
    "Kreeda",
    "Shuchi",
    "Mati",
    "Rati",
    "Shubha",
    "Bhaya",
    "Prarthana",
    "Kriti",
    "Kshama",
    "Lobha",
    "Kama",
    "Vani",
    "Shranta",
    "Nasha",
    "Arti",
    "Japa",
    "Dana_II",
    "Shuddhi",
    "Adhvan",
    "Kshudha",
    "Trisha",
    "Kala",
    "Yuddha",
    "Ahara",
    "Pralaya",
    "Madira",
    "Rati_II",
    "Kreeda_II",
    "Shayana_II",
    "Bhogalipsa",
    "Garva",
    "Dana_III",
    "Madira_II",
    "Nasha_II",
    "Ahara_II",
    "Yuddha_II",
    "Kala_II",
)

BALADI_NAMES: tuple[str, ...] = ("Bala", "Kumara", "Yuva", "Vriddha", "Mrita")


def classify_gandanta(longitude_sidereal_deg: float) -> dict[str, Any]:
    """Detect nakshatra-pada and rasi Gandanta (Candidate)."""
    lon = normalize_longitude(longitude_sidereal_deg)
    nak_name, pada, label = nakshatra_from_longitude(lon)
    nak_idx = int(lon // NAKSHATRA_SPAN) % 27
    sign, sign_deg = sign_from_longitude(lon)
    sign_idx = SIGNS.index(sign)

    nak_gandanta = (nak_idx in GANDANTA_END_NAK_IDX and pada == 4) or (
        nak_idx in GANDANTA_START_NAK_IDX and pada == 1
    )
    rasi_gandanta = (
        sign_idx in GANDANTA_WATER_SIGNS and sign_deg >= (30.0 - PADA_SPAN)
    ) or (sign_idx in GANDANTA_FIRE_SIGNS and sign_deg < PADA_SPAN)

    junction = None
    if nak_idx in {26, 0} or sign_idx in {11, 0}:
        junction = "Pisces-Aries"
    elif nak_idx in {8, 9} or sign_idx in {3, 4}:
        junction = "Cancer-Leo"
    elif nak_idx in {17, 18} or sign_idx in {7, 8}:
        junction = "Scorpio-Sagittarius"

    active = bool(nak_gandanta or rasi_gandanta)
    return {
        "active": active,
        "nakshatra_gandanta": nak_gandanta,
        "rasi_gandanta": rasi_gandanta,
        "junction": junction if active else None,
        "nakshatra": nak_name,
        "pada": pada,
        "nakshatra_label": label,
        "sign": sign,
        "sign_degree": sign_deg,
        "variant": GANDANTA_VARIANT,
        "notes": [
            "Nakshatra Gandanta: pada 4 of Aslesha/Jyesta/Revathi or pada 1 of Aswini/Makha/Moola.",
            "Rasi Gandanta: last/first 3°20' at water→fire sign junctions.",
        ],
    }


def classify_chandra_kriya(moon_longitude: float) -> dict[str, Any]:
    """60 Chandra Kriyas of 6° each from 0° Aries (Candidate names)."""
    lon = normalize_longitude(moon_longitude)
    idx0 = min(int(lon // 6.0), 59)
    start = idx0 * 6.0
    return {
        "index": idx0 + 1,
        "name": CHANDRA_KRIYA_NAMES[idx0],
        "span_start_deg": start,
        "span_end_deg": start + 6.0,
        "fraction_elapsed": (lon - start) / 6.0,
        "variant": KRIYA_VARIANT,
        "notes": [
            "Index is authoritative (6° zones from 0° sidereal).",
            "Names are Candidate spellings pending classical edition freeze.",
        ],
    }


def classify_chandra_vela(moon_longitude: float) -> dict[str, Any]:
    """36 Chandra Velas of 10° each (Candidate index-only thin slice)."""
    lon = normalize_longitude(moon_longitude)
    idx0 = min(int(lon // 10.0), 35)
    start = idx0 * 10.0
    return {
        "index": idx0 + 1,
        "count": 36,
        "span_deg": 10.0,
        "span_start_deg": start,
        "span_end_deg": start + 10.0,
        "fraction_elapsed": (lon - start) / 10.0,
        "variant": VELA_VARIANT,
        "notes": ["Candidate 36×10° partition; named Vela table deferred."],
    }


def classify_baladi_avastha(
    *,
    longitude_sidereal_deg: float,
    planet: str | None = None,
) -> dict[str, Any]:
    """Baladi Avastha from degree-in-sign (odd forward / even reverse)."""
    sign, sign_deg = sign_from_longitude(longitude_sidereal_deg)
    sign_idx = SIGNS.index(sign)
    odd = sign_idx % 2 == 0  # Aries=0 odd in Vedic counting (1-based odd)
    # Vedic: Aries, Gemini, Leo... are odd signs (1,3,5...) → sign_idx 0,2,4 even in 0-based
    band = min(int(sign_deg // 6.0), 4)
    if odd:
        name = BALADI_NAMES[band]
    else:
        name = BALADI_NAMES[4 - band]
    return {
        "planet": planet,
        "sign": sign,
        "sign_degree": sign_deg,
        "avastha": name,
        "band_index": band + 1,
        "odd_sign": odd,
        "variant": AVASTHA_VARIANT,
    }


def classify_point(longitude_sidereal_deg: float, *, label: str) -> dict[str, Any]:
    gandanta = classify_gandanta(longitude_sidereal_deg)
    avastha = classify_baladi_avastha(
        longitude_sidereal_deg=longitude_sidereal_deg,
        planet=label,
    )
    nak, pada, nak_label = nakshatra_from_longitude(longitude_sidereal_deg)
    return {
        "body": label,
        "longitude_sidereal_deg": normalize_longitude(longitude_sidereal_deg),
        "nakshatra": nak,
        "pada": pada,
        "nakshatra_label": nak_label,
        "gandanta": gandanta,
        "baladi_avastha": avastha,
    }


__all__ = [
    "AVASTHA_VARIANT",
    "CHANDRA_KRIYA_NAMES",
    "GANDANTA_VARIANT",
    "KRIYA_VARIANT",
    "VELA_VARIANT",
    "classify_baladi_avastha",
    "classify_chandra_kriya",
    "classify_chandra_vela",
    "classify_gandanta",
    "classify_point",
]

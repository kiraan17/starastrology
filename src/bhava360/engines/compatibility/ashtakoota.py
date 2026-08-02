"""Ashtakoota (8-fold) compatibility — Candidate (TEC-094)."""

from __future__ import annotations

from typing import Any

from bhava360.chart.dignity import sign_lord
from bhava360.kernel.derived import nakshatra_from_longitude, sign_from_longitude
from bhava360.kernel.models import SIGNS
from bhava360.timing.bala import compute_tara_bala, nakshatra_index

KUTA_VARIANT = "ashtakoota_candidate_v1"
MAX_TOTAL = 36.0

# Moon-sign Varna (Candidate).
VARNA_BY_SIGN: dict[str, str] = {
    "Cancer": "Brahmin",
    "Scorpio": "Brahmin",
    "Pisces": "Brahmin",
    "Aries": "Kshatriya",
    "Leo": "Kshatriya",
    "Sagittarius": "Kshatriya",
    "Taurus": "Vaishya",
    "Virgo": "Vaishya",
    "Capricorn": "Vaishya",
    "Gemini": "Shudra",
    "Libra": "Shudra",
    "Aquarius": "Shudra",
}
VARNA_RANK = {"Brahmin": 4, "Kshatriya": 3, "Vaishya": 2, "Shudra": 1}

# Vashya groups (Candidate simplified classical mapping).
VASHYA_BY_SIGN: dict[str, str] = {
    "Aries": "Chatushpada",
    "Taurus": "Chatushpada",
    "Gemini": "Manava",
    "Cancer": "Jalachara",
    "Leo": "Vanachara",
    "Virgo": "Manava",
    "Libra": "Manava",
    "Scorpio": "Keeta",
    "Sagittarius": "Manava",  # dual; Candidate uses Manava
    "Capricorn": "Jalachara",  # dual first half often Chatushpada — Candidate Jalachara
    "Aquarius": "Manava",
    "Pisces": "Jalachara",
}

# Yoni animals for 27 nakshatras (Candidate classical list).
YONI_BY_NAK: tuple[str, ...] = (
    "Ashwa",
    "Gaja",
    "Mesha",
    "Sarpa",
    "Sarpa",
    "Shwana",
    "Marjara",
    "Mesha",
    "Marjara",
    "Mushaka",
    "Mushaka",
    "Gaja",
    "Mahisha",
    "Vyaghra",
    "Mahisha",
    "Vyaghra",
    "Mriga",
    "Mriga",
    "Shwana",
    "Vanara",
    "Nakula",
    "Vanara",
    "Simha",
    "Ashwa",
    "Simha",
    "Gaja",
    "Gaja",
)

# Hostile yoni pairs (symmetric) — Candidate.
YONI_HOSTILE: frozenset[frozenset[str]] = frozenset(
    {
        frozenset({"Ashwa", "Simha"}),
        frozenset({"Gaja", "Simha"}),
        frozenset({"Gaja", "Nakula"}),
        frozenset({"Mesha", "Vanara"}),
        frozenset({"Sarpa", "Nakula"}),
        frozenset({"Sarpa", "Mriga"}),
        frozenset({"Shwana", "Mriga"}),
        frozenset({"Marjara", "Mushaka"}),
        frozenset({"Marjara", "Mahisha"}),
        frozenset({"Mushaka", "Mahisha"}),
        frozenset({"Vyaghra", "Mahisha"}),
        frozenset({"Vyaghra", "Gaja"}),
        frozenset({"Vanara", "Mesha"}),
        frozenset({"Simha", "Ashwa"}),
    }
)

# Gana by nakshatra (Candidate).
GANA_BY_NAK: tuple[str, ...] = (
    "Deva",
    "Manushya",
    "Rakshasa",
    "Manushya",
    "Deva",
    "Manushya",
    "Deva",
    "Deva",
    "Rakshasa",
    "Rakshasa",
    "Manushya",
    "Manushya",
    "Deva",
    "Rakshasa",
    "Deva",
    "Rakshasa",
    "Deva",
    "Rakshasa",
    "Rakshasa",
    "Manushya",
    "Manushya",
    "Deva",
    "Rakshasa",
    "Rakshasa",
    "Manushya",
    "Manushya",
    "Deva",
)

# Nadi by nakshatra (Candidate Adi/Madhya/Antya cycle).
NADI_BY_NAK: tuple[str, ...] = (
    "Adi",
    "Madhya",
    "Antya",
    "Adi",
    "Madhya",
    "Antya",
    "Adi",
    "Madhya",
    "Antya",
    "Adi",
    "Madhya",
    "Antya",
    "Adi",
    "Madhya",
    "Antya",
    "Adi",
    "Madhya",
    "Antya",
    "Adi",
    "Madhya",
    "Antya",
    "Adi",
    "Madhya",
    "Antya",
    "Adi",
    "Madhya",
    "Antya",
)

# Permanent friendship for Graha Maitri (Candidate simplified).
FRIENDS: dict[str, frozenset[str]] = {
    "Sun": frozenset({"Moon", "Mars", "Jupiter"}),
    "Moon": frozenset({"Sun", "Mercury"}),
    "Mars": frozenset({"Sun", "Moon", "Jupiter"}),
    "Mercury": frozenset({"Sun", "Venus"}),
    "Jupiter": frozenset({"Sun", "Moon", "Mars"}),
    "Venus": frozenset({"Mercury", "Saturn"}),
    "Saturn": frozenset({"Mercury", "Venus"}),
}
NEUTRALS: dict[str, frozenset[str]] = {
    "Sun": frozenset({"Mercury"}),
    "Moon": frozenset({"Mars", "Jupiter", "Venus", "Saturn"}),
    "Mars": frozenset({"Venus", "Saturn"}),
    "Mercury": frozenset({"Mars", "Jupiter", "Saturn"}),
    "Jupiter": frozenset({"Saturn"}),
    "Venus": frozenset({"Mars", "Jupiter"}),
    "Saturn": frozenset({"Jupiter"}),
}


def _sign_diff(a: str, b: str) -> int:
    """Count of signs from a to b inclusive of start as 1."""
    return ((SIGNS.index(b) - SIGNS.index(a)) % 12) + 1


def score_varna(*, boy_sign: str, girl_sign: str) -> dict[str, Any]:
    b, g = VARNA_BY_SIGN[boy_sign], VARNA_BY_SIGN[girl_sign]
    points = 1.0 if VARNA_RANK[b] >= VARNA_RANK[g] else 0.0
    return {"kuta": "Varna", "max": 1.0, "points": points, "boy": b, "girl": g}


def score_vashya(*, boy_sign: str, girl_sign: str) -> dict[str, Any]:
    b, g = VASHYA_BY_SIGN[boy_sign], VASHYA_BY_SIGN[girl_sign]
    if b == g:
        points = 2.0
    elif {b, g} == {"Manava", "Chatushpada"}:
        points = 1.0
    elif {b, g} <= {"Jalachara", "Keeta", "Vanachara"} and b != g:
        points = 0.5
    else:
        points = 1.0 if b != g else 2.0
        # Candidate simplification: different groups default 1 except known weak pairs
        if frozenset({b, g}) in {
            frozenset({"Manava", "Vanachara"}),
            frozenset({"Chatushpada", "Keeta"}),
        }:
            points = 0.0
    return {"kuta": "Vashya", "max": 2.0, "points": points, "boy": b, "girl": g}


def score_tara(*, boy_nak_idx: int, girl_nak_idx: int) -> dict[str, Any]:
    # Classical: count from girl to boy
    tara = compute_tara_bala(
        reference_nakshatra_index=girl_nak_idx,
        target_nakshatra_index=boy_nak_idx,
    )
    # Common rule: Vipat(3), Pratyak(5), Naidhana(7) = 0; others = 3
    points = 3.0 if tara["tara_number"] not in {3, 5, 7} else 0.0
    return {
        "kuta": "Tara",
        "max": 3.0,
        "points": points,
        "tara": tara["tara"],
        "tara_number": tara["tara_number"],
    }


def score_yoni(*, boy_nak_idx: int, girl_nak_idx: int) -> dict[str, Any]:
    by, gy = YONI_BY_NAK[boy_nak_idx], YONI_BY_NAK[girl_nak_idx]
    if by == gy:
        points = 4.0
    elif frozenset({by, gy}) in YONI_HOSTILE:
        points = 0.0
    else:
        points = 2.0
    return {"kuta": "Yoni", "max": 4.0, "points": points, "boy": by, "girl": gy}


def score_graha_maitri(*, boy_sign: str, girl_sign: str) -> dict[str, Any]:
    bl = sign_lord(boy_sign)
    gl = sign_lord(girl_sign)
    assert bl is not None and gl is not None
    b, g = bl.value, gl.value
    if b == g:
        points = 5.0
    elif g in FRIENDS.get(b, ()) and b in FRIENDS.get(g, ()):
        points = 5.0
    elif g in FRIENDS.get(b, ()) or b in FRIENDS.get(g, ()):
        points = 4.0
    elif g in NEUTRALS.get(b, ()) or b in NEUTRALS.get(g, ()):
        points = 3.0
    else:
        points = 0.0
    return {
        "kuta": "GrahaMaitri",
        "max": 5.0,
        "points": points,
        "boy_lord": b,
        "girl_lord": g,
    }


def score_gana(*, boy_nak_idx: int, girl_nak_idx: int) -> dict[str, Any]:
    bg, gg = GANA_BY_NAK[boy_nak_idx], GANA_BY_NAK[girl_nak_idx]
    if bg == gg:
        points = 6.0
    elif {bg, gg} == {"Deva", "Manushya"}:
        points = 6.0
    elif {bg, gg} == {"Manushya", "Rakshasa"}:
        points = 0.0
    elif {bg, gg} == {"Deva", "Rakshasa"}:
        points = 1.0
    else:
        points = 0.0
    return {"kuta": "Gana", "max": 6.0, "points": points, "boy": bg, "girl": gg}


def score_bhakoot(*, boy_sign: str, girl_sign: str) -> dict[str, Any]:
    diff = _sign_diff(girl_sign, boy_sign)
    # Inauspicious: 2/12, 5/9, 6/8 from each other (Candidate classical)
    bad = {2, 5, 6, 8, 9, 12}
    points = 0.0 if diff in bad else 7.0
    return {
        "kuta": "Bhakoot",
        "max": 7.0,
        "points": points,
        "sign_count_girl_to_boy": diff,
    }


def score_nadi(*, boy_nak_idx: int, girl_nak_idx: int) -> dict[str, Any]:
    bn, gn = NADI_BY_NAK[boy_nak_idx], NADI_BY_NAK[girl_nak_idx]
    points = 0.0 if bn == gn else 8.0
    return {"kuta": "Nadi", "max": 8.0, "points": points, "boy": bn, "girl": gn}


def compute_ashtakoota(
    *,
    boy_moon_longitude: float,
    girl_moon_longitude: float,
) -> dict[str, Any]:
    """North-Indian Ashtakoota from both Moon longitudes (Candidate)."""
    b_sign, _ = sign_from_longitude(boy_moon_longitude)
    g_sign, _ = sign_from_longitude(girl_moon_longitude)
    b_nak, b_pada, b_label = nakshatra_from_longitude(boy_moon_longitude)
    g_nak, g_pada, g_label = nakshatra_from_longitude(girl_moon_longitude)
    b_idx = nakshatra_index(boy_moon_longitude)
    g_idx = nakshatra_index(girl_moon_longitude)

    parts = [
        score_varna(boy_sign=b_sign, girl_sign=g_sign),
        score_vashya(boy_sign=b_sign, girl_sign=g_sign),
        score_tara(boy_nak_idx=b_idx, girl_nak_idx=g_idx),
        score_yoni(boy_nak_idx=b_idx, girl_nak_idx=g_idx),
        score_graha_maitri(boy_sign=b_sign, girl_sign=g_sign),
        score_gana(boy_nak_idx=b_idx, girl_nak_idx=g_idx),
        score_bhakoot(boy_sign=b_sign, girl_sign=g_sign),
        score_nadi(boy_nak_idx=b_idx, girl_nak_idx=g_idx),
    ]
    total = sum(float(p["points"]) for p in parts)
    return {
        "variant": KUTA_VARIANT,
        "system": "ashtakoota",
        "max_total": MAX_TOTAL,
        "total": total,
        "percentage": round(100.0 * total / MAX_TOTAL, 4),
        "kutas": parts,
        "boy": {
            "moon_longitude_sidereal_deg": boy_moon_longitude,
            "sign": b_sign,
            "nakshatra": b_nak,
            "pada": b_pada,
            "nakshatra_label": b_label,
        },
        "girl": {
            "moon_longitude_sidereal_deg": girl_moon_longitude,
            "sign": g_sign,
            "nakshatra": g_nak,
            "pada": g_pada,
            "nakshatra_label": g_label,
        },
        "notes": [
            "Candidate North-Indian Ashtakoota point tables.",
            "Dosha interpretation / exceptions (e.g. Nadi exceptions) deferred.",
            "Not a legal/medical/relationship-advice verdict — score only.",
        ],
    }


__all__ = ["KUTA_VARIANT", "MAX_TOTAL", "compute_ashtakoota"]

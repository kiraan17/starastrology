"""Numerology number helpers — Candidate mantra-shastra thin slice (TEC-092)."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

NUMEROLOGY_VARIANT = "numerology_mantra_shastra_candidate_v1"

# Chaldean letter values (Candidate). Digit 9 is unused in classical Chaldean.
CHALDEAN_LETTER_VALUE: dict[str, int] = {
    "A": 1,
    "I": 1,
    "J": 1,
    "Q": 1,
    "Y": 1,
    "B": 2,
    "K": 2,
    "R": 2,
    "C": 3,
    "G": 3,
    "L": 3,
    "S": 3,
    "D": 4,
    "M": 4,
    "T": 4,
    "E": 5,
    "H": 5,
    "N": 5,
    "X": 5,
    "U": 6,
    "V": 6,
    "W": 6,
    "O": 7,
    "Z": 7,
    "F": 8,
    "P": 8,
}

# Vedic/Chaldean number → planet (Candidate classical mapping).
PLANET_BY_NUMBER: dict[int, str] = {
    1: "Sun",
    2: "Moon",
    3: "Jupiter",
    4: "Rahu",
    5: "Mercury",
    6: "Venus",
    7: "Ketu",
    8: "Saturn",
    9: "Mars",
}


def reduce_to_single_digit(n: int) -> int:
    """Digital root in 1–9 (multiples of 9 → 9). Master/compound retention deferred."""
    if n <= 0:
        raise ValueError("numerology reduction requires a positive integer")
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n


def birth_number(day: int) -> dict[str, Any]:
    """Birth / psychic number from calendar day of month."""
    if not 1 <= day <= 31:
        raise ValueError(f"day must be 1–31, got {day}")
    value = reduce_to_single_digit(day)
    return {
        "kind": "birth_number",
        "raw": day,
        "value": value,
        "ruling_planet": PLANET_BY_NUMBER[value],
    }


def destiny_number(year: int, month: int, day: int) -> dict[str, Any]:
    """Destiny number from full civil date (day + month + year), reduced 1–9."""
    if not 1 <= month <= 12:
        raise ValueError(f"month must be 1–12, got {month}")
    if not 1 <= day <= 31:
        raise ValueError(f"day must be 1–31, got {day}")
    if year < 1:
        raise ValueError(f"year must be positive, got {year}")
    raw = day + month + year
    value = reduce_to_single_digit(raw)
    return {
        "kind": "destiny_number",
        "raw": raw,
        "components": {"day": day, "month": month, "year": year},
        "value": value,
        "ruling_planet": PLANET_BY_NUMBER[value],
    }


def name_number_chaldean(name: str) -> dict[str, Any]:
    """
    Chaldean name number from Latin letters only.

    Non-letters are ignored; empty after filter raises.
    """
    letters: list[dict[str, Any]] = []
    total = 0
    for ch in name.upper():
        if not ch.isalpha():
            continue
        if ch not in CHALDEAN_LETTER_VALUE:
            raise ValueError(f"unsupported letter for Chaldean map: {ch!r}")
        val = CHALDEAN_LETTER_VALUE[ch]
        letters.append({"letter": ch, "value": val})
        total += val
    if not letters:
        raise ValueError("name must contain at least one A–Z letter")
    value = reduce_to_single_digit(total)
    return {
        "kind": "name_number",
        "system": "chaldean_candidate_v1",
        "input_name": name,
        "letters": letters,
        "raw": total,
        "value": value,
        "ruling_planet": PLANET_BY_NUMBER[value],
    }


def compute_numerology_profile(
    *,
    birth: date | datetime,
    name: str | None = None,
) -> dict[str, Any]:
    """Assemble birth + destiny (+ optional name) profile."""
    d = birth.date() if isinstance(birth, datetime) else birth
    bn = birth_number(d.day)
    dn = destiny_number(d.year, d.month, d.day)
    profile: dict[str, Any] = {
        "variant": NUMEROLOGY_VARIANT,
        "civil_date": d.isoformat(),
        "birth_number": bn,
        "destiny_number": dn,
        "birth_destiny_aligned": bn["value"] == dn["value"],
        "name_number": None,
        "name_birth_aligned": None,
        "name_destiny_aligned": None,
    }
    if name is not None and str(name).strip():
        nn = name_number_chaldean(str(name).strip())
        profile["name_number"] = nn
        profile["name_birth_aligned"] = nn["value"] == bn["value"]
        profile["name_destiny_aligned"] = nn["value"] == dn["value"]
    return profile


__all__ = [
    "CHALDEAN_LETTER_VALUE",
    "NUMEROLOGY_VARIANT",
    "PLANET_BY_NUMBER",
    "birth_number",
    "compute_numerology_profile",
    "destiny_number",
    "name_number_chaldean",
    "reduce_to_single_digit",
]

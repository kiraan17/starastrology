"""Tara Bala and Chandra Bala (TEC-072 / P16c)."""

from __future__ import annotations

from typing import Any

from bhava360.kernel.derived import nakshatra_from_longitude, normalize_longitude, sign_from_longitude
from bhava360.kernel.models import SIGNS

TARA_NAMES: tuple[str, ...] = (
    "Janma",
    "Sampat",
    "Vipat",
    "Kshema",
    "Pratyak",
    "Sadhana",
    "Naidhana",
    "Mitra",
    "Paramitra",
)

# Classical muhurta grouping: Vipat/Pratyak/Naidhana inauspicious.
TARA_AUSPICIOUS: dict[str, bool] = {
    "Janma": False,  # mixed/sensitive — treat as not freely auspicious
    "Sampat": True,
    "Vipat": False,
    "Kshema": True,
    "Pratyak": False,
    "Sadhana": True,
    "Naidhana": False,
    "Mitra": True,
    "Paramitra": True,
}

# Chandra Bala: count of signs from reference Moon (1=same sign).
# Favorable: 1, 3, 6, 7, 10, 11
CHANDRA_BALA_GOOD: frozenset[int] = frozenset({1, 3, 6, 7, 10, 11})

BALA_VARIANT = "classical_candidate_v1"


def nakshatra_index(longitude_sidereal_deg: float) -> int:
    name, _pada, _label = nakshatra_from_longitude(longitude_sidereal_deg)
    from bhava360.kernel.models import NAKSHATRAS_VEDASTRO

    return NAKSHATRAS_VEDASTRO.index(name)


def sign_index(longitude_sidereal_deg: float) -> int:
    sign, _ = sign_from_longitude(longitude_sidereal_deg)
    return SIGNS.index(sign)


def compute_tara_bala(
    *,
    reference_nakshatra_index: int,
    target_nakshatra_index: int,
) -> dict[str, Any]:
    """Tara counted from reference (usually Moon) nakshatra to target (1..27 → 1..9 cycle)."""
    ref = reference_nakshatra_index % 27
    tgt = target_nakshatra_index % 27
    count = ((tgt - ref) % 27) + 1  # 1..27 inclusive of start
    tara_num = ((count - 1) % 9) + 1
    name = TARA_NAMES[tara_num - 1]
    return {
        "reference_nakshatra_index": ref + 1,
        "target_nakshatra_index": tgt + 1,
        "count_from_reference": count,
        "tara_number": tara_num,
        "tara": name,
        "auspicious": TARA_AUSPICIOUS[name],
        "variant": BALA_VARIANT,
    }


def compute_chandra_bala(
    *,
    reference_sign_index: int,
    target_sign_index: int,
) -> dict[str, Any]:
    """Sign count from reference Moon sign to target sign (1=same)."""
    ref = reference_sign_index % 12
    tgt = target_sign_index % 12
    count = ((tgt - ref) % 12) + 1
    good = count in CHANDRA_BALA_GOOD
    return {
        "reference_sign": SIGNS[ref],
        "target_sign": SIGNS[tgt],
        "count_from_reference": count,
        "bala": "present" if good else "absent",
        "auspicious": good,
        "variant": BALA_VARIANT,
    }


def compute_tara_chandra_pack(
    *,
    moon_longitude_sidereal: float,
    lagna_longitude_sidereal: float,
    planet_longitudes: dict[str, float],
) -> dict[str, Any]:
    """
    Chart-relative Tara/Chandra:
    - Tara of each planet (and Lagna) from Moon nakshatra
    - Chandra Bala of Moon from Lagna
    - Chandra Bala of each planet sign from Moon
    """
    moon_lon = normalize_longitude(moon_longitude_sidereal)
    moon_nak = nakshatra_index(moon_lon)
    moon_sign = sign_index(moon_lon)
    lagna_lon = normalize_longitude(lagna_longitude_sidereal)
    lagna_nak = nakshatra_index(lagna_lon)
    lagna_sign = sign_index(lagna_lon)

    moon_name, moon_pada, moon_label = nakshatra_from_longitude(moon_lon)

    planet_tara = {}
    planet_chandra = {}
    for name, lon in planet_longitudes.items():
        lon_n = normalize_longitude(lon)
        planet_tara[name] = compute_tara_bala(
            reference_nakshatra_index=moon_nak,
            target_nakshatra_index=nakshatra_index(lon_n),
        )
        planet_chandra[name] = compute_chandra_bala(
            reference_sign_index=moon_sign,
            target_sign_index=sign_index(lon_n),
        )

    return {
        "moon": {
            "longitude_sidereal_deg": moon_lon,
            "sign": SIGNS[moon_sign],
            "nakshatra": moon_name,
            "pada": moon_pada,
            "nakshatra_label": moon_label,
        },
        "tara_from_moon": {
            "Lagna": compute_tara_bala(
                reference_nakshatra_index=moon_nak,
                target_nakshatra_index=lagna_nak,
            ),
            **planet_tara,
        },
        "chandra_bala": {
            "moon_from_lagna": compute_chandra_bala(
                reference_sign_index=lagna_sign,
                target_sign_index=moon_sign,
            ),
            "from_moon": {
                "Lagna": compute_chandra_bala(
                    reference_sign_index=moon_sign,
                    target_sign_index=lagna_sign,
                ),
                **planet_chandra,
            },
        },
        "notes": [
            "Tara counted from Moon nakshatra; Vipat/Pratyak/Naidhana (and Janma) marked not freely auspicious.",
            "Chandra Bala present when target is 1/3/6/7/10/11 signs from reference.",
            "moon_from_lagna uses Lagna as reference and Moon as target (common natal strength check).",
        ],
        "variant": BALA_VARIANT,
    }

"""Sudarshana Chakra primitives — Candidate (TEC-080)."""

from __future__ import annotations

from typing import Any

from bhava360.kernel.models import SIGNS

SUDARSHANA_VARIANT = "sudarshana_thin_candidate_v1"
LAGNA_KEYS = ("lagna", "chandra", "surya")


def sign_index(sign: str) -> int:
    return SIGNS.index(sign)


def house_from_reference(*, reference_sign: str, body_sign: str) -> int:
    """Whole-sign house of body counted from reference sign (1–12)."""
    return ((sign_index(body_sign) - sign_index(reference_sign)) % 12) + 1


def sign_for_house(*, reference_sign: str, house: int) -> str:
    """Sign occupying whole-sign house N from reference."""
    h = int(house)
    if not 1 <= h <= 12:
        raise ValueError("house must be 1–12")
    return SIGNS[(sign_index(reference_sign) + h - 1) % 12]


def build_sudarshana_wheel(
    *,
    lagna_sign: str,
    sun_sign: str,
    moon_sign: str,
    planet_signs: dict[str, str],
) -> dict[str, Any]:
    """
    Build Sudarshana Chakra house overlay from Lagna, Chandra, and Surya.

    Deterministic whole-sign geometry only — no interpretive verdicts.
    """
    refs = {
        "lagna": {"key": "lagna", "label": "Lagna", "sign": lagna_sign},
        "chandra": {"key": "chandra", "label": "Chandra Lagna", "sign": moon_sign},
        "surya": {"key": "surya", "label": "Surya Lagna", "sign": sun_sign},
    }

    # Per-planet houses from each reference
    planet_rows: list[dict[str, Any]] = []
    for planet, p_sign in planet_signs.items():
        houses = {
            key: house_from_reference(reference_sign=refs[key]["sign"], body_sign=p_sign)
            for key in LAGNA_KEYS
        }
        planet_rows.append(
            {
                "planet": planet,
                "sign": p_sign,
                "house_from_lagna": houses["lagna"],
                "house_from_chandra": houses["chandra"],
                "house_from_surya": houses["surya"],
            }
        )

    # Per-reference wheel: house 1–12 → sign + occupants
    wheels: dict[str, Any] = {}
    for key in LAGNA_KEYS:
        ref_sign = refs[key]["sign"]
        houses_out: list[dict[str, Any]] = []
        for h in range(1, 13):
            h_sign = sign_for_house(reference_sign=ref_sign, house=h)
            occupants = [
                p
                for p, p_sign in planet_signs.items()
                if house_from_reference(reference_sign=ref_sign, body_sign=p_sign) == h
            ]
            houses_out.append(
                {
                    "house": h,
                    "sign": h_sign,
                    "occupants": occupants,
                }
            )
        wheels[key] = {
            **refs[key],
            "houses": houses_out,
        }

    # Tri-view: for each house number, occupants under each lagna
    tri_view: list[dict[str, Any]] = []
    for h in range(1, 13):
        tri_view.append(
            {
                "house": h,
                "from_lagna": {
                    "sign": sign_for_house(reference_sign=lagna_sign, house=h),
                    "occupants": wheels["lagna"]["houses"][h - 1]["occupants"],
                },
                "from_chandra": {
                    "sign": sign_for_house(reference_sign=moon_sign, house=h),
                    "occupants": wheels["chandra"]["houses"][h - 1]["occupants"],
                },
                "from_surya": {
                    "sign": sign_for_house(reference_sign=sun_sign, house=h),
                    "occupants": wheels["surya"]["houses"][h - 1]["occupants"],
                },
            }
        )

    return {
        "variant": SUDARSHANA_VARIANT,
        "references": refs,
        "planets": planet_rows,
        "wheels": wheels,
        "tri_view": tri_view,
        "notes": [
            "Sudarshana = simultaneous whole-sign houses from Lagna, Moon, and Sun.",
            "Scaffold only — no bhava-effect verdicts or yearly spoke progression yet.",
        ],
    }


__all__ = [
    "LAGNA_KEYS",
    "SUDARSHANA_VARIANT",
    "build_sudarshana_wheel",
    "house_from_reference",
    "sign_for_house",
]

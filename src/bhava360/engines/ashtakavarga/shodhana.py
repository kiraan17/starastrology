"""Ashtakavarga Shodhana and Sodhya Pinda (P12b).

Procedure follows the common B.V. Raman computational sequence
(Trikona → Ekadhipatya → Rasi/Graha gunakara). Tables and edge rules are
Candidate pending Approved classical edition citation.

VedAstro commentary is used only as a comparator/reference — not as a
classical source of record for this product.
"""

from __future__ import annotations

from typing import Iterable

from bhava360.engines.ashtakavarga.tables import BAV_PLANETS
from bhava360.kernel.models import PlanetName, SIGNS

# Elemental trikonas (whole-sign).
TRIKONA_GROUPS: tuple[tuple[str, str, str], ...] = (
    ("Aries", "Leo", "Sagittarius"),  # Fire
    ("Taurus", "Virgo", "Capricorn"),  # Earth
    ("Gemini", "Libra", "Aquarius"),  # Air
    ("Cancer", "Scorpio", "Pisces"),  # Water
)

# Dual-lordship pairs (Cancer/Leo exempt — single luminaries).
EKADHIPATYA_PAIRS: tuple[tuple[str, str], ...] = (
    ("Aries", "Scorpio"),  # Mars
    ("Taurus", "Libra"),  # Venus
    ("Gemini", "Virgo"),  # Mercury
    ("Sagittarius", "Pisces"),  # Jupiter
    ("Capricorn", "Aquarius"),  # Saturn
)

RASI_GUNAKARA: dict[str, int] = {
    "Aries": 7,
    "Taurus": 10,
    "Gemini": 8,
    "Cancer": 4,
    "Leo": 10,
    "Virgo": 5,
    "Libra": 7,
    "Scorpio": 8,
    "Sagittarius": 9,
    "Capricorn": 5,
    "Aquarius": 11,
    "Pisces": 12,
}

GRAHA_GUNAKARA: dict[str, int] = {
    "Sun": 5,
    "Moon": 5,
    "Mars": 8,
    "Mercury": 5,
    "Jupiter": 10,
    "Venus": 7,
    "Saturn": 5,
}

SHODHANA_VARIANT = "raman_candidate_v1"


def _copy_bindus(sign_bindus: dict[str, int]) -> dict[str, int]:
    return {sign: int(sign_bindus.get(sign, 0)) for sign in SIGNS}


def occupied_signs_from_planet_signs(planet_signs: dict[str, str]) -> set[str]:
    """Signs occupied by the seven BAV planets (Rahu/Ketu not counted here)."""
    occupied: set[str] = set()
    for p in BAV_PLANETS:
        sign = planet_signs.get(p.value)
        if sign in SIGNS:
            occupied.add(sign)
    return occupied


def apply_trikona_shodhana(sign_bindus: dict[str, int]) -> dict:
    """I Reduction — Trikona Sodhana with Raman-style zero/equal rules."""
    before = _copy_bindus(sign_bindus)
    after = _copy_bindus(sign_bindus)
    steps: list[dict] = []

    for group in TRIKONA_GROUPS:
        vals = [after[s] for s in group]
        zero_count = sum(1 for v in vals if v == 0)
        rule: str
        result_vals: list[int]

        if zero_count == 1:
            # Rule (b): one zero → no reduction
            rule = "b_one_zero_no_reduction"
            result_vals = list(vals)
        elif zero_count >= 2:
            # Rule (c): two zeros → eliminate remaining figure
            rule = "c_two_zeros_eliminate_group"
            result_vals = [0, 0, 0]
        elif vals[0] == vals[1] == vals[2]:
            # Rule (d): all equal → eliminate group
            rule = "d_all_equal_eliminate_group"
            result_vals = [0, 0, 0]
        else:
            # Rule (a): subtract minimum from all three
            rule = "a_subtract_minimum"
            m = min(vals)
            result_vals = [v - m for v in vals]

        for sign, new_v in zip(group, result_vals, strict=True):
            after[sign] = new_v
        steps.append(
            {
                "group": list(group),
                "before": list(vals),
                "after": result_vals,
                "rule": rule,
            }
        )

    return {
        "kind": "trikona_shodhana",
        "before": before,
        "after": after,
        "steps": steps,
        "variant": SHODHANA_VARIANT,
    }


def apply_ekadhipatya_shodhana(
    sign_bindus: dict[str, int],
    occupied_signs: Iterable[str],
) -> dict:
    """II Reduction — Ekadhipatya Sodhana driven by natal occupation."""
    occupied = {s for s in occupied_signs if s in SIGNS}
    before = _copy_bindus(sign_bindus)
    after = _copy_bindus(sign_bindus)
    steps: list[dict] = []

    for a, b in EKADHIPATYA_PAIRS:
        va, vb = after[a], after[b]
        oa, ob = a in occupied, b in occupied
        rule: str
        na, nb = va, vb

        if va == 0 or vb == 0:
            # I(b): zero figure in one sign → no reduction
            rule = "I_b_zero_figure_no_reduction"
        elif oa and ob:
            # I(a): both occupied → no reduction
            rule = "I_a_both_occupied_no_reduction"
        elif oa ^ ob:
            # Scenario II — exactly one occupied
            if oa:
                # a occupied, b unoccupied
                if va > vb or va == vb:
                    rule = "II_a_or_c_eliminate_unoccupied"
                    na, nb = va, 0
                else:
                    rule = "II_b_equalise_unoccupied_to_occupied"
                    na, nb = va, va
            else:
                # b occupied, a unoccupied
                if vb > va or vb == va:
                    rule = "II_a_or_c_eliminate_unoccupied"
                    na, nb = 0, vb
                else:
                    rule = "II_b_equalise_unoccupied_to_occupied"
                    na, nb = vb, vb
        else:
            # Scenario III — both unoccupied
            if va == vb:
                rule = "III_a_both_unoccupied_equal_eliminate"
                na, nb = 0, 0
            else:
                # III(b): make larger equal to smaller
                rule = "III_b_both_unoccupied_equalise_to_smaller"
                m = min(va, vb)
                na, nb = m, m

        after[a], after[b] = na, nb
        steps.append(
            {
                "pair": [a, b],
                "before": [va, vb],
                "after": [na, nb],
                "occupied": [oa, ob],
                "rule": rule,
            }
        )

    return {
        "kind": "ekadhipatya_shodhana",
        "before": before,
        "after": after,
        "occupied_signs": sorted(occupied),
        "steps": steps,
        "variant": SHODHANA_VARIANT,
    }


def apply_mandala_shodhana(sign_bindus: dict[str, int]) -> dict:
    """SAV preliminary reduction: expunge completed multiples of 12 (leave 12)."""
    before = _copy_bindus(sign_bindus)
    after: dict[str, int] = {}
    steps: list[dict] = []
    for sign in SIGNS:
        n = before[sign]
        if n <= 0:
            reduced = 0
        else:
            r = n % 12
            reduced = 12 if r == 0 else r
        after[sign] = reduced
        steps.append({"sign": sign, "before": n, "after": reduced})
    return {
        "kind": "mandala_shodhana",
        "before": before,
        "after": after,
        "steps": steps,
        "variant": SHODHANA_VARIANT,
    }


def compute_sodhya_pinda(
    reduced_bindus: dict[str, int],
    planet_signs: dict[str, str],
) -> dict:
    """Rasi Pinda + Graha Pinda from reduced figures."""
    rasi_rows = []
    rasi_total = 0
    for sign in SIGNS:
        bindus = int(reduced_bindus.get(sign, 0))
        gunaka = RASI_GUNAKARA[sign]
        product = bindus * gunaka
        rasi_total += product
        rasi_rows.append(
            {
                "sign": sign,
                "bindus": bindus,
                "gunakara": gunaka,
                "product": product,
            }
        )

    graha_rows = []
    graha_total = 0
    for p in BAV_PLANETS:
        sign = planet_signs[p.value]
        bindus = int(reduced_bindus.get(sign, 0))
        gunaka = GRAHA_GUNAKARA[p.value]
        product = bindus * gunaka
        graha_total += product
        graha_rows.append(
            {
                "planet": p.value,
                "occupied_sign": sign,
                "bindus_in_sign": bindus,
                "gunakara": gunaka,
                "product": product,
            }
        )

    return {
        "rasi_pinda": rasi_total,
        "graha_pinda": graha_total,
        "sodhya_pinda": rasi_total + graha_total,
        "rasi_rows": rasi_rows,
        "graha_rows": graha_rows,
        "rasi_gunakara": dict(RASI_GUNAKARA),
        "graha_gunakara": dict(GRAHA_GUNAKARA),
        "variant": SHODHANA_VARIANT,
    }


def reduce_bhinna_ashtakavarga(
    *,
    sign_bindus: dict[str, int],
    planet_signs: dict[str, str],
) -> dict:
    """Full BAV reduction chain + Sodhya Pinda."""
    occupied = occupied_signs_from_planet_signs(planet_signs)
    trikona = apply_trikona_shodhana(sign_bindus)
    ekadhipatya = apply_ekadhipatya_shodhana(trikona["after"], occupied)
    sodhya = compute_sodhya_pinda(ekadhipatya["after"], planet_signs)
    return {
        "raw_bindus": _copy_bindus(sign_bindus),
        "trikona": trikona,
        "ekadhipatya": ekadhipatya,
        "reduced_bindus": ekadhipatya["after"],
        "reduced_total": sum(ekadhipatya["after"].values()),
        "sodhya_pinda": sodhya,
        "variant": SHODHANA_VARIANT,
    }


def reduce_sarva_ashtakavarga(
    *,
    sign_bindus: dict[str, int],
    planet_signs: dict[str, str],
) -> dict:
    """SAV reduction: Mandala → Trikona → Ekadhipatya + Sodhya Pinda."""
    occupied = occupied_signs_from_planet_signs(planet_signs)
    mandala = apply_mandala_shodhana(sign_bindus)
    trikona = apply_trikona_shodhana(mandala["after"])
    ekadhipatya = apply_ekadhipatya_shodhana(trikona["after"], occupied)
    sodhya = compute_sodhya_pinda(ekadhipatya["after"], planet_signs)
    return {
        "raw_bindus": _copy_bindus(sign_bindus),
        "mandala": mandala,
        "trikona": trikona,
        "ekadhipatya": ekadhipatya,
        "reduced_bindus": ekadhipatya["after"],
        "reduced_total": sum(ekadhipatya["after"].values()),
        "sodhya_pinda": sodhya,
        "variant": SHODHANA_VARIANT,
    }

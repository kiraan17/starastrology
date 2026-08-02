"""Prastara Ashtakavarga (P12c) — contributor × sign bindu grid.

Prastara reorganises Bhinnashtakavarga contributor donations into an
8×12 matrix (kakshya-lord order × signs). Variant: raman_candidate_v1.
"""

from __future__ import annotations

from typing import Any

from bhava360.engines.ashtakavarga.tables import (
    BAV_PLANETS,
    KAKSHYA_LORD_NAMES,
    KAKSHYA_SPAN,
    compute_bhinna_ashtakavarga,
    kakshya_for_longitude,
)
from bhava360.kernel.models import PlanetName, SIGNS

PRASTARA_VARIANT = "raman_candidate_v1"
CONTRIBUTOR_ORDER: tuple[str, ...] = KAKSHYA_LORD_NAMES  # Sat→…→Lagna


def build_prastara_matrix(bindus_by_contributor: dict[str, dict[str, int]]) -> dict[str, Any]:
    """Build 8×12 binary grid from per-contributor sign bindu counts."""
    grid: dict[str, dict[str, int]] = {}
    for contributor in CONTRIBUTOR_ORDER:
        row = bindus_by_contributor.get(contributor) or {}
        grid[contributor] = {
            sign: 1 if int(row.get(sign, 0)) > 0 else 0 for sign in SIGNS
        }

    # Reconstruct sign totals from prastara rows.
    sign_totals = {sign: 0 for sign in SIGNS}
    for contributor in CONTRIBUTOR_ORDER:
        for sign in SIGNS:
            sign_totals[sign] += grid[contributor][sign]

    return {
        "contributor_order": list(CONTRIBUTOR_ORDER),
        "signs": list(SIGNS),
        "grid": grid,  # contributor -> sign -> 0|1
        "sign_totals_from_prastara": sign_totals,
        "kakshya_span_deg": KAKSHYA_SPAN,
        "variant": PRASTARA_VARIANT,
    }


def compute_prastara_ashtakavarga(
    *,
    planet_signs: dict[str, str],
    lagna_sign: str,
    target: PlanetName | None = None,
) -> dict[str, Any]:
    """Prastara for one BAV target, or all seven when target is None."""
    targets = [target] if target is not None else list(BAV_PLANETS)
    by_planet: dict[str, Any] = {}
    for t in targets:
        bav = compute_bhinna_ashtakavarga(
            planet_signs=planet_signs,
            lagna_sign=lagna_sign,
            target=t,
        )
        matrix = build_prastara_matrix(bav["bindus_by_contributor"])
        reconstruction_ok = matrix["sign_totals_from_prastara"] == bav["sign_bindus"]
        by_planet[t.value] = {
            "target_planet": t.value,
            "prastara": matrix,
            "bav_sign_bindus": bav["sign_bindus"],
            "reconstruction_ok": reconstruction_ok,
        }
    return {
        "system": "prastara_ashtakavarga",
        "by_planet": by_planet,
        "notes": [
            "Prastara is BAV contributor donations laid out in kakshya-lord order.",
            "Cell=1 means that contributor donated a bindu to the sign in this BAV.",
            "Sign column sum must equal BAV sign bindus.",
        ],
        "variant": PRASTARA_VARIANT,
    }


def kakshya_bindu_active(
    *,
    prastara_grid: dict[str, dict[str, int]],
    sign: str,
    sign_degree: float,
) -> dict[str, Any]:
    """Whether the natal/transit kakshya lord donated a bindu in this sign."""
    kak = kakshya_for_longitude(sign_degree)
    lord = kak["kakshya_lord"]
    active = int(prastara_grid.get(lord, {}).get(sign, 0)) == 1
    return {
        **kak,
        "sign": sign,
        "kakshya_lord_bindu": active,
    }

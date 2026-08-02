"""Lal Kitab engine scaffold (P22a / TEC-090)."""

from __future__ import annotations

from typing import Any

from bhava360.chart.builder import ChartConstructor
from bhava360.engines.lal_kitab.teva import LK_VARIANT, build_lal_kitab_teva
from bhava360.kernel.models import ChartConfig, SubjectInput

ENGINE_NAME = "LalKitab"
ENGINE_VERSION = "0.1.0-teva-scaffold"
TECHNIQUE_IDS = ("TEC-090",)
STATUS = "Candidate"
SAFETY_LEVEL = "restricted"


def run_lal_kitab_engine(
    subject: SubjectInput | None = None,
    *,
    config: ChartConfig | None = None,
    chart: dict[str, Any] | None = None,
    target_year: int | None = None,
    age: int | None = None,
) -> dict[str, Any]:
    """
    Lal Kitab Teva scaffold: fixed-Aries houses, Pakka Ghar, aspects, axis yuti.

    Optional arithmetic varshphal. Debts and remedies are deferred (restricted).
    Contradictions vs Parashara house numbering are kept visible.
    """
    cfg = config or ChartConfig()
    built = chart or ChartConstructor(cfg).build(
        subject,  # type: ignore[arg-type]
        include_vimshottari=False,
        include_relationships=False,
    ).to_dict()

    teva = build_lal_kitab_teva(built, target_year=target_year, age=age)

    return {
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "technique_ids": list(TECHNIQUE_IDS),
        "status": STATUS,
        "safety_level": SAFETY_LEVEL,
        "school": "lal_kitab",
        "config": {
            "lal_kitab.variant": LK_VARIANT,
            "teva_basis": "fixed_aries_house_1",
            "target_year": target_year,
            "age": age,
        },
        "teva": teva,
        "deferred": [
            "Planetary debts (rin) rule packs",
            "Remedies / upay (never auto-invented)",
            "Sleeping house/planet interpretive rules",
            "Friend–enemy yuti effect verdicts",
            "Artificial (farzi) planet constructions",
            "100% aspect interpretive mix rules",
        ],
        "provenance": {
            "status": STATUS,
            "stamp": LK_VARIANT,
            "sources": ["TEC-090", "SRC-013"],
            "notes": [
                "Candidate Teva: fixed Aries=1 from sidereal signs.",
                "Pakka Ghar and LK aspect offsets are Candidate tables.",
                "Keep contradictions vs Parashara visible; do not blend schools.",
            ],
        },
        "safety": {
            "level": SAFETY_LEVEL,
            "note": (
                "Restricted scaffold — structural Teva/aspects only. "
                "Not medical, financial, longevity, or remedial advice."
            ),
            "remedies_emitted": False,
            "debts_emitted": False,
        },
    }


__all__ = [
    "ENGINE_NAME",
    "ENGINE_VERSION",
    "SAFETY_LEVEL",
    "STATUS",
    "TECHNIQUE_IDS",
    "run_lal_kitab_engine",
]

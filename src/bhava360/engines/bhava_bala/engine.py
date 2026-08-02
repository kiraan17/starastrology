"""Bhava Bala engine (P28b / TEC-024)."""

from __future__ import annotations

from typing import Any

from bhava360.chart.builder import ChartConstructor
from bhava360.engines.bhava_bala.components import (
    BHAVA_BALA_VARIANT,
    compute_bhava_bala_pack,
)
from bhava360.engines.shadbala.components import compute_shadbala_pack
from bhava360.kernel.models import ChartConfig, SubjectInput

ENGINE_NAME = "BhavaBala"
ENGINE_VERSION = "0.1.0-partial-scaffold"
TECHNIQUE_IDS = ("TEC-024",)
STATUS = "Candidate"


def run_bhava_bala_engine(
    subject: SubjectInput | None = None,
    *,
    config: ChartConfig | None = None,
    chart: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Partial Bhava Bala: Bhavadhipati + Dig (Lagna class) + Drishti (aspect sum).

    Classical Dig half-sign splits and Drishti polarity deferred.
    """
    cfg = config or ChartConfig()
    built = chart
    if built is None:
        if subject is None:
            raise ValueError("subject or chart is required")
        built = ChartConstructor(cfg).build(
            subject, include_vimshottari=False, include_relationships=True
        ).to_dict()

    shadbala = compute_shadbala_pack(built)
    pack = compute_bhava_bala_pack(built, shadbala=shadbala)

    return {
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "technique_ids": list(TECHNIQUE_IDS),
        "status": STATUS,
        "school": "strength",
        "config": {
            "bhava_bala.variant": BHAVA_BALA_VARIANT,
            "house_basis": "whole_sign_rasi",
            "bhavadhipati_source": "shadbala_partial_total_virupa",
        },
        "bhava_bala": pack,
        "deferred": [
            "Sagittarius/Capricorn half-sign Dig splits",
            "Benefic/malefic Drishti polarity",
            "Classical rupas calibration / full BPHS tables",
        ],
        "provenance": {
            "status": STATUS,
            "stamp": BHAVA_BALA_VARIANT,
            "sources": ["TEC-024", "BPHS Bhava Bala overview (Candidate thin)"],
            "notes": [
                "Partial component pack only.",
                "Depends on partial Shadbala (TEC-023) for Bhavadhipati.",
            ],
        },
        "safety": {
            "note": "Strength metrics for verification — not predictive advice.",
        },
    }


__all__ = [
    "ENGINE_NAME",
    "ENGINE_VERSION",
    "STATUS",
    "TECHNIQUE_IDS",
    "run_bhava_bala_engine",
]

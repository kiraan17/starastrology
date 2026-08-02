"""Shadbala engine (P27b/P28a / TEC-023)."""

from __future__ import annotations

from typing import Any

from bhava360.chart.builder import ChartConstructor
from bhava360.engines.shadbala.components import SHADBALA_VARIANT, compute_shadbala_pack
from bhava360.kernel.models import ChartConfig, SubjectInput

ENGINE_NAME = "Shadbala"
ENGINE_VERSION = "0.2.0-kala-chesta-drik"
TECHNIQUE_IDS = ("TEC-023",)
STATUS = "Candidate"


def run_shadbala_engine(
    subject: SubjectInput | None = None,
    *,
    config: ChartConfig | None = None,
    chart: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Partial Shadbala: Sthana thin + Dig + Naisargika + Kala thin + Chesta thin + Drik thin.

    Remaining Sthana/Kala/Chesta classical tables still deferred.
    """
    cfg = config or ChartConfig()
    built = chart
    if built is None:
        if subject is None:
            raise ValueError("subject or chart is required")
        built = ChartConstructor(cfg).build(
            subject, include_vimshottari=False, include_relationships=True
        ).to_dict()

    pack = compute_shadbala_pack(built)

    return {
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "technique_ids": list(TECHNIQUE_IDS),
        "status": STATUS,
        "school": "strength",
        "config": {
            "shadbala.variant": SHADBALA_VARIANT,
            "house_basis": "whole_sign_rasi",
        },
        "shadbala": pack,
        "deferred": [
            "Saptavargaja / Drekkana / full Ojayugma (navamsa)",
            "Kala remainder (Tribhaga, Abda, Masa, Ayana, Yuddha)",
            "Chesta seeghra kendra + Ayana Chesta for Sun/Moon",
            "Classical Drik drishti-strength tables",
            "Full-pack minimum threshold verdicts",
        ],
        "provenance": {
            "status": STATUS,
            "stamp": SHADBALA_VARIANT,
            "sources": ["TEC-023", "BPHS Shadbala overview (Candidate thin)"],
            "notes": [
                "Partial component pack only.",
                "Do not treat partial_total as complete Shadbala.",
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
    "run_shadbala_engine",
]

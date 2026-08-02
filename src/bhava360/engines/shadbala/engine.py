"""Shadbala engine (P27b–P30b / TEC-023)."""

from __future__ import annotations

from typing import Any

from bhava360.chart.builder import ChartConstructor
from bhava360.engines.shadbala.components import SHADBALA_VARIANT, compute_shadbala_pack
from bhava360.kernel.models import ChartConfig, SubjectInput

ENGINE_NAME = "Shadbala"
ENGINE_VERSION = "0.5.0-chesta-motion"
TECHNIQUE_IDS = ("TEC-023",)
STATUS = "Candidate"


def run_shadbala_engine(
    subject: SubjectInput | None = None,
    *,
    config: ChartConfig | None = None,
    chart: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Partial Shadbala: fuller Sthana + Dig + Naisargika + fuller Kala + Saravali Chesta + Drik thin.

    Seeghra-kendra Chesta and classical Drik tables still deferred.
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
            "Chesta Seeghra-kendra alternate (BPHS mean/true formula)",
            "Abda/Masa Hora-lord-at-sankranti (weekday approx used)",
            "Saptavargaja Adhi-mitra / Adhi-satru (temporal friendship)",
            "Classical Drik drishti-strength tables",
            "Full-pack minimum threshold verdicts",
        ],
        "provenance": {
            "status": STATUS,
            "stamp": SHADBALA_VARIANT,
            "sources": ["TEC-023", "BPHS/Saravali Shadbala Chesta overview (Candidate)"],
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

"""Shadbala engine scaffold (P27b / TEC-023)."""

from __future__ import annotations

from typing import Any

from bhava360.chart.builder import ChartConstructor
from bhava360.engines.shadbala.components import SHADBALA_VARIANT, compute_shadbala_pack
from bhava360.kernel.models import ChartConfig, SubjectInput

ENGINE_NAME = "Shadbala"
ENGINE_VERSION = "0.1.0-partial-scaffold"
TECHNIQUE_IDS = ("TEC-023",)
STATUS = "Candidate"


def run_shadbala_engine(
    subject: SubjectInput | None = None,
    *,
    config: ChartConfig | None = None,
    chart: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Partial Shadbala scaffold: Naisargika + Dig + Uchcha + Kendradi + Ojayugma(rasi).

    Kala, Chesta, Drik, and remaining Sthana subs are deferred.
    """
    cfg = config or ChartConfig()
    built = chart
    if built is None:
        if subject is None:
            raise ValueError("subject or chart is required")
        built = ChartConstructor(cfg).build(
            subject, include_vimshottari=False, include_relationships=False
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
            "Kala Bala pack (Natonnata, Paksha, Tribhaga, Abda/Masa/Vara/Hora, Ayana, Yuddha)",
            "Chesta Bala (mean/true / seeghra kendra)",
            "Drik Bala (aspectual net)",
            "Full-pack minimum threshold verdicts",
        ],
        "provenance": {
            "status": STATUS,
            "stamp": SHADBALA_VARIANT,
            "sources": ["TEC-023", "BPHS Shadbala overview (Candidate thin)"],
            "notes": [
                "Partial component scaffold only.",
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

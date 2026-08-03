"""Vimshopaka engine (P29a / TEC-025)."""

from __future__ import annotations

from typing import Any

from bhava360.chart.builder import ChartConstructor
from bhava360.engines.vimshopaka.components import (
    VIMSHOPAKA_VARIANT,
    compute_vimshopaka_pack,
)
from bhava360.kernel.models import ChartConfig, SubjectInput

ENGINE_NAME = "Vimshopaka"
ENGINE_VERSION = "0.1.0-shodashavarga"
TECHNIQUE_IDS = ("TEC-025",)
STATUS = "Candidate"


def run_vimshopaka_engine(
    subject: SubjectInput | None = None,
    *,
    config: ChartConfig | None = None,
    chart: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Partial Vimshopaka: Shodashavarga weights × Candidate Varga Vishwa.

    Temporal friendship and alternate varga schemes deferred.
    """
    cfg = config or ChartConfig()
    built = chart
    if built is None:
        if subject is None:
            raise ValueError("subject or chart is required")
        built = ChartConstructor(cfg).build(
            subject, include_vimshottari=False, include_relationships=False
        ).to_dict()

    pack = compute_vimshopaka_pack(built)

    return {
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "technique_ids": list(TECHNIQUE_IDS),
        "status": STATUS,
        "school": "strength",
        "config": {
            "vimshopaka.variant": VIMSHOPAKA_VARIANT,
            "scheme": "shodashavarga",
        },
        "vimshopaka": pack,
        "deferred": [
            "Temporal friendship (great friend / great enemy)",
            "Shadvarga / Saptavarga / Dasavarga alternate schemes",
            "BPHS interpretive result bands as verdicts",
        ],
        "provenance": {
            "status": STATUS,
            "stamp": VIMSHOPAKA_VARIANT,
            "sources": ["TEC-025", "BPHS Vimshopaka overview (Candidate thin)"],
            "notes": [
                "Shodashavarga swaviswa weights summing to 20.",
                "Permanent natural friendship only for Varga Vishwa.",
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
    "run_vimshopaka_engine",
]

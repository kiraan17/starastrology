"""Shadbala engine (P27b–P33a / TEC-023)."""

from __future__ import annotations

from typing import Any

from bhava360.chart.builder import ChartConstructor
from bhava360.engines.shadbala.components import SHADBALA_VARIANT, compute_shadbala_pack
from bhava360.kernel.models import ChartConfig, SubjectInput

ENGINE_NAME = "Shadbala"
ENGINE_VERSION = "0.10.0-adhi-mitra"
TECHNIQUE_IDS = ("TEC-023",)
STATUS = "Candidate"


def run_shadbala_engine(
    subject: SubjectInput | None = None,
    *,
    config: ChartConfig | None = None,
    chart: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Partial Shadbala: Sthana (Panchadha) / Kala / Chesta(Seeghra) / Sphuta Drik.

    Inferior Seeghrochcha product tables and sankranti ephemeris sunrise deferred.
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
            "Mercury/Venus Seeghrochcha classical product tables (heliocentric mean proxy used)",
            "Exact ephemeris sunrise for sankranti day (birth-day clocks shifted)",
            "Full-pack minimum threshold verdicts",
        ],
        "provenance": {
            "status": STATUS,
            "stamp": SHADBALA_VARIANT,
            "sources": [
                "TEC-023",
                "BPHS Panchadha Saptavargaja + Seeghra Chesta + Sphuta Drig (Candidate)",
            ],
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

"""Compatibility engine — Ashtakoota thin slice (P20a / TEC-094)."""

from __future__ import annotations

from typing import Any

from bhava360.chart.builder import ChartConstructor
from bhava360.engines.compatibility.ashtakoota import KUTA_VARIANT, compute_ashtakoota
from bhava360.kernel.errors import KernelError, KernelErrorCode
from bhava360.kernel.models import ChartConfig, SubjectInput

ENGINE_NAME = "Compatibility"
ENGINE_VERSION = "0.1.0-ashtakoota"
TECHNIQUE_IDS = ("TEC-094",)
STATUS = "Candidate"


def _moon_longitude(chart: dict[str, Any]) -> float:
    for p in chart.get("planets", []):
        if p.get("planet") == "Moon":
            return float(p["longitude_sidereal_deg"])
    raise KernelError(
        KernelErrorCode.CALCULATION_FAILED,
        "Moon not found in chart for Ashtakoota",
    )


def run_compatibility_engine(
    boy_subject: SubjectInput | None = None,
    girl_subject: SubjectInput | None = None,
    *,
    config: ChartConfig | None = None,
    boy_chart: dict[str, Any] | None = None,
    girl_chart: dict[str, Any] | None = None,
    boy_moon_longitude: float | None = None,
    girl_moon_longitude: float | None = None,
) -> dict[str, Any]:
    """
    Ashtakoota from two Moon longitudes / charts / subjects.

    Score only — no relationship advice or medical claims.
    """
    cfg = config or ChartConfig()

    if boy_moon_longitude is None:
        built_b = boy_chart or ChartConstructor(cfg).build(
            boy_subject,  # type: ignore[arg-type]
            include_vimshottari=False,
            include_relationships=False,
        ).to_dict()
        boy_moon_longitude = _moon_longitude(built_b)
    if girl_moon_longitude is None:
        built_g = girl_chart or ChartConstructor(cfg).build(
            girl_subject,  # type: ignore[arg-type]
            include_vimshottari=False,
            include_relationships=False,
        ).to_dict()
        girl_moon_longitude = _moon_longitude(built_g)

    if boy_moon_longitude is None or girl_moon_longitude is None:
        raise KernelError(
            KernelErrorCode.UNSUPPORTED_CONFIG,
            "boy and girl Moon longitudes (or subjects/charts) are required",
        )

    kuta = compute_ashtakoota(
        boy_moon_longitude=float(boy_moon_longitude),
        girl_moon_longitude=float(girl_moon_longitude),
    )

    return {
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "technique_ids": list(TECHNIQUE_IDS),
        "status": STATUS,
        "school": "compatibility",
        "config": {"ashtakoota.variant": KUTA_VARIANT},
        "ashtakoota": kuta,
        "deferred": [
            "Dosha exception rules (Nadi/Bhakoot exceptions)",
            "South-Indian Dasha kuta variants",
            "Manglik / Kuja dosha overlay",
            "Narrative match advice",
        ],
        "provenance": {
            "status": STATUS,
            "stamp": KUTA_VARIANT,
            "sources": ["TEC-094"],
            "notes": [
                "North-Indian Ashtakoota Candidate point tables.",
                "Output is a numeric score only — not advice.",
            ],
        },
        "safety": {
            "note": "Compatibility score for verification only — not professional advice.",
        },
    }


__all__ = [
    "ENGINE_NAME",
    "ENGINE_VERSION",
    "STATUS",
    "TECHNIQUE_IDS",
    "run_compatibility_engine",
]

"""Transit engine — natal overlay thin slice (P25b / TEC-035)."""

from __future__ import annotations

from typing import Any

from bhava360.chart.builder import ChartConstructor
from bhava360.engines.transit.compare import (
    DEFAULT_CONJUNCTION_ORB_DEG,
    TRANSIT_VARIANT,
    build_transit_overlay,
)
from bhava360.kernel.errors import KernelError, KernelErrorCode
from bhava360.kernel.models import ChartConfig, SubjectInput

ENGINE_NAME = "Transit"
ENGINE_VERSION = "0.1.0-natal-overlay"
TECHNIQUE_IDS = ("TEC-035",)
STATUS = "Candidate"


def _as_transit_subject(subject: SubjectInput) -> SubjectInput:
    return SubjectInput(
        local_datetime=subject.local_datetime,
        timezone_offset_minutes=subject.timezone_offset_minutes,
        timezone_id=subject.timezone_id,
        dst_ambiguity_policy=subject.dst_ambiguity_policy,
        latitude=subject.latitude,
        longitude=subject.longitude,
        location_label=subject.location_label,
        birth_time_uncertainty_minutes=None,
        input_kind="transit",
    )


def run_transit_engine(
    natal_subject: SubjectInput | None = None,
    transit_subject: SubjectInput | None = None,
    *,
    config: ChartConfig | None = None,
    natal_chart: dict[str, Any] | None = None,
    transit_chart: dict[str, Any] | None = None,
    conjunction_orb_deg: float = DEFAULT_CONJUNCTION_ORB_DEG,
) -> dict[str, Any]:
    """
    Compare a transit chart against a natal reference.

    Emits house placements (from natal Lagna/Moon), degree conjunctions,
    and whole-sign transit→natal aspects. No gochara verdicts.
    """
    cfg = config or ChartConfig()
    if natal_chart is None:
        if natal_subject is None:
            raise KernelError(
                KernelErrorCode.UNSUPPORTED_CONFIG,
                "natal_subject or natal_chart is required",
            )
        natal_chart = ChartConstructor(cfg).build(
            natal_subject,
            include_vimshottari=False,
            include_relationships=False,
        ).to_dict()

    if transit_chart is None:
        if transit_subject is None:
            raise KernelError(
                KernelErrorCode.UNSUPPORTED_CONFIG,
                "transit_subject or transit_chart is required",
            )
        transit_chart = ChartConstructor(cfg).build(
            _as_transit_subject(transit_subject),
            include_vimshottari=False,
            include_relationships=False,
        ).to_dict()

    overlay = build_transit_overlay(
        natal_chart,
        transit_chart,
        conjunction_orb_deg=conjunction_orb_deg,
    )

    return {
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "technique_ids": list(TECHNIQUE_IDS),
        "status": STATUS,
        "school": "timing",
        "config": {
            "transit.variant": TRANSIT_VARIANT,
            "conjunction_orb_deg": float(conjunction_orb_deg),
            "house_basis": "whole_sign_from_natal_lagna_and_moon",
        },
        "natal_ref": {
            "local_datetime": (natal_chart.get("input") or {}).get("local_datetime"),
            "lagna_sign": overlay["natal_lagna_sign"],
            "moon_sign": overlay["natal_moon_sign"],
        },
        "transit_ref": {
            "local_datetime": (transit_chart.get("input") or {}).get("local_datetime"),
            "input_kind": (transit_chart.get("input") or {}).get("input_kind"),
        },
        "overlay": overlay,
        "deferred": [
            "Timed ephemeris sweep / next-hit search",
            "Ashtakavarga transit scoring integration",
            "Gochara interpretive verdict packs",
            "Degree-based aspect orbs beyond whole-sign",
        ],
        "provenance": {
            "status": STATUS,
            "stamp": TRANSIT_VARIANT,
            "sources": ["TEC-035"],
            "notes": [
                "Candidate structural overlay only.",
                "Houses counted whole-sign from natal Lagna and natal Moon.",
            ],
        },
        "safety": {
            "note": "Transit overlay for verification — not predictive advice.",
        },
    }


__all__ = [
    "ENGINE_NAME",
    "ENGINE_VERSION",
    "STATUS",
    "TECHNIQUE_IDS",
    "run_transit_engine",
]

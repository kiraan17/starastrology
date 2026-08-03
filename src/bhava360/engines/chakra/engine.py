"""Sudarshana Chakra engine (P18a) — Candidate scaffold."""

from __future__ import annotations

from typing import Any

from bhava360.chart.builder import ChartConstructor
from bhava360.engines.chakra.sudarshana import SUDARSHANA_VARIANT, build_sudarshana_wheel
from bhava360.kernel.models import ChartConfig, SubjectInput

ENGINE_NAME = "SudarshanaChakra"
ENGINE_VERSION = "0.1.0-scaffold"
TECHNIQUE_IDS = ("TEC-080",)
STATUS = "Candidate"


def run_sudarshana_engine(
    subject: SubjectInput | None = None,
    *,
    config: ChartConfig | None = None,
    chart: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Sudarshana Chakra thin scaffold: Lagna / Chandra / Surya whole-sign overlay.

    Deferred: interpretive house effects, yearly spoke progression, transit overlays.
    """
    cfg = config or ChartConfig()
    built = chart or ChartConstructor(cfg).build(
        subject,  # type: ignore[arg-type]
        include_vimshottari=False,
    ).to_dict()

    planets = {p["planet"]: p for p in built["planets"]}
    lagna_sign = built["angles"]["whole_sign"]["ascendant"]["sign"]
    sun_sign = planets["Sun"]["sign"]
    moon_sign = planets["Moon"]["sign"]
    planet_signs = {p["planet"]: p["sign"] for p in built["planets"]}

    wheel = build_sudarshana_wheel(
        lagna_sign=lagna_sign,
        sun_sign=sun_sign,
        moon_sign=moon_sign,
        planet_signs=planet_signs,
    )

    return {
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "technique_ids": list(TECHNIQUE_IDS),
        "status": STATUS,
        "school": "chakra",
        "config": {
            "sudarshana.variant": SUDARSHANA_VARIANT,
            "house_basis": "whole_sign",
        },
        "sudarshana": wheel,
        "deferred": [
            "Bhava-effect / strength verdicts from tri-lagna concurrence",
            "Yearly Sudarshana spoke progression",
            "Transit overlays on Sudarshana wheel",
        ],
        "provenance": {
            "status": STATUS,
            "stamp": SUDARSHANA_VARIANT,
            "sources": ["TEC-080"],
            "notes": [
                "Geometric three-lagna whole-sign overlay only.",
                "No classical interpretive rule pack loaded yet.",
            ],
        },
    }


__all__ = [
    "ENGINE_NAME",
    "ENGINE_VERSION",
    "STATUS",
    "TECHNIQUE_IDS",
    "run_sudarshana_engine",
]

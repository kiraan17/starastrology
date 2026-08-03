"""Panchaka / Bhadra engine (P26a) — TEC-074 thin slice."""

from __future__ import annotations

from typing import Any

from bhava360.chart.builder import ChartConstructor
from bhava360.kernel.models import ChartConfig, SubjectInput
from bhava360.timing.panchaka import PANCHAKA_VARIANT, evaluate_panchaka_bhadra
from bhava360.timing.panchanga_engine import run_panchanga_engine

ENGINE_NAME = "PanchakaBhadra"
ENGINE_VERSION = "0.1.0-panchaka-bhadra"
TECHNIQUE_IDS = ("TEC-074",)
STATUS = "Candidate"


def _lagna_lon(chart: dict[str, Any]) -> float:
    return float(chart["angles"]["whole_sign"]["ascendant"]["longitude_sidereal_deg"])


def run_panchaka_bhadra_engine(
    subject: SubjectInput,
    *,
    config: ChartConfig | None = None,
    chart: dict[str, Any] | None = None,
    panchanga: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Classify Moon Panchak, Panchaka Rahita remainder, and Bhadra at the subject instant.

    Reuses panchanga engine outputs when provided.
    """
    cfg = config or ChartConfig()
    built = chart
    if built is None:
        built = ChartConstructor(cfg).build(
            subject, include_vimshottari=False, include_relationships=False
        ).to_dict()

    pan = panchanga or run_panchanga_engine(subject, config=cfg, chart=built)
    core = pan.get("panchanga") or {}
    tithi = core.get("tithi") or {}
    vara = core.get("vara") or {}
    nak = core.get("nakshatra") or {}
    karana = core.get("karana") or {}

    pack = evaluate_panchaka_bhadra(
        moon_lon_sidereal=float(core["moon_longitude_sidereal_deg"]),
        lagna_lon_sidereal=_lagna_lon(built),
        tithi_index=int(tithi["index"]),
        vara_index=int(vara["index"]),
        nakshatra_index=int(nak["index"]),
        karana_name=karana.get("name"),
    )

    return {
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "technique_ids": list(TECHNIQUE_IDS),
        "status": STATUS,
        "school": "panchanga",
        "config": {
            "panchaka.variant": PANCHAKA_VARIANT,
        },
        "panchaka_bhadra": pack,
        "panchanga_ref": {
            "engine": pan.get("engine"),
            "engine_version": pan.get("engine_version"),
            "tithi": tithi.get("label"),
            "vara": vara.get("name"),
            "nakshatra": nak.get("label"),
            "karana": karana.get("name"),
        },
        "deferred": [
            "Sunrise-to-sunrise lagna-segment sweep for Rahita windows",
            "Moon Panchak ingress/egress timed ephemeris search",
            "Activity-specific classical nibandha mappings beyond labels",
        ],
        "provenance": {
            "status": STATUS,
            "stamp": PANCHAKA_VARIANT,
            "sources": ["TEC-074"],
            "notes": [
                "Candidate structural flags over Panchanga limbs + Lagna.",
                "No medical, longevity, or certainty claims.",
            ],
        },
        "safety": {
            "note": "Timing classification only — not predictive or medical advice.",
        },
    }


__all__ = [
    "ENGINE_NAME",
    "ENGINE_VERSION",
    "STATUS",
    "TECHNIQUE_IDS",
    "run_panchaka_bhadra_engine",
]

"""Muhurta event engine (P20b) — TEC-093 / TEC-076 thin pack."""

from __future__ import annotations

from typing import Any

from bhava360.kernel.models import ChartConfig, SubjectInput
from bhava360.timing.event_rules import ACTIVITY_IDS, EVENT_RULE_VARIANT, evaluate_event_pack
from bhava360.timing.panchanga_engine import run_panchanga_engine

ENGINE_NAME = "MuhurtaEvents"
ENGINE_VERSION = "0.1.0-event-pack"
TECHNIQUE_IDS = ("TEC-093", "TEC-076")
STATUS = "Candidate"


def run_muhurta_event_engine(
    subject: SubjectInput,
    *,
    config: ChartConfig | None = None,
    chart: dict[str, Any] | None = None,
    panchanga: dict[str, Any] | None = None,
    activities: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    """
    Evaluate Candidate activity timing pack at the subject instant.

    Reuses panchanga engine outputs when provided.
    """
    pan = panchanga or run_panchanga_engine(subject, config=config, chart=chart)
    pack = evaluate_event_pack(
        panchanga=pan.get("panchanga") or {},
        muhurta=pan.get("muhurta"),
        bala=pan.get("bala"),
        activities=activities,
    )

    return {
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "technique_ids": list(TECHNIQUE_IDS),
        "status": STATUS,
        "school": "muhurta",
        "config": {
            "event_rules.variant": EVENT_RULE_VARIANT,
            "activities": list(activities) if activities else list(ACTIVITY_IDS),
        },
        "event_pack": pack,
        "panchanga_ref": {
            "engine": pan.get("engine"),
            "engine_version": pan.get("engine_version"),
            "tithi": (pan.get("panchanga") or {}).get("tithi", {}).get("label"),
            "vara": (pan.get("panchanga") or {}).get("vara", {}).get("name"),
            "karana": (pan.get("panchanga") or {}).get("karana", {}).get("name"),
        },
        "deferred": [
            "Full classical muhurta nibandha / event-specific rule libraries",
            "Multi-day window search for next good slot",
            "Electional chart construction beyond instant classification",
        ],
        "provenance": {
            "status": STATUS,
            "stamp": EVENT_RULE_VARIANT,
            "sources": ["TEC-093", "TEC-076"],
            "notes": [
                "Thin Candidate pack layered on P16a–c facts.",
                "Verdicts are good/mixed/avoid timing classes only.",
            ],
        },
        "safety": {
            "note": "Not medical, financial, legal, or longevity advice.",
        },
    }


__all__ = [
    "ENGINE_NAME",
    "ENGINE_VERSION",
    "STATUS",
    "TECHNIQUE_IDS",
    "run_muhurta_event_engine",
]

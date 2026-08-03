"""Birth-time rectification toolkit scaffold (P22b / TEC-095)."""

from __future__ import annotations

from typing import Any

from bhava360.engines.rectification.scan import (
    DEFAULT_STEP_MINUTES,
    DEFAULT_WINDOW_MINUTES,
    RECTIFICATION_VARIANT,
    run_rectification_scan,
)
from bhava360.kernel.models import ChartConfig, SubjectInput

ENGINE_NAME = "Rectification"
ENGINE_VERSION = "0.1.0-scan-scaffold"
TECHNIQUE_IDS = ("TEC-095",)
STATUS = "Candidate"
SAFETY_LEVEL = "restricted"


def run_rectification_engine(
    subject: SubjectInput,
    *,
    config: ChartConfig | None = None,
    window_minutes: float | None = None,
    step_minutes: float = DEFAULT_STEP_MINUTES,
    max_samples: int | None = None,
    events: Any = None,
) -> dict[str, Any]:
    """
    Birth-time sensitivity scan across ±window.

    Emits fingerprints and transitions only — does not assert a true birth time
    or score life events (manual event anchors are passthrough).
    """
    kwargs: dict[str, Any] = {
        "config": config,
        "window_minutes": window_minutes,
        "step_minutes": step_minutes,
        "events": events,
    }
    if max_samples is not None:
        kwargs["max_samples"] = max_samples

    scan = run_rectification_scan(subject, **kwargs)

    return {
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "technique_ids": list(TECHNIQUE_IDS),
        "status": STATUS,
        "safety_level": SAFETY_LEVEL,
        "school": "rectification",
        "config": {
            "rectification.variant": RECTIFICATION_VARIANT,
            "window_minutes": scan["grid"]["window_minutes"],
            "step_minutes": scan["grid"]["step_minutes"],
            "default_window_minutes": DEFAULT_WINDOW_MINUTES,
            "default_step_minutes": DEFAULT_STEP_MINUTES,
        },
        "scan": scan,
        "deferred": [
            "Pranapada / Tatkalika classical check packs",
            "Event-matching dasha/transit scoring",
            "Automatic ranked birth-time selection",
            "Confidence window productization beyond flip markers",
        ],
        "provenance": {
            "status": STATUS,
            "stamp": RECTIFICATION_VARIANT,
            "sources": ["TEC-095"],
            "notes": [
                "Candidate toolkit: time-window fingerprint scan + transition list.",
                "Kunda = lagna×81 mod 360 as structural sensitivity marker.",
                "No winner is selected; manual events are unscored passthrough.",
            ],
        },
        "safety": {
            "level": SAFETY_LEVEL,
            "note": (
                "Restricted scaffold — sensitivity scan only. "
                "Does not certify a true birth time or provide advice."
            ),
            "winner_selected": False,
            "events_scored": False,
        },
    }


__all__ = [
    "ENGINE_NAME",
    "ENGINE_VERSION",
    "SAFETY_LEVEL",
    "STATUS",
    "TECHNIQUE_IDS",
    "run_rectification_engine",
]

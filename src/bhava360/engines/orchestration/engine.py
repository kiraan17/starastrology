"""Evidence / conflict orchestration engine (P23a / TEC-096)."""

from __future__ import annotations

from typing import Any

from bhava360.engines.orchestration.collect import (
    DEFAULT_SCHOOL_WEIGHTS,
    ORCHESTRATION_VARIANT,
    orchestrate_evidence,
)

ENGINE_NAME = "Orchestration"
ENGINE_VERSION = "0.1.0-evidence-scaffold"
TECHNIQUE_IDS = ("TEC-096",)
STATUS = "Candidate"


def run_orchestration_engine(
    sections: dict[str, Any] | None = None,
    *,
    school_weights: dict[str, float] | None = None,
) -> dict[str, Any]:
    """
    Orchestrate multi-engine evidence without blending schools.

    Consumes verification `sections`. Product weights are display aids only —
    never cross-school truth. Does not replace school engines.
    """
    bundle = orchestrate_evidence(
        dict(sections or {}),
        school_weights=school_weights,
    )

    return {
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "technique_ids": list(TECHNIQUE_IDS),
        "status": STATUS,
        "school": "orchestration",
        "config": {
            "orchestration.variant": ORCHESTRATION_VARIANT,
            "school_weights": {
                **DEFAULT_SCHOOL_WEIGHTS,
                **(school_weights or {}),
            },
        },
        "orchestration": bundle,
        "deferred": [
            "Approved product weight schedules per customer tier",
            "Full domain taxonomy for prediction candidates",
            "Expert review / approval workflow hooks",
            "Persistence of evidence snapshots",
        ],
        "provenance": {
            "status": STATUS,
            "stamp": ORCHESTRATION_VARIANT,
            "sources": ["TEC-096", "SRC-015", "SRC-014"],
            "notes": [
                "Consumes engine evidence; never replaces school engines.",
                "Cross-school conflicts kept visible; blended_verdicts=false.",
                "Weights are Candidate product display aids only.",
            ],
        },
        "safety": {
            "note": "Orchestration scaffold — no blended advice or medical claims.",
            "blended_verdicts": False,
        },
    }


__all__ = [
    "ENGINE_NAME",
    "ENGINE_VERSION",
    "STATUS",
    "TECHNIQUE_IDS",
    "run_orchestration_engine",
]

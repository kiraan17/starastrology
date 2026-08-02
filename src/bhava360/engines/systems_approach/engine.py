"""Systems Approach engine scaffold (P21b / TEC-091)."""

from __future__ import annotations

from typing import Any

from bhava360.chart.builder import ChartConstructor
from bhava360.engines.systems_approach.config import (
    SA_VARIANT,
    build_systems_approach_profile,
)
from bhava360.kernel.models import ChartConfig, SubjectInput

ENGINE_NAME = "SystemsApproach"
ENGINE_VERSION = "0.1.0-config-scaffold"
TECHNIQUE_IDS = ("TEC-091",)
STATUS = "Candidate"


def run_systems_approach_engine(
    subject: SubjectInput | None = None,
    *,
    config: ChartConfig | None = None,
    chart: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Systems' Approach configuration scaffold.

    Emits functional natures, MT-house primaries, structural weakness flags,
    and close-longitude pairs. No interpretive verdicts or remedies.
    """
    cfg = config or ChartConfig()
    built = chart or ChartConstructor(cfg).build(
        subject,  # type: ignore[arg-type]
        include_vimshottari=False,
        include_relationships=False,
    ).to_dict()

    profile = build_systems_approach_profile(built)

    return {
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "technique_ids": list(TECHNIQUE_IDS),
        "status": STATUS,
        "school": "systems_approach",
        "config": {
            "systems_approach.variant": SA_VARIANT,
            **profile["config"],
        },
        "profile": profile,
        "deferred": [
            "Close aspect affliction scoring (non-conjunction special aspects)",
            "Transit / dasha timing under Systems' Approach",
            "Interpretive house/planet verdict packs",
            "Combustion and exact orb refinements beyond chart dignity flag",
            "Remedial / advice narratives",
        ],
        "provenance": {
            "status": STATUS,
            "stamp": SA_VARIANT,
            "sources": ["TEC-091"],
            "notes": [
                "Candidate SA configuration: MT-in-dusthana functional nature rule.",
                "Moon mooltrikona treated as Cancer under Systems' Approach.",
                "Structural flags only — no interpretive rule pack loaded.",
            ],
        },
        "safety": {
            "note": "Configuration/scaffold output for verification — not advice.",
        },
    }


__all__ = [
    "ENGINE_NAME",
    "ENGINE_VERSION",
    "STATUS",
    "TECHNIQUE_IDS",
    "run_systems_approach_engine",
]

"""Yogini dasha engine (P25a / TEC-031)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from bhava360.chart.builder import ChartConstructor
from bhava360.kernel.models import ChartConfig, SubjectInput
from bhava360.kernel.timeutil import resolve_subject_time
from bhava360.timing.yogini import YOGINI_VARIANT, build_yogini_tree

ENGINE_NAME = "YoginiDasha"
ENGINE_VERSION = "0.1.0-maha-antar"
TECHNIQUE_IDS = ("TEC-031",)
STATUS = "Candidate"


def run_yogini_dasha_engine(
    subject: SubjectInput,
    *,
    config: ChartConfig | None = None,
    chart: dict[str, Any] | None = None,
    moon_longitude: float | None = None,
    years_ahead: float = 72.0,
    include_antar: bool = True,
) -> dict[str, Any]:
    """
    Yogini Maha (+ optional Antar) from Moon nakshatra.

    Candidate start rule: (nakshatra_number + 3) mod 8. No interpretive verdicts.
    """
    cfg = config or ChartConfig()
    moon_lon = moon_longitude
    birth_utc: datetime
    if moon_lon is None:
        built = chart or ChartConstructor(cfg).build(
            subject,
            include_vimshottari=False,
            include_relationships=False,
        ).to_dict()
        moon = next(p for p in built["planets"] if p["planet"] == "Moon")
        moon_lon = float(moon["longitude_sidereal_deg"])
        rt = built.get("resolved_time") or {}
        birth_utc = datetime.fromisoformat(str(rt["utc_datetime"]).replace("Z", "+00:00"))
    else:
        resolved = resolve_subject_time(subject)
        birth_utc = resolved.utc_datetime

    if birth_utc.tzinfo is not None:
        birth_utc = birth_utc.astimezone(timezone.utc).replace(tzinfo=None)

    tree = build_yogini_tree(
        birth_utc,
        float(moon_lon),
        years_ahead=years_ahead,
        include_antar=include_antar,
    )

    return {
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "technique_ids": list(TECHNIQUE_IDS),
        "status": STATUS,
        "school": "timing",
        "config": {
            "yogini.variant": YOGINI_VARIANT,
            "years_ahead": years_ahead,
            "include_antar": include_antar,
            "mean_year_days": 365.2425,
        },
        "yogini": tree,
        "deferred": [
            "Alternate Yogini start-rule variants beyond (nak+3) mod 8",
            "Pratyantar and deeper levels",
            "Interpretive Yogini effect packs",
        ],
        "provenance": {
            "status": STATUS,
            "stamp": YOGINI_VARIANT,
            "sources": ["TEC-031"],
            "notes": [
                "Candidate 36-year Yogini cycle; start via (nakshatra_number+3) mod 8.",
                "Antar proportional like Vimshottari-style subdivision.",
            ],
        },
        "safety": {
            "note": "Timing periods only — not predictive advice.",
        },
    }


__all__ = [
    "ENGINE_NAME",
    "ENGINE_VERSION",
    "STATUS",
    "TECHNIQUE_IDS",
    "run_yogini_dasha_engine",
]

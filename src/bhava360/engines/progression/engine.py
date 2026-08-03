"""Bhrigu Bindu / progression engine (P18b) — Candidate thin slice."""

from __future__ import annotations

from typing import Any

from bhava360.chart.builder import ChartConstructor
from bhava360.engines.progression.bhrigu_bindu import (
    BHRIGU_BINDU_VARIANT,
    DEFAULT_CONJUNCTION_ORB_DEG,
    compute_bhrigu_bindu,
    transit_hits_on_bindu,
)
from bhava360.kernel.models import ChartConfig, SubjectInput

ENGINE_NAME = "BhriguBindu"
ENGINE_VERSION = "0.1.0-thin-slice"
TECHNIQUE_IDS = ("TEC-081",)
STATUS = "Candidate"


def run_bhrigu_bindu_engine(
    subject: SubjectInput | None = None,
    *,
    config: ChartConfig | None = None,
    chart: dict[str, Any] | None = None,
    conjunction_orb_deg: float = DEFAULT_CONJUNCTION_ORB_DEG,
    transit_chart: dict[str, Any] | None = None,
    transit_longitudes: dict[str, float] | None = None,
) -> dict[str, Any]:
    """
    Compute natal Bhrigu Bindu and optional transit conjunction hits.

    Pass ``transit_chart`` (constructed chart dict) or ``transit_longitudes``
    to evaluate Candidate transit triggers on the bindu.
    """
    cfg = config or ChartConfig()
    built = chart or ChartConstructor(cfg).build(
        subject,  # type: ignore[arg-type]
        include_vimshottari=False,
    ).to_dict()

    planets = {p["planet"]: p for p in built["planets"]}
    moon = float(planets["Moon"]["longitude_sidereal_deg"])
    rahu = float(planets["Rahu"]["longitude_sidereal_deg"])
    lagna = float(built["angles"]["whole_sign"]["ascendant"]["longitude_sidereal_deg"])
    planet_lons = {p["planet"]: float(p["longitude_sidereal_deg"]) for p in built["planets"]}

    bindu = compute_bhrigu_bindu(
        moon_longitude=moon,
        rahu_longitude=rahu,
        lagna_longitude=lagna,
        conjunction_orb_deg=conjunction_orb_deg,
        planet_longitudes=planet_lons,
    )

    transit_lons = transit_longitudes
    if transit_lons is None and transit_chart is not None:
        transit_lons = {
            p["planet"]: float(p["longitude_sidereal_deg"])
            for p in transit_chart.get("planets", [])
        }

    transit_hits: list[dict[str, Any]] = []
    if transit_lons is not None:
        transit_hits = transit_hits_on_bindu(
            bindu_longitude=float(bindu["longitude_sidereal_deg"]),
            transit_longitudes=transit_lons,
            orb_deg=conjunction_orb_deg,
        )

    return {
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "technique_ids": list(TECHNIQUE_IDS),
        "status": STATUS,
        "school": "progression",
        "config": {
            "bhrigu_bindu.variant": BHRIGU_BINDU_VARIANT,
            "conjunction_orb_deg": float(conjunction_orb_deg),
        },
        "bhrigu_bindu": bindu,
        "transit_hits": transit_hits,
        "transit_evaluated": transit_lons is not None,
        "deferred": [
            "Aspect triggers to Bhrigu Bindu (beyond conjunction)",
            "Timed transit search / ephemeris sweep",
            "Event scoring / interpretive outcomes",
            "Alternate midpoint conventions (arithmetic mean without shorter-arc)",
        ],
        "provenance": {
            "status": STATUS,
            "stamp": BHRIGU_BINDU_VARIANT,
            "sources": ["TEC-081"],
            "notes": [
                "Bhrigu Bindu = shorter-arc midpoint of Moon and Rahu.",
                "Transit hits = conjunction within configured orb (Candidate).",
            ],
        },
    }


__all__ = [
    "ENGINE_NAME",
    "ENGINE_VERSION",
    "STATUS",
    "TECHNIQUE_IDS",
    "run_bhrigu_bindu_engine",
]

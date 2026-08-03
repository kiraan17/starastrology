"""Nakshatra chakra engine — Tara / Kota / Sarvatobhadra scaffolds (P18c)."""

from __future__ import annotations

from typing import Any

from bhava360.chart.builder import ChartConstructor
from bhava360.engines.chakra.nakshatra_chakras import (
    KOTA_CHAKRA_VARIANT,
    SBC_VARIANT,
    TARA_CHAKRA_VARIANT,
    build_nakshatra_chakra_pack,
)
from bhava360.kernel.models import ChartConfig, SubjectInput

ENGINE_NAME = "NakshatraChakras"
ENGINE_VERSION = "0.1.0-scaffold"
TECHNIQUE_IDS = ("TEC-082", "TEC-083")
STATUS = "Candidate"


def run_nakshatra_chakra_engine(
    subject: SubjectInput | None = None,
    *,
    config: ChartConfig | None = None,
    chart: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Tara Chakra + Kota Chakra + Sarvatobhadra rim placement (Candidate).

    Vedha / attack-defense / full 9×9 SBC grid deferred.
    """
    cfg = config or ChartConfig()
    built = chart or ChartConstructor(cfg).build(
        subject,  # type: ignore[arg-type]
        include_vimshottari=False,
    ).to_dict()

    planet_longitudes = {
        p["planet"]: float(p["longitude_sidereal_deg"]) for p in built["planets"]
    }
    moon_lon = planet_longitudes["Moon"]
    pack = build_nakshatra_chakra_pack(
        moon_longitude=moon_lon,
        planet_longitudes=planet_longitudes,
    )

    return {
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "technique_ids": list(TECHNIQUE_IDS),
        "status": STATUS,
        "school": "chakra",
        "config": {
            "tara_chakra.variant": TARA_CHAKRA_VARIANT,
            "kota_chakra.variant": KOTA_CHAKRA_VARIANT,
            "sarvatobhadra.variant": SBC_VARIANT,
        },
        **pack,
        "deferred": [
            "Sarvatobhadra full 9×9 alphabet/tithi/rashi grid",
            "Vedha (front/side/back) obstruction rules",
            "Kota Abhijit placement and attack/defense verdicts",
            "Tara Chakra muhurta event rule packs",
        ],
        "provenance": {
            "status": STATUS,
            "stamp": "nakshatra_chakras_candidate_v1",
            "sources": ["TEC-082", "TEC-083"],
            "notes": [
                "Tara Chakra reuses Moon-based 9-tara cycle from TEC-072.",
                "Kota layout is Candidate 8-direction 27-nakshatra placement.",
                "Sarvatobhadra is rim placement only; Vedha Source Needed.",
            ],
        },
    }


__all__ = [
    "ENGINE_NAME",
    "ENGINE_VERSION",
    "STATUS",
    "TECHNIQUE_IDS",
    "run_nakshatra_chakra_engine",
]

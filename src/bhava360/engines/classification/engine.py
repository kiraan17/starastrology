"""Classification engine — Gandanta / Chandra Kriya / Avastha (P19a)."""

from __future__ import annotations

from typing import Any

from bhava360.chart.builder import ChartConstructor
from bhava360.engines.classification.conditions import (
    AVASTHA_VARIANT,
    GANDANTA_VARIANT,
    KRIYA_VARIANT,
    VELA_VARIANT,
    classify_chandra_kriya,
    classify_chandra_vela,
    classify_point,
)
from bhava360.kernel.models import ChartConfig, SubjectInput

ENGINE_NAME = "Classification"
ENGINE_VERSION = "0.1.0-gandanta-kriya"
TECHNIQUE_IDS = ("TEC-084", "TEC-085")
STATUS = "Candidate"


def run_classification_engine(
    subject: SubjectInput | None = None,
    *,
    config: ChartConfig | None = None,
    chart: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Classify natal points for Gandanta, Baladi Avastha, and Moon Kriya/Vela.

    No medical/longevity claims — structural flags only.
    """
    cfg = config or ChartConfig()
    built = chart or ChartConstructor(cfg).build(
        subject,  # type: ignore[arg-type]
        include_vimshottari=False,
    ).to_dict()

    bodies: list[dict[str, Any]] = []
    for p in built["planets"]:
        bodies.append(
            classify_point(
                float(p["longitude_sidereal_deg"]),
                label=str(p["planet"]),
            )
        )

    lagna_lon = float(built["angles"]["whole_sign"]["ascendant"]["longitude_sidereal_deg"])
    lagna_row = classify_point(lagna_lon, label="Lagna")
    bodies.append(lagna_row)

    moon = next(b for b in bodies if b["body"] == "Moon")
    kriya = classify_chandra_kriya(float(moon["longitude_sidereal_deg"]))
    vela = classify_chandra_vela(float(moon["longitude_sidereal_deg"]))

    gandanta_hits = [
        {
            "body": b["body"],
            "junction": b["gandanta"]["junction"],
            "nakshatra_gandanta": b["gandanta"]["nakshatra_gandanta"],
            "rasi_gandanta": b["gandanta"]["rasi_gandanta"],
            "nakshatra_label": b["nakshatra_label"],
        }
        for b in bodies
        if b["gandanta"]["active"]
    ]

    return {
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "technique_ids": list(TECHNIQUE_IDS),
        "status": STATUS,
        "school": "classification",
        "config": {
            "gandanta.variant": GANDANTA_VARIANT,
            "chandra_kriya.variant": KRIYA_VARIANT,
            "chandra_vela.variant": VELA_VARIANT,
            "baladi_avastha.variant": AVASTHA_VARIANT,
        },
        "bodies": bodies,
        "gandanta_hits": gandanta_hits,
        "moon": {
            "chandra_kriya": kriya,
            "chandra_vela": vela,
            "gandanta": moon["gandanta"],
            "baladi_avastha": moon["baladi_avastha"],
        },
        "lagna": {
            "gandanta": lagna_row["gandanta"],
            "baladi_avastha": lagna_row["baladi_avastha"],
        },
        "deferred": [
            "Named Chandra Vela table",
            "Jagrat/Swapna/Sushupti and other avastha systems",
            "Full interpretive Gandanta remedies / severity scoring",
            "Approved freeze of Chandra Kriya name spellings",
        ],
        "provenance": {
            "status": STATUS,
            "stamp": "classification_candidate_v1",
            "sources": ["TEC-084", "TEC-085"],
            "notes": [
                "Gandanta via nakshatra pada and rasi 3°20' junction rules (Candidate).",
                "Chandra Kriya = 60×6° zones; names Candidate.",
                "Baladi Avastha = 5×6° bands with odd/even reverse.",
                "No medical or longevity conclusions.",
            ],
        },
        "safety": {
            "restricted_claims": False,
            "note": "Classification flags only — not health/longevity advice.",
        },
    }


__all__ = [
    "ENGINE_NAME",
    "ENGINE_VERSION",
    "STATUS",
    "TECHNIQUE_IDS",
    "run_classification_engine",
]

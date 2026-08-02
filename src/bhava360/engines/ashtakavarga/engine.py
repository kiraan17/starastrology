from __future__ import annotations

from typing import Any

from bhava360.chart.builder import ChartConstructor
from bhava360.engines.ashtakavarga.tables import (
    BAV_PLANETS,
    compute_bhinna_ashtakavarga,
    compute_sarva_ashtakavarga,
    kakshya_for_longitude,
)
from bhava360.kernel.models import ChartConfig, PlanetName, SubjectInput


def run_ashtakavarga_engine(
    subject: SubjectInput,
    *,
    config: ChartConfig | None = None,
    chart: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compute BAV/SAV with contributor audit trails and kakshya labels."""
    built = chart or ChartConstructor(config).build(
        subject,
        include_vimshottari=False,
    ).to_dict()

    planet_signs = {p["planet"]: p["sign"] for p in built["planets"] if p["planet"] in {x.value for x in BAV_PLANETS}}
    lagna_sign = built["angles"]["whole_sign"]["ascendant"]["sign"]

    sav = compute_sarva_ashtakavarga(planet_signs=planet_signs, lagna_sign=lagna_sign)

    kakshyas = {}
    for p in built["planets"]:
        if p["planet"] in planet_signs:
            kakshyas[p["planet"]] = kakshya_for_longitude(p["sign_degree"])

    # Transit scoring stub: natal SAV of each planet's occupied sign.
    transit_scores = {}
    for p in built["planets"]:
        if p["planet"] not in planet_signs:
            continue
        sign = p["sign"]
        transit_scores[p["planet"]] = {
            "occupied_sign": sign,
            "sav_bindus": sav["sign_bindus"][sign],
            "bav_bindus": sav["bhinnas"][p["planet"]]["sign_bindus"][sign],
            "kakshya": kakshyas[p["planet"]],
        }

    return {
        "engine": "Ashtakavarga",
        "engine_version": "0.1.0-thin-slice",
        "lagna_sign": lagna_sign,
        "planet_signs": planet_signs,
        "sarvashtakavarga": {
            "sign_bindus": sav["sign_bindus"],
            "total_bindus": sav["total_bindus"],
        },
        "bhinnashtakavarga": sav["bhinnas"],
        "kakshyas": kakshyas,
        "natal_sign_scores": transit_scores,
        "notes": sav["notes"]
        + [
            "Kakshya labelling included; full kakshya-lord transit scorer deferred.",
            "Trikona/Ekadhipatya Shodhana and Sodhya Pinda deferred.",
        ],
        "table_variant": sav["table_variant"],
    }

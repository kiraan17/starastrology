from __future__ import annotations

from typing import Any

from bhava360.chart.builder import ChartConstructor
from bhava360.engines.ashtakavarga.prastara import (
    compute_prastara_ashtakavarga,
    kakshya_bindu_active,
)
from bhava360.engines.ashtakavarga.shodhana import (
    reduce_bhinna_ashtakavarga,
    reduce_sarva_ashtakavarga,
)
from bhava360.engines.ashtakavarga.tables import (
    BAV_PLANETS,
    compute_sarva_ashtakavarga,
    kakshya_for_longitude,
)
from bhava360.kernel.models import ChartConfig, SubjectInput

ENGINE_VERSION = "0.3.0-prastara"


def run_ashtakavarga_engine(
    subject: SubjectInput,
    *,
    config: ChartConfig | None = None,
    chart: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compute BAV/SAV, Prastara, Shodhana, Sodhya Pinda, and kakshya labels."""
    built = chart or ChartConstructor(config).build(
        subject,
        include_vimshottari=False,
    ).to_dict()

    planet_signs = {
        p["planet"]: p["sign"]
        for p in built["planets"]
        if p["planet"] in {x.value for x in BAV_PLANETS}
    }
    lagna_sign = built["angles"]["whole_sign"]["ascendant"]["sign"]

    sav = compute_sarva_ashtakavarga(planet_signs=planet_signs, lagna_sign=lagna_sign)
    prastara = compute_prastara_ashtakavarga(
        planet_signs=planet_signs,
        lagna_sign=lagna_sign,
    )

    bhinna_reduced = {}
    for p in BAV_PLANETS:
        bav = sav["bhinnas"][p.value]
        bhinna_reduced[p.value] = reduce_bhinna_ashtakavarga(
            sign_bindus=bav["sign_bindus"],
            planet_signs=planet_signs,
        )

    sav_reduced = reduce_sarva_ashtakavarga(
        sign_bindus=sav["sign_bindus"],
        planet_signs=planet_signs,
    )

    kakshyas = {}
    for p in built["planets"]:
        if p["planet"] in planet_signs:
            kakshyas[p["planet"]] = kakshya_for_longitude(p["sign_degree"])

    transit_scores = {}
    for p in built["planets"]:
        if p["planet"] not in planet_signs:
            continue
        sign = p["sign"]
        grid = prastara["by_planet"][p["planet"]]["prastara"]["grid"]
        kak_bindu = kakshya_bindu_active(
            prastara_grid=grid,
            sign=sign,
            sign_degree=p["sign_degree"],
        )
        transit_scores[p["planet"]] = {
            "occupied_sign": sign,
            "sav_bindus": sav["sign_bindus"][sign],
            "bav_bindus": sav["bhinnas"][p["planet"]]["sign_bindus"][sign],
            "sav_reduced_bindus": sav_reduced["reduced_bindus"][sign],
            "bav_reduced_bindus": bhinna_reduced[p["planet"]]["reduced_bindus"][sign],
            "kakshya": kakshyas[p["planet"]],
            "kakshya_lord_bindu": kak_bindu["kakshya_lord_bindu"],
        }

    return {
        "engine": "Ashtakavarga",
        "engine_version": ENGINE_VERSION,
        "technique_ids": [
            "TEC-048",
            "TEC-049",
            "TEC-050",
            "TEC-051",
            "TEC-052",
            "TEC-053",
        ],
        "lagna_sign": lagna_sign,
        "planet_signs": planet_signs,
        "sarvashtakavarga": {
            "sign_bindus": sav["sign_bindus"],
            "total_bindus": sav["total_bindus"],
            "shodhana": sav_reduced,
        },
        "bhinnashtakavarga": sav["bhinnas"],
        "bhinnashtakavarga_shodhana": bhinna_reduced,
        "prastara": prastara,
        "kakshyas": kakshyas,
        "natal_sign_scores": transit_scores,
        "notes": [
            "SAV is sum of seven BAVs (Sun–Saturn).",
            "Bindu contributors are retained per BAV for audit/reconstruction.",
            "Prastara Ashtakavarga: 8×12 contributor grids per BAV (TEC-050).",
            "Natal kakshya_lord_bindu flags whether occupied kakshya donated in that BAV.",
            "Trikona + Ekadhipatya Shodhana and Sodhya Pinda included (raman_candidate_v1).",
            "SAV shodhana applies Mandala (mod-12 leave-12) before Trikona/Ekadhipatya.",
            "Full transit-day kakshya scorer deferred.",
            "Longevity/ayurdaya conversion from Sodhya Pinda deferred.",
        ],
        "table_variant": sav["table_variant"],
        "shodhana_variant": sav_reduced["variant"],
        "prastara_variant": prastara["variant"],
    }

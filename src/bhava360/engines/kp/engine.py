from __future__ import annotations

from typing import Any

from bhava360.chart.builder import ChartConstructor
from bhava360.chart.dignity import sign_lord
from bhava360.engines.evidence import RuleOutcome
from bhava360.engines.kp.config_rules import evaluate_kp_config_isolation
from bhava360.engines.kp.lords import kp_lord_chain
from bhava360.kernel.errors import KernelError, KernelErrorCode
from bhava360.kernel.models import (
    AyanamsaMode,
    ChartConfig,
    HouseSystem,
    PlanetName,
    SubjectInput,
)


def _significators_for_house(
    house_num: int,
    planets: list[dict[str, Any]],
    cuspal_chain: dict[str, Any],
) -> dict[str, list[str]]:
    """Thin significator sketch: occupants, owner, star lord, sub lord."""
    occupants = []
    for p in planets:
        houses = p.get("houses") or {}
        if houses.get("bhava_chalit_house") == house_num:
            occupants.append(p["planet"])

    cusp_sign = cuspal_chain.get("sign")
    owner_planet = sign_lord(cusp_sign) if cusp_sign else None
    owner = owner_planet.value if owner_planet else None
    return {
        "occupants": occupants,
        "owner": [owner] if owner else [],
        "star_lord": [cuspal_chain["star_lord"]],
        "sub_lord": [cuspal_chain["sub_lord"]],
    }


def run_kp_engine(
    subject: SubjectInput,
    *,
    config: ChartConfig | None = None,
    allow_nonstandard_config: bool = False,
) -> dict[str, Any]:
    """KP thin-slice: config gate, planet/cusp lord chains, basic significators."""
    cfg = config or ChartConfig(
        ayanamsa=AyanamsaMode.KP,
        house_system=HouseSystem.PLACIDUS,
    )
    cfg.calc_library_version = "bhava360-kernel-0.5.0-kp"

    config_stamp = cfg.stamp()
    config_stamp["kp_allow_nonstandard_config"] = allow_nonstandard_config
    isolation = evaluate_kp_config_isolation(config_stamp)
    if isolation.outcome != RuleOutcome.MATCHED:
        raise KernelError(
            KernelErrorCode.UNSUPPORTED_CONFIG,
            "KP_CONFIG_MISMATCH",
            isolation.to_dict(),
        )

    # Build chart under KP ayanamsa + Placidus.
    chart = ChartConstructor(cfg).build(
        subject,
        bhava_system=HouseSystem.PLACIDUS,
        include_vimshottari=True,
    ).to_dict()

    planet_chains = {}
    for p in chart["planets"]:
        chain = kp_lord_chain(p["longitude_sidereal_deg"]).to_dict()
        planet_chains[p["planet"]] = chain
        p["kp_lords"] = chain

    cusp_chains = []
    bhava = chart["angles"]["bhava_chalit"]
    for cusp in bhava["cusps"]:
        chain = kp_lord_chain(cusp["longitude_sidereal_deg"]).to_dict()
        chain["house"] = cusp["house"]
        chain["sign"] = cusp["sign"]
        chain["sign_degree"] = cusp["sign_degree"]
        chain["significators"] = _significators_for_house(
            cusp["house"],
            chart["planets"],
            chain,
        )
        cusp_chains.append(chain)

    return {
        "engine": "KP",
        "engine_version": "0.1.0-thin-slice",
        "config_isolation": isolation.to_dict(),
        "chart": chart,
        "planet_lord_chains": planet_chains,
        "cuspal_lord_chains": cusp_chains,
        "notes": [
            "Thin slice only: lord chains + basic significator sketch.",
            "No domain verdicts or horary 1–249 in this release.",
            "Uses KP ayanamsa + Placidus; Lahiri/whole-sign silently refused.",
        ],
    }

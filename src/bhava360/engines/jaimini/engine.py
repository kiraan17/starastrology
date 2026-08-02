"""Jaimini school engine (thin slice).

Terminology lock: this engine is *Jaimini* only — never Gemini.
"""

from __future__ import annotations

from typing import Any

from bhava360.chart.builder import ChartConstructor
from bhava360.engines.jaimini.calculations import (
    CharaKarakaScheme,
    compute_argala,
    compute_arudha_padas,
    compute_chara_karakas,
    compute_karakamsa_swamsa,
)
from bhava360.kernel.errors import KernelError, KernelErrorCode
from bhava360.kernel.models import ChartConfig, SubjectInput

ENGINE_NAME = "Jaimini"
ENGINE_VERSION = "0.1.0-thin-slice"
TECHNIQUE_IDS = ("TEC-028", "TEC-066", "TEC-067", "TEC-068")


def _parse_scheme(scheme: CharaKarakaScheme | str) -> CharaKarakaScheme:
    if isinstance(scheme, CharaKarakaScheme):
        return scheme
    normalized = str(scheme).strip().lower()
    if normalized in {"seven", "7", "seven_planet", "7-planet"}:
        return CharaKarakaScheme.SEVEN
    if normalized in {"eight", "8", "eight_planet", "8-planet"}:
        return CharaKarakaScheme.EIGHT
    raise KernelError(
        KernelErrorCode.UNSUPPORTED_CONFIG,
        f"jaimini.chara_karaka.scheme must be seven|eight (got {scheme!r})",
    )


def run_jaimini_engine(
    subject: SubjectInput | None = None,
    *,
    config: ChartConfig | None = None,
    chart: dict[str, Any] | None = None,
    chara_karaka_scheme: CharaKarakaScheme | str = CharaKarakaScheme.SEVEN,
) -> dict[str, Any]:
    """
    Thin-slice Jaimini: Chara Karakas, Arudha A1–A12, Karakamsa/Swamsa, Argala sketch.

    `chara_karaka_scheme` is always stamped (VARIANT-001). Console may pass seven or eight;
    production verdict APIs should require an explicit caller choice.
    """
    scheme = _parse_scheme(chara_karaka_scheme)
    built = chart or ChartConstructor(config).build(
        subject,  # type: ignore[arg-type]
        include_vimshottari=False,
    ).to_dict()

    planet_longitudes = {
        p["planet"]: float(p["longitude_sidereal_deg"]) for p in built["planets"]
    }
    planet_signs = {p["planet"]: p["sign"] for p in built["planets"]}
    lagna_sign = built["angles"]["whole_sign"]["ascendant"]["sign"]
    asc_lon = float(built["angles"]["whole_sign"]["ascendant"]["longitude_sidereal_deg"])

    chara = compute_chara_karakas(planet_longitudes, scheme=scheme)
    arudha = compute_arudha_padas(lagna_sign=lagna_sign, planet_signs=planet_signs)
    ak_lon = float(chara["atmakaraka"]["longitude_sidereal_deg"])
    karakamsa = compute_karakamsa_swamsa(
        atmakaraka_longitude=ak_lon,
        ascendant_longitude=asc_lon,
    )
    a1_sign = arudha["arudha_lagna"]["arudha_sign"]
    argala = compute_argala(a1_sign)

    return {
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "technique_ids": list(TECHNIQUE_IDS),
        "school": "jaimini",
        "config": {
            "jaimini.chara_karaka.scheme": scheme.value,
            "variant_id": "VARIANT-001",
        },
        "lagna_sign": lagna_sign,
        "chara_karakas": chara,
        "arudha": arudha,
        "karakamsa_swamsa": karakamsa,
        "argala": argala,
        "notes": [
            "Engine name is Jaimini — never Gemini.",
            "Thin slice Candidate pending classical/expert confirmation of tables.",
            "Jaimini rashi dashas and event interpretation pack deferred.",
            *chara.get("notes", []),
            *arudha.get("notes", []),
            *karakamsa.get("notes", []),
            *argala.get("notes", []),
        ],
    }

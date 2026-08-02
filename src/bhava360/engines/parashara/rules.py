from __future__ import annotations

from bhava360.chart.bhava import rasi_house_from_asc
from bhava360.chart.dignity import classify_dignity
from bhava360.engines.evidence import ConditionResult, RuleEvidence, RuleOutcome
from bhava360.kernel.derived import normalize_longitude
from bhava360.kernel.models import PlanetName


def _planet_map(planets: list[dict]) -> dict[str, dict]:
    return {p["planet"]: p for p in planets}


def _rasi_house(asc_lon: float, planet_lon: float) -> int:
    return rasi_house_from_asc(asc_lon, planet_lon)


def _relative_house(from_house: int, to_house: int) -> int:
    return ((to_house - from_house) % 12) + 1


def _is_kendra_relative(from_house: int, to_house: int) -> bool:
    return _relative_house(from_house, to_house) in {1, 4, 7, 10}


def evaluate_gajakesari(chart: dict) -> RuleEvidence:
    """Provisional product definition: Moon and Jupiter in mutual whole-sign kendras.

    Source: SRC-004 Candidate + SRC-015 product isolation; exact classical wording
    still pending expert edition approval. Natal potential only until activation.
    """
    planets = _planet_map(chart["planets"])
    asc = chart["angles"]["whole_sign"]["ascendant"]["longitude_sidereal_deg"]
    moon = planets["Moon"]
    jup = planets["Jupiter"]
    moon_h = _rasi_house(asc, moon["longitude_sidereal_deg"])
    jup_h = _rasi_house(asc, jup["longitude_sidereal_deg"])

    c1 = ConditionResult(
        "C1_mutual_kendra",
        _is_kendra_relative(moon_h, jup_h) and _is_kendra_relative(jup_h, moon_h),
        {
            "moon_house": moon_h,
            "jupiter_house": jup_h,
            "definition": "whole_sign_mutual_kendra_1_4_7_10",
        },
    )

    # Provisional cancellation: Jupiter combust (near Sun) weakens/cancels formation claim.
    jup_dign = classify_dignity(
        PlanetName.JUPITER,
        jup["longitude_sidereal_deg"],
        sun_longitude_sidereal_deg=planets["Sun"]["longitude_sidereal_deg"],
    )
    x1 = ConditionResult(
        "X1_jupiter_combust_provisional",
        jup_dign.is_combust_candidate,
        {"is_combust_candidate": jup_dign.is_combust_candidate},
    )

    notes = [
        "Provisional product definition pending Approved BPHS edition citation.",
        "Natal potential only; do not treat as current-event claim without activation.",
    ]

    if not c1.passed:
        outcome = RuleOutcome.FAILED
    elif x1.passed:
        outcome = RuleOutcome.CANCELLED
    else:
        outcome = RuleOutcome.MATCHED

    return RuleEvidence(
        rule_id="RULE-PARASHARA-001",
        technique_id="TEC-037",
        school="Parashara",
        name="Gajakesari Yoga natal formation",
        version="0.2.0-provisional",
        source_ids=["SRC-004", "SRC-014"],
        outcome=outcome,
        conditions=[c1],
        exceptions=[x1],
        participants=["Moon", "Jupiter"],
        houses={"Moon": moon_h, "Jupiter": jup_h},
        activation={
            "type": "natal_potential_until_period_activation",
            "required_lords": ["Moon", "Jupiter"],
            "active": False,
            "reason": "activation evaluated separately against dasha lords",
        },
        notes=notes,
    )


def evaluate_budha_aditya(chart: dict) -> RuleEvidence:
    """Provisional: Sun and Mercury in the same whole sign (sign conjunction)."""
    planets = _planet_map(chart["planets"])
    sun = planets["Sun"]
    mer = planets["Mercury"]
    same_sign = sun["sign"] == mer["sign"]
    orb = abs(
        (
            normalize_longitude(sun["longitude_sidereal_deg"])
            - normalize_longitude(mer["longitude_sidereal_deg"])
            + 180.0
        )
        % 360.0
        - 180.0
    )
    c1 = ConditionResult(
        "C1_same_sign_conjunction",
        same_sign,
        {"sun_sign": sun["sign"], "mercury_sign": mer["sign"], "orb_deg": orb},
    )
    # Provisional exception: Mercury retrograde noted as modifier, not hard cancel.
    x1 = ConditionResult(
        "X1_mercury_retrograde_note",
        bool(mer.get("is_retrograde")),
        {"is_retrograde": mer.get("is_retrograde")},
    )
    outcome = RuleOutcome.MATCHED if c1.passed else RuleOutcome.FAILED
    notes = ["Provisional product definition; expert source citation still required."]
    if x1.passed and outcome == RuleOutcome.MATCHED:
        notes.append("Mercury retrograde present — recorded as modifier note, not cancellation.")

    asc = chart["angles"]["whole_sign"]["ascendant"]["longitude_sidereal_deg"]
    return RuleEvidence(
        rule_id="RULE-PARASHARA-002",
        technique_id="TEC-037",
        school="Parashara",
        name="Budha-Aditya Yoga natal formation",
        version="0.1.0-provisional",
        source_ids=["SRC-004", "SRC-014"],
        outcome=outcome,
        conditions=[c1],
        exceptions=[x1],
        participants=["Sun", "Mercury"],
        houses={
            "Sun": _rasi_house(asc, sun["longitude_sidereal_deg"]),
            "Mercury": _rasi_house(asc, mer["longitude_sidereal_deg"]),
        },
        activation={
            "type": "natal_potential_until_period_activation",
            "required_lords": ["Sun", "Mercury"],
            "active": False,
            "reason": "activation evaluated separately against dasha lords",
        },
        notes=notes,
    )


PARASHARA_RULES = (
    evaluate_gajakesari,
    evaluate_budha_aditya,
)

from __future__ import annotations

from bhava360.engines.evidence import ConditionResult, RuleEvidence, RuleOutcome
from bhava360.kernel.models import AyanamsaMode, HouseSystem


def evaluate_kp_config_isolation(config: dict) -> RuleEvidence:
    """RULE-KP-001: KP runs must use KP ayanamsa + Placidus unless explicit override."""
    ayanamsa = config.get("ayanamsa")
    house_system = config.get("house_system")
    allow_override = bool(config.get("kp_allow_nonstandard_config", False))

    c1 = ConditionResult(
        "C1_kp_ayanamsa",
        ayanamsa == AyanamsaMode.KP.value,
        {"ayanamsa": ayanamsa, "required": AyanamsaMode.KP.value},
    )
    c2 = ConditionResult(
        "C2_placidus_houses",
        house_system == HouseSystem.PLACIDUS.value,
        {"house_system": house_system, "required": HouseSystem.PLACIDUS.value},
    )
    e1 = ConditionResult(
        "E1_override_flag",
        allow_override,
        {"kp_allow_nonstandard_config": allow_override},
    )

    if c1.passed and c2.passed:
        outcome = RuleOutcome.MATCHED
        notes = ["KP config isolation satisfied."]
    elif allow_override:
        outcome = RuleOutcome.MATCHED
        notes = ["Nonstandard KP config accepted only because override flag is set."]
    else:
        outcome = RuleOutcome.FAILED
        notes = ["KP_CONFIG_MISMATCH: refuse silent Lahiri/whole-sign reuse for KP engine."]

    return RuleEvidence(
        rule_id="RULE-KP-001",
        technique_id="TEC-042",
        school="KP",
        name="KP configuration isolation",
        version="0.1.0",
        source_ids=["SRC-006", "SRC-015"],
        outcome=outcome,
        conditions=[c1, c2],
        exceptions=[e1],
        participants=[],
        houses={},
        activation={"type": "always_for_kp_runs", "active": True},
        notes=notes,
    )

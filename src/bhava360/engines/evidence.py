from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RuleOutcome(str, Enum):
    MATCHED = "matched"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"
    INCONCLUSIVE = "inconclusive"


@dataclass(slots=True)
class ConditionResult:
    condition_id: str
    passed: bool
    detail: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "condition_id": self.condition_id,
            "passed": self.passed,
            "detail": self.detail,
        }


@dataclass(slots=True)
class RuleEvidence:
    rule_id: str
    technique_id: str
    school: str
    name: str
    version: str
    source_ids: list[str]
    outcome: RuleOutcome
    conditions: list[ConditionResult]
    exceptions: list[ConditionResult]
    participants: list[str]
    houses: dict[str, int]
    activation: dict[str, Any]
    notes: list[str] = field(default_factory=list)
    safety_level: str = "normal"

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "technique_id": self.technique_id,
            "school": self.school,
            "name": self.name,
            "version": self.version,
            "source_ids": self.source_ids,
            "outcome": self.outcome.value,
            "conditions": [c.to_dict() for c in self.conditions],
            "exceptions": [e.to_dict() for e in self.exceptions],
            "participants": self.participants,
            "houses": self.houses,
            "activation": self.activation,
            "notes": self.notes,
            "safety_level": self.safety_level,
        }

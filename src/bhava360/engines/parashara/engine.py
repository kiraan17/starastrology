from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from bhava360.engines.evidence import RuleEvidence, RuleOutcome
from bhava360.engines.parashara.rules import PARASHARA_RULES


def active_lords_at(
    dashas: dict[str, Any] | None,
    when_utc: datetime,
) -> dict[str, str | None]:
    """Return maha/antar lords active at a UTC instant, if dasha tree present."""
    if not dashas:
        return {"maha": None, "antar": None}
    result: dict[str, str | None] = {"maha": None, "antar": None}
    for level in ("maha", "antar"):
        for period in dashas.get("levels", {}).get(level, []):
            start = datetime.fromisoformat(period["start_utc"])
            end = datetime.fromisoformat(period["end_utc"])
            if start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)
            if end.tzinfo is None:
                end = end.replace(tzinfo=timezone.utc)
            if start <= when_utc < end:
                result[level] = period["lord"]
                break
    return result


def apply_period_activation(
    evidence: RuleEvidence,
    dashas: dict[str, Any] | None,
    when_utc: datetime | None = None,
) -> RuleEvidence:
    """Mark natal yoga as period-activated when a required lord rules maha or antar."""
    when = when_utc or datetime.now(timezone.utc)
    lords = active_lords_at(dashas, when)
    required = set(evidence.activation.get("required_lords", []))
    active_set = {v for v in lords.values() if v}
    activated = bool(required & active_set)
    evidence.activation = {
        **evidence.activation,
        "when_utc": when.isoformat(),
        "active_lords": lords,
        "active": activated and evidence.outcome == RuleOutcome.MATCHED,
        "reason": (
            "required participant rules current maha/antar"
            if activated and evidence.outcome == RuleOutcome.MATCHED
            else "natal potential only or no overlapping period lord"
        ),
    }
    return evidence


def run_parashara_engine(
    chart: dict[str, Any],
    *,
    when_utc: datetime | None = None,
) -> dict[str, Any]:
    """Run the thin-slice Parashara rule pack against a constructed chart dict."""
    when = when_utc or datetime.fromisoformat(chart["resolved_time"]["utc_datetime"])
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)

    results: list[RuleEvidence] = []
    for rule_fn in PARASHARA_RULES:
        evidence = rule_fn(chart)
        evidence = apply_period_activation(evidence, chart.get("dashas"), when)
        results.append(evidence)

    return {
        "engine": "Parashara",
        "engine_version": "0.1.0-thin-slice",
        "evaluated_at_utc": when.isoformat(),
        "rule_count": len(results),
        "results": [r.to_dict() for r in results],
    }

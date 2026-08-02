"""Evidence collection and conflict grouping — Candidate (TEC-096)."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

ORCHESTRATION_VARIANT = "evidence_orchestration_candidate_v1"

# Candidate product display weights — not universal truth; never blend schools.
DEFAULT_SCHOOL_WEIGHTS: dict[str, float] = {
    "parashara": 1.0,
    "kp": 1.0,
    "jaimini": 1.0,
    "nadi": 1.0,
    "ashtakavarga": 1.0,
    "tajika": 1.0,
    "lal_kitab": 1.0,
    "systems_approach": 1.0,
    "compatibility": 1.0,
    "numerology": 1.0,
    "muhurta": 1.0,
    "classification": 1.0,
    "prashna": 1.0,
    "rectification": 1.0,
    "chakra": 1.0,
    "progression": 1.0,
    "orchestration": 1.0,
}

OUTCOME_SCORE: dict[str, float] = {
    "matched": 1.0,
    "failed": 0.0,
    "cancelled": 0.0,
    "skipped": 0.0,
    "inconclusive": 0.5,
}

RESTRICTED_SAFETY_LEVELS = frozenset(
    {"restricted", "research_only", "prohibited_user_facing"}
)

# Map known rule/technique ids → conflict group keys (Candidate taxonomy).
CONFLICT_GROUP_BY_RULE: dict[str, str] = {
    "RULE-PARASHARA-001": "yoga.gajakesari",
    "RULE-PARASHARA-002": "yoga.budha_aditya",
    "RULE-KP-001": "config.kp_isolation",
}

CONFLICT_GROUP_BY_TECHNIQUE: dict[str, str] = {
    "TEC-090": "school.house_numbering",
    "TEC-091": "school.functional_nature",
    "TEC-095": "input.birth_time_sensitivity",
}


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:12]}"


def normalize_evidence_item(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize a rule/engine evidence dict into the orchestration envelope."""
    school = str(raw.get("school") or "unknown").lower()
    rule_id = raw.get("rule_id")
    technique_id = raw.get("technique_id") or (
        (raw.get("technique_ids") or [None])[0]
    )
    outcome = raw.get("outcome") or "inconclusive"
    if hasattr(outcome, "value"):
        outcome = outcome.value
    outcome = str(outcome)

    conflict_group = (
        raw.get("conflict_group")
        or (CONFLICT_GROUP_BY_RULE.get(str(rule_id)) if rule_id else None)
        or (CONFLICT_GROUP_BY_TECHNIQUE.get(str(technique_id)) if technique_id else None)
        or f"school.{school}.ungrouped"
    )

    safety = str(raw.get("safety_level") or "normal")
    item = {
        "result_id": raw.get("result_id") or _new_id("res"),
        "engine": raw.get("engine"),
        "school": school,
        "technique_id": technique_id,
        "rule_id": rule_id,
        "rule_version": raw.get("version") or raw.get("rule_version"),
        "name": raw.get("name"),
        "outcome": outcome,
        "source_ids": list(raw.get("source_ids") or []),
        "participants": list(raw.get("participants") or []),
        "houses": dict(raw.get("houses") or {}),
        "activation": dict(raw.get("activation") or {}),
        "notes": list(raw.get("notes") or []),
        "safety_level": safety,
        "conflict_group": conflict_group,
        "domain": raw.get("domain") or conflict_group.split(".")[0],
        "claim_restriction": raw.get("claim_restriction")
        or ("disclaimer" if safety in RESTRICTED_SAFETY_LEVELS else "none"),
    }
    return item


def collect_evidence_from_sections(sections: dict[str, Any]) -> list[dict[str, Any]]:
    """Harvest RuleEvidence-like items from verification report sections."""
    items: list[dict[str, Any]] = []

    para = sections.get("parashara")
    if para:
        for r in para.get("results") or []:
            items.append(
                normalize_evidence_item(
                    {
                        **r,
                        "engine": para.get("engine") or "Parashara",
                        "school": r.get("school") or "parashara",
                    }
                )
            )

    kp = sections.get("kp")
    if kp and kp.get("config_isolation"):
        iso = kp["config_isolation"]
        items.append(
            normalize_evidence_item(
                {
                    **iso,
                    "engine": kp.get("engine") or "KP",
                    "school": iso.get("school") or "kp",
                    "domain": "config",
                }
            )
        )

    lk = sections.get("lal_kitab")
    if lk:
        teva = lk.get("teva") or {}
        contra = teva.get("contradictions") or {}
        diff_count = int(contra.get("diff_count") or 0)
        items.append(
            normalize_evidence_item(
                {
                    "engine": lk.get("engine") or "LalKitab",
                    "school": "lal_kitab",
                    "technique_id": "TEC-090",
                    "rule_id": "STRUCT-LK-HOUSE-VS-PARASHARA",
                    "name": "Lal Kitab Teva vs Parashara house numbering",
                    "version": lk.get("engine_version"),
                    "outcome": "matched" if diff_count > 0 else "failed",
                    "source_ids": ["TEC-090", "SRC-013", "SRC-015"],
                    "notes": list(contra.get("vs_parashara") or []),
                    "safety_level": lk.get("safety_level") or "restricted",
                    "conflict_group": "school.house_numbering",
                    "domain": "school",
                    "participants": list(contra.get("planets_with_house_number_diff") or []),
                    "houses": {"diff_count": diff_count},
                }
            )
        )
        # Mirror structural note from Parashara side when chart present.
        if sections.get("chart") and diff_count > 0:
            items.append(
                normalize_evidence_item(
                    {
                        "engine": "Parashara",
                        "school": "parashara",
                        "technique_id": "TEC-007",
                        "rule_id": "STRUCT-PARA-LAGNA-HOUSES",
                        "name": "Parashara lagna-counted rasi houses",
                        "version": "structural",
                        "outcome": "matched",
                        "source_ids": ["SRC-015"],
                        "notes": [
                            "Parashara whole-sign houses count from lagna — not fixed Aries=1.",
                        ],
                        "safety_level": "normal",
                        "conflict_group": "school.house_numbering",
                        "domain": "school",
                    }
                )
            )

    sa = sections.get("systems_approach")
    if sa:
        profile = sa.get("profile") or {}
        natures = profile.get("functional_natures") or {}
        items.append(
            normalize_evidence_item(
                {
                    "engine": sa.get("engine") or "SystemsApproach",
                    "school": "systems_approach",
                    "technique_id": "TEC-091",
                    "rule_id": "STRUCT-SA-FUNCTIONAL-NATURE",
                    "name": "Systems Approach functional natures",
                    "version": sa.get("engine_version"),
                    "outcome": "matched",
                    "source_ids": ["TEC-091"],
                    "notes": [
                        f"FM={natures.get('functional_malefics')}",
                        f"FB={natures.get('functional_benefics')}",
                    ],
                    "safety_level": "normal",
                    "conflict_group": "school.functional_nature",
                    "domain": "school",
                    "participants": list(natures.get("functional_malefics") or []),
                }
            )
        )

    rect = sections.get("rectification")
    if rect:
        scan = rect.get("scan") or {}
        sm = scan.get("summary") or {}
        flips = bool(sm.get("lagna_sign_flips") or sm.get("d9_lagna_flips"))
        items.append(
            normalize_evidence_item(
                {
                    "engine": rect.get("engine") or "Rectification",
                    "school": "rectification",
                    "technique_id": "TEC-095",
                    "rule_id": "STRUCT-RECT-SENSITIVITY",
                    "name": "Birth-time sensitivity in window",
                    "version": rect.get("engine_version"),
                    "outcome": "matched" if flips else "failed",
                    "source_ids": ["TEC-095"],
                    "notes": [
                        "Fingerprint flips in scan window (not a birth-time verdict).",
                    ],
                    "safety_level": rect.get("safety_level") or "restricted",
                    "conflict_group": "input.birth_time_sensitivity",
                    "domain": "input",
                    "houses": {
                        "transition_count": sm.get("transition_count") or 0,
                    },
                }
            )
        )

    return items


def score_item(item: dict[str, Any], weights: dict[str, float]) -> dict[str, Any]:
    """Attach Candidate product score (school weight × outcome). Not blended truth."""
    school = item["school"]
    w = float(weights.get(school, 1.0))
    o = float(OUTCOME_SCORE.get(item["outcome"], 0.0))
    return {
        **item,
        "score": {
            "school_weight": w,
            "outcome_score": o,
            "weighted": round(w * o, 6),
            "policy": "candidate_product_weight_v1",
            "note": "Display ranking aid within a school — not cross-school truth.",
        },
    }


def apply_safety_gates(items: list[dict[str, Any]]) -> dict[str, Any]:
    """Partition evidence by safety; block prohibited user-facing claims."""
    allowed: list[dict[str, Any]] = []
    gated: list[dict[str, Any]] = []
    for item in items:
        level = item.get("safety_level") or "normal"
        if level == "prohibited_user_facing":
            gated.append({**item, "gate": "blocked"})
        elif level in RESTRICTED_SAFETY_LEVELS:
            gated.append({**item, "gate": "restricted_visible"})
            allowed.append({**item, "gate": "restricted_visible"})
        else:
            allowed.append({**item, "gate": "allowed"})
    return {
        "allowed": allowed,
        "gated": gated,
        "blocked_count": sum(1 for g in gated if g.get("gate") == "blocked"),
        "restricted_count": sum(1 for g in gated if g.get("gate") == "restricted_visible"),
    }


def build_conflict_groups(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Group evidence by conflict_group.

    Cross-school conflict when ≥2 schools present with disagreeing outcomes.
    Schools are never blended into a single verdict.
    """
    by_group: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        by_group.setdefault(item["conflict_group"], []).append(item)

    groups: list[dict[str, Any]] = []
    for key, members in sorted(by_group.items()):
        schools = sorted({m["school"] for m in members})
        outcomes = sorted({m["outcome"] for m in members})
        cross_school = len(schools) >= 2
        disagree = cross_school and len(outcomes) >= 2
        # Also conflict if same group has matched vs failed across schools
        matched_schools = {m["school"] for m in members if m["outcome"] == "matched"}
        failed_schools = {
            m["school"]
            for m in members
            if m["outcome"] in {"failed", "cancelled"}
        }
        structural_conflict = bool(matched_schools & failed_schools) or (
            cross_school and matched_schools and failed_schools
        )
        # House-numbering: both matched but different school meanings = conflict
        isolation_conflict = cross_school and key.startswith("school.")
        is_conflict = disagree or structural_conflict or (
            isolation_conflict and len(members) >= 2
        )

        groups.append(
            {
                "conflict_group": key,
                "domain": members[0].get("domain"),
                "member_result_ids": [m["result_id"] for m in members],
                "schools": schools,
                "outcomes": outcomes,
                "cross_school": cross_school,
                "is_conflict": is_conflict,
                "resolution": "keep_separate",
                "blended": False,
                "notes": [
                    "Schools remain independent (SRC-015).",
                    "No silent averaging or blended verdict.",
                ],
            }
        )
    return groups


def build_prediction_candidates(
    items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Thin prediction-candidate stubs from matched/failed evidence by domain.

    No narrative claims — support/oppose lists only.
    """
    by_domain: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        if item.get("gate") == "blocked":
            continue
        by_domain.setdefault(item.get("domain") or "general", []).append(item)

    candidates: list[dict[str, Any]] = []
    for domain, members in sorted(by_domain.items()):
        support = [m["result_id"] for m in members if m["outcome"] == "matched"]
        oppose = [
            m["result_id"]
            for m in members
            if m["outcome"] in {"failed", "cancelled"}
        ]
        mixed = [
            m["result_id"]
            for m in members
            if m["outcome"] in {"inconclusive", "skipped"}
        ]
        # Per-school weighted sum — listed separately, not merged as truth
        school_scores: dict[str, float] = {}
        for m in members:
            school = m["school"]
            school_scores[school] = school_scores.get(school, 0.0) + float(
                (m.get("score") or {}).get("weighted") or 0.0
            )
        claim_restriction = "none"
        if any(
            m.get("safety_level") in RESTRICTED_SAFETY_LEVELS for m in members
        ):
            claim_restriction = "disclaimer"
        if any(m.get("safety_level") == "prohibited_user_facing" for m in members):
            claim_restriction = "blocked"

        candidates.append(
            {
                "candidate_id": _new_id("cand"),
                "domain": domain,
                "support_result_ids": support,
                "oppose_result_ids": oppose,
                "mixed_result_ids": mixed,
                "score": {
                    "by_school": school_scores,
                    "policy": "per_school_only",
                    "blended_total": None,
                    "note": "Scores are per-school; blended_total is intentionally null.",
                },
                "claim_restriction": claim_restriction,
                "blended": False,
            }
        )
    return candidates


def orchestrate_evidence(
    sections: dict[str, Any],
    *,
    school_weights: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Full Candidate orchestration pass over verification sections."""
    weights = {**DEFAULT_SCHOOL_WEIGHTS, **(school_weights or {})}
    raw_items = collect_evidence_from_sections(sections)
    scored = [score_item(i, weights) for i in raw_items]
    safety = apply_safety_gates(scored)
    # Rank within each school by weighted score (desc)
    by_school: dict[str, list[dict[str, Any]]] = {}
    for item in safety["allowed"]:
        by_school.setdefault(item["school"], []).append(item)
    ranked_by_school = {
        school: sorted(
            members,
            key=lambda m: float((m.get("score") or {}).get("weighted") or 0.0),
            reverse=True,
        )
        for school, members in by_school.items()
    }
    conflicts = build_conflict_groups(scored)
    candidates = build_prediction_candidates(safety["allowed"])

    return {
        "variant": ORCHESTRATION_VARIANT,
        "policy": {
            "school_isolation": True,
            "blended_verdicts": False,
            "source_ids": ["SRC-015", "SRC-014", "TEC-096"],
            "weights": weights,
        },
        "evidence": scored,
        "evidence_count": len(scored),
        "safety": {
            "allowed_count": len(safety["allowed"]),
            "blocked_count": safety["blocked_count"],
            "restricted_count": safety["restricted_count"],
            "gated_result_ids": [g["result_id"] for g in safety["gated"]],
        },
        "ranked_by_school": ranked_by_school,
        "conflict_groups": conflicts,
        "conflict_count": sum(1 for c in conflicts if c["is_conflict"]),
        "prediction_candidates": candidates,
        "summary": {
            "evidence_count": len(scored),
            "school_count": len(by_school),
            "conflict_count": sum(1 for c in conflicts if c["is_conflict"]),
            "candidate_count": len(candidates),
            "blended": False,
        },
    }


__all__ = [
    "CONFLICT_GROUP_BY_RULE",
    "DEFAULT_SCHOOL_WEIGHTS",
    "ORCHESTRATION_VARIANT",
    "OUTCOME_SCORE",
    "apply_safety_gates",
    "build_conflict_groups",
    "build_prediction_candidates",
    "collect_evidence_from_sections",
    "normalize_evidence_item",
    "orchestrate_evidence",
    "score_item",
]

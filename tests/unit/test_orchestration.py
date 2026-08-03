"""Unit tests for evidence orchestration scaffold (P23a / TEC-096)."""

from __future__ import annotations

from datetime import datetime

from bhava360.chart.builder import ChartConstructor
from bhava360.engines.lal_kitab import run_lal_kitab_engine
from bhava360.engines.orchestration import run_orchestration_engine
from bhava360.engines.orchestration.collect import (
    build_conflict_groups,
    normalize_evidence_item,
    orchestrate_evidence,
)
from bhava360.engines.parashara import run_parashara_engine
from bhava360.kernel.models import SubjectInput


def test_normalize_assigns_conflict_group():
    item = normalize_evidence_item(
        {
            "rule_id": "RULE-PARASHARA-001",
            "school": "parashara",
            "outcome": "matched",
            "technique_id": "TEC-020",
        }
    )
    assert item["conflict_group"] == "yoga.gajakesari"
    assert item["result_id"]


def test_cross_school_house_conflict_not_blended():
    items = [
        normalize_evidence_item(
            {
                "school": "lal_kitab",
                "technique_id": "TEC-090",
                "rule_id": "STRUCT-LK-HOUSE-VS-PARASHARA",
                "outcome": "matched",
                "conflict_group": "school.house_numbering",
            }
        ),
        normalize_evidence_item(
            {
                "school": "parashara",
                "technique_id": "TEC-007",
                "rule_id": "STRUCT-PARA-LAGNA-HOUSES",
                "outcome": "matched",
                "conflict_group": "school.house_numbering",
            }
        ),
    ]
    groups = build_conflict_groups(items)
    assert len(groups) == 1
    g = groups[0]
    assert g["is_conflict"] is True
    assert g["blended"] is False
    assert g["resolution"] == "keep_separate"
    assert set(g["schools"]) == {"lal_kitab", "parashara"}


def test_orchestrate_from_live_sections():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_offset_minutes=330,
        latitude=13.0827,
        longitude=80.2707,
    )
    chart = ChartConstructor().build(
        subject, include_vimshottari=True, include_relationships=False
    ).to_dict()
    sections = {
        "chart": chart,
        "parashara": run_parashara_engine(chart),
        "lal_kitab": run_lal_kitab_engine(chart=chart, target_year=2024),
    }
    out = run_orchestration_engine(sections)
    assert out["engine"] == "Orchestration"
    assert "TEC-096" in out["technique_ids"]
    bundle = out["orchestration"]
    assert bundle["summary"]["blended"] is False
    assert out["safety"]["blended_verdicts"] is False
    assert bundle["evidence_count"] >= 2
    assert bundle["conflict_count"] >= 1
    assert any(
        c["conflict_group"] == "school.house_numbering" and c["is_conflict"]
        for c in bundle["conflict_groups"]
    )
    for cand in bundle["prediction_candidates"]:
        assert cand["score"]["blended_total"] is None
        assert cand["blended"] is False


def test_empty_sections_scaffold():
    out = orchestrate_evidence({})
    assert out["evidence_count"] == 0
    assert out["summary"]["blended"] is False

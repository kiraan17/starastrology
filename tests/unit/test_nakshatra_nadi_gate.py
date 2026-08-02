"""P13 Nakshatra Nadi corpus gate and planet-in-star scaffold."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

from bhava360.chart.builder import ChartConstructor
from bhava360.engines.nadi import (
    assert_nadi_corpus_approved,
    is_nadi_corpus_approved,
    load_nadi_corpus_status,
    planet_in_star_facts,
    run_nakshatra_nadi_engine,
)
from bhava360.kernel.errors import KernelError, KernelErrorCode
from bhava360.kernel.models import SubjectInput


def test_default_corpus_blocked():
    status = load_nadi_corpus_status()
    assert status.corpus_status == "blocked"
    assert status.interpretive_rules_allowed is False
    assert is_nadi_corpus_approved() is False


def test_assert_corpus_blocked():
    with pytest.raises(KernelError) as exc:
        assert_nadi_corpus_approved()
    assert exc.value.code == KernelErrorCode.CORPUS_GATE_BLOCKED


def test_approved_status_requires_fields(tmp_path: Path):
    bad = tmp_path / "bad.json"
    bad.write_text(
        json.dumps(
            {
                "source_id": "SRC-009",
                "technique_ids": ["TEC-054"],
                "corpus_status": "approved",
                "corpus_id": None,
                "approval_status": "Candidate",
                "approved_by": [],
                "approved_at": None,
                "notes": "",
                "schema_version": 1,
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(KernelError) as exc:
        load_nadi_corpus_status(bad)
    assert exc.value.code == KernelErrorCode.CORPUS_GATE_BLOCKED


def test_approved_status_loads(tmp_path: Path):
    good = tmp_path / "good.json"
    good.write_text(
        json.dumps(
            {
                "source_id": "SRC-009",
                "technique_ids": ["TEC-054", "TEC-055"],
                "corpus_status": "approved",
                "corpus_id": "CORPUS-NADI-TEST",
                "approval_status": "Approved",
                "approved_by": ["domain:test"],
                "approved_at": "2026-08-02T00:00:00Z",
                "notes": "test only",
                "schema_version": 1,
            }
        ),
        encoding="utf-8",
    )
    status = assert_nadi_corpus_approved(status_path=good)
    assert status.corpus_id == "CORPUS-NADI-TEST"


def test_planet_in_star_facts_and_engine_scaffold():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_id="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
        location_label="Chennai",
    )
    chart = ChartConstructor().build(subject, include_vimshottari=False).to_dict()
    facts = planet_in_star_facts(chart)
    assert any(r["planet"] == "Sun" for r in facts)
    assert any(r["planet"] == "Asc" for r in facts)

    out = run_nakshatra_nadi_engine(chart=chart, attempt_chains=True)
    assert out["engine"] == "NakshatraNadi"
    assert out["corpus_gate"]["corpus_status"] == "blocked"
    assert out["chains"] is None
    assert out["chain_error"]["code"] == "CORPUS_GATE_BLOCKED"
    assert len(out["planet_in_star"]) >= 9

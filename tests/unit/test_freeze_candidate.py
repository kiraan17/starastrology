"""Tests for freeze-candidate manifest and public API readiness (P24a)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from bhava360.api import (
    enable_public_api_surface,
    freeze_candidate_summary,
    load_freeze_candidate_manifest,
    public_api_readiness,
)
from bhava360.api.freeze_manifest import clear_manifest_cache
from bhava360.kernel.errors import KernelError, KernelErrorCode


def test_load_freeze_candidate_manifest():
    clear_manifest_cache()
    m = load_freeze_candidate_manifest()
    assert m["manifest_id"] == "FREEZE-CANDIDATE-v0.1"
    assert m["freeze_status"] == "candidate"
    assert m["frozen"] is False
    assert m["expert_approved"] is False
    assert m["public_api_eligible"] is False
    assert len(m["engines"]) >= 10
    assert m["blocked_reasons"]


def test_refuse_forged_frozen_manifest(tmp_path: Path):
    clear_manifest_cache()
    forged = {
        "manifest_id": "FORGED",
        "freeze_status": "candidate",
        "frozen": True,
        "expert_approved": False,
        "public_api_eligible": False,
        "engines": [],
    }
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(forged), encoding="utf-8")
    with pytest.raises(KernelError) as ei:
        load_freeze_candidate_manifest(str(path))
    assert ei.value.code == KernelErrorCode.UNSUPPORTED_CONFIG


def test_refuse_public_api_eligible_on_candidate(tmp_path: Path):
    clear_manifest_cache()
    forged = {
        "manifest_id": "FORGED2",
        "freeze_status": "candidate",
        "frozen": False,
        "expert_approved": False,
        "public_api_eligible": True,
        "engines": [],
    }
    path = tmp_path / "bad2.json"
    path.write_text(json.dumps(forged), encoding="utf-8")
    with pytest.raises(KernelError):
        load_freeze_candidate_manifest(str(path))


def test_public_api_readiness_includes_freeze_and_stays_blocked():
    clear_manifest_cache()
    readiness = public_api_readiness()
    assert readiness["ready"] is False
    assert "freeze_candidate" in readiness
    assert readiness["freeze_candidate"]["frozen"] is False
    assert readiness["freeze_candidate"]["public_api_eligible"] is False
    assert readiness["blocked_reasons"]
    with pytest.raises(KernelError) as ei:
        enable_public_api_surface()
    assert ei.value.code == KernelErrorCode.LICENSE_GATE_BLOCKED


def test_freeze_candidate_summary_shape():
    clear_manifest_cache()
    s = freeze_candidate_summary()
    assert s["manifest_id"]
    assert s["engine_count"] >= 10
    assert s["programme_gates"]["backend_freeze"] == "not_frozen"

"""Tests for ADR-002 Swiss Ephemeris public license gate."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from bhava360.api import enable_public_api_surface, public_api_readiness
from bhava360.kernel.errors import KernelError, KernelErrorCode
from bhava360.licensing import (
    assert_public_activation_allowed,
    is_public_api_allowed,
    load_se_license_status,
)


def test_default_status_is_blocked():
    status = load_se_license_status()
    assert status.public_activation == "blocked"
    assert status.public_api_allowed is False
    assert is_public_api_allowed() is False


def test_assert_public_activation_blocked(monkeypatch):
    monkeypatch.setenv("BHAVA360_PUBLIC_API", "1")
    with pytest.raises(KernelError) as exc:
        assert_public_activation_allowed()
    assert exc.value.code == KernelErrorCode.LICENSE_GATE_BLOCKED
    assert "ADR-002" in exc.value.message


def test_public_api_surface_blocked():
    readiness = public_api_readiness()
    assert readiness["ready"] is False
    with pytest.raises(KernelError) as exc:
        enable_public_api_surface()
    assert exc.value.code == KernelErrorCode.LICENSE_GATE_BLOCKED


def test_allowed_status_requires_evidence(tmp_path: Path):
    bad = tmp_path / "bad.json"
    bad.write_text(
        json.dumps(
            {
                "adr": "ADR-002",
                "public_activation": "allowed",
                "chosen_path": None,
                "evidence_ids": [],
                "approved_by": [],
                "approved_at": None,
                "notes": "incomplete",
                "schema_version": 1,
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(KernelError) as exc:
        load_se_license_status(bad)
    assert exc.value.code == KernelErrorCode.LICENSE_GATE_BLOCKED


def test_allowed_status_with_complete_evidence(tmp_path: Path):
    good = tmp_path / "good.json"
    good.write_text(
        json.dumps(
            {
                "adr": "ADR-002",
                "public_activation": "allowed",
                "chosen_path": "L2_COMMERCIAL",
                "evidence_ids": ["EVID-SE-L2-TEST"],
                "approved_by": ["legal:test", "product:test"],
                "approved_at": "2026-08-02T00:00:00Z",
                "notes": "test fixture only",
                "schema_version": 1,
            }
        ),
        encoding="utf-8",
    )
    status = assert_public_activation_allowed(status_path=good)
    assert status.public_api_allowed is True
    assert status.chosen_path == "L2_COMMERCIAL"

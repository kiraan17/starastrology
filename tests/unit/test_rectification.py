"""Unit tests for rectification toolkit scaffold (P22b / TEC-095)."""

from __future__ import annotations

from datetime import datetime

from bhava360.engines.rectification import run_rectification_engine
from bhava360.engines.rectification.scan import (
    kunda_from_lagna,
    normalize_manual_events,
    resolve_scan_grid,
)
from bhava360.kernel.models import SubjectInput


def test_kunda_is_lagna_times_81_mod_360():
    out = kunda_from_lagna(10.0)
    # 10 * 81 = 810 → 810 % 360 = 90 → Cancer 0°
    assert out["sign"] == "Cancer"
    assert abs(out["sign_degree"] - 0.0) < 1e-9


def test_resolve_scan_grid_includes_zero():
    grid = resolve_scan_grid(window_minutes=10, step_minutes=5)
    assert grid["offsets_minutes"][0] == -10.0
    assert 0.0 in grid["offsets_minutes"]
    assert grid["offsets_minutes"][-1] == 10.0
    assert len(grid["offsets_minutes"]) == 5


def test_resolve_scan_grid_widens_step_for_cap():
    grid = resolve_scan_grid(window_minutes=60, step_minutes=1, max_samples=7)
    assert grid["step_adjusted"] is True
    assert len(grid["offsets_minutes"]) <= 7


def test_manual_events_passthrough_unscored():
    out = normalize_manual_events("Marriage|2015-06-01, Job|2018-01-15")
    assert out["provided"] is True
    assert out["status"] == "passthrough_unscored"
    assert len(out["events"]) == 2
    assert out["events"][0]["label"] == "Marriage"


def test_engine_scan_no_winner():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_offset_minutes=330,
        latitude=13.0827,
        longitude=80.2707,
        birth_time_uncertainty_minutes=10.0,
    )
    out = run_rectification_engine(
        subject,
        step_minutes=5,
        events="Marriage|2015-06-01",
    )
    assert out["engine"] == "Rectification"
    assert out["safety_level"] == "restricted"
    assert "TEC-095" in out["technique_ids"]
    scan = out["scan"]
    assert scan["grid"]["window_minutes"] == 10.0
    assert scan["summary"]["winner_selected"] is False
    assert out["safety"]["winner_selected"] is False
    assert out["safety"]["events_scored"] is False
    assert scan["manual_events"]["provided"] is True
    assert scan["summary"]["sample_count"] >= 3
    assert any(s["is_baseline"] for s in scan["samples"])
    baseline = scan["baseline"]["fingerprint"]
    assert baseline["lagna_sign"]
    assert baseline["kunda_sign"]
    assert baseline["d9_lagna_sign"]

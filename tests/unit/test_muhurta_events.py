"""Unit tests for muhurta event rule packs (P20b / TEC-093)."""

from __future__ import annotations

from datetime import datetime

from bhava360.kernel.models import SubjectInput
from bhava360.timing.event_rules import evaluate_activity, evaluate_event_pack
from bhava360.timing.muhurta_event_engine import run_muhurta_event_engine


def test_evaluate_activity_avoid_on_rahu_kala():
    out = evaluate_activity(
        activity_id="general",
        panchanga={"karana": {"name": "Bava"}, "tithi": {"index": 5}},
        muhurta_active={"rahu_kala": True, "yamaganda": False, "gulika": False},
        moon_tara={"tara": "Vipat", "auspicious": False},
    )
    assert out["verdict"] == "avoid"
    assert any("Rahu Kala" in r for r in out["reasons"])


def test_evaluate_activity_good_on_abhijit():
    out = evaluate_activity(
        activity_id="meeting",
        panchanga={"karana": {"name": "Bava"}, "tithi": {"index": 5}},
        muhurta_active={
            "rahu_kala": False,
            "yamaganda": False,
            "gulika": False,
            "abhijit": True,
            "chaughadiya": {"label": "Amrit"},
        },
        moon_tara={"tara": "Sampat", "auspicious": True},
    )
    assert out["verdict"] == "good"


def test_evaluate_event_pack_summary():
    pack = evaluate_event_pack(
        panchanga={"karana": {"name": "Vishti"}, "tithi": {"index": 14}},
        muhurta={"active": {"rahu_kala": False, "yamaganda": False, "gulika": False}},
        bala={"tara_from_moon": {"Moon": {"tara": "Vipat", "auspicious": False}}},
        activities=["travel", "general"],
    )
    assert "travel" in pack["summary"]["avoid"] or "travel" in pack["summary"]["mixed"]
    assert len(pack["results"]) == 2


def test_muhurta_event_engine_live():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_id="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
    )
    out = run_muhurta_event_engine(subject)
    assert out["engine"] == "MuhurtaEvents"
    assert "TEC-093" in out["technique_ids"]
    assert out["event_pack"]["summary"]
    assert len(out["event_pack"]["results"]) == 5
    assert out["safety"]["note"]

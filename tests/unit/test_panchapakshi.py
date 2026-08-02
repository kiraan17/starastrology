"""Unit tests for Panchapakshi (P26b / TEC-075)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from bhava360.kernel.models import SubjectInput
from bhava360.timing.panchapakshi import (
    birth_bird_from_nakshatra,
    build_yama_clock,
    evaluate_panchapakshi,
)
from bhava360.timing.panchapakshi_engine import run_panchapakshi_engine


def test_birth_bird_shukla_ashwini_vulture():
    out = birth_bird_from_nakshatra(nakshatra_index=1, paksha="Shukla")
    assert out["bird"] == "Vulture"
    assert out["element"] == "Fire"


def test_birth_bird_krishna_ashwini_peacock():
    out = birth_bird_from_nakshatra(nakshatra_index=1, paksha="Krishna")
    assert out["bird"] == "Peacock"


def test_birth_bird_shukla_revathi_peacock():
    out = birth_bird_from_nakshatra(nakshatra_index=27, paksha="Shukla")
    assert out["bird"] == "Peacock"


def test_yama_clock_ten_segments():
    sunrise = datetime(2024, 8, 15, 6, 0)
    sunset = datetime(2024, 8, 15, 18, 0)
    next_rise = datetime(2024, 8, 16, 6, 0)
    when = datetime(2024, 8, 15, 7, 0, tzinfo=timezone.utc)
    # Treat naive locals as UTC for this unit check.
    clock = build_yama_clock(
        sunrise=sunrise.replace(tzinfo=timezone.utc),
        sunset=sunset.replace(tzinfo=timezone.utc),
        next_sunrise=next_rise.replace(tzinfo=timezone.utc),
        when_utc=when,
    )
    assert len(clock["yamas"]) == 10
    assert clock["active"]["yama_index"] == 1
    assert clock["active"]["phase"] == "day"


def test_evaluate_shukla_has_activity_schedule():
    sunrise = datetime(1990, 8, 15, 6, 0)
    sunset = datetime(1990, 8, 15, 18, 0)
    next_rise = datetime(1990, 8, 16, 6, 0)
    # Wednesday 1990-08-15 → bright group B
    out = evaluate_panchapakshi(
        moon_lon_sidereal=10.0,  # Aswini → Vulture in Shukla
        paksha="Shukla",
        sunrise=sunrise,
        sunset=sunset,
        next_sunrise=next_rise,
        when_utc=datetime(1990, 8, 15, 7, 0, tzinfo=timezone.utc),
    )
    assert out["birth_bird"]["bird"] == "Vulture"
    assert out["summary"]["activity"] is not None
    assert out["summary"]["schedule_count"] == 10
    assert out["bright_half_group"] == "B"
    # Group B day yama 1 for Vulture = Dying
    assert out["current"]["activity"] == "Dying"
    assert out["current"]["activity_class"] == "avoid"


def test_evaluate_krishna_defers_activity():
    sunrise = datetime(1990, 8, 15, 6, 0)
    sunset = datetime(1990, 8, 15, 18, 0)
    next_rise = datetime(1990, 8, 16, 6, 0)
    out = evaluate_panchapakshi(
        moon_lon_sidereal=10.0,
        paksha="Krishna",
        sunrise=sunrise,
        sunset=sunset,
        next_sunrise=next_rise,
        when_utc=datetime(1990, 8, 15, 12, 0, tzinfo=timezone.utc),
    )
    assert out["birth_bird"]["bird"] == "Peacock"
    assert out["summary"]["dark_half_activity_deferred"] is True
    assert out["summary"]["activity"] is None
    assert out["summary"]["schedule_count"] == 0
    assert any("Source Needed" in d for d in out["deferred"])


def test_panchapakshi_engine_live():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_id="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
    )
    out = run_panchapakshi_engine(subject)
    assert out["engine"] == "Panchapakshi"
    assert "TEC-075" in out["technique_ids"]
    pack = out["panchapakshi"]
    assert pack["birth_bird"]["bird"] in {
        "Vulture",
        "Owl",
        "Crow",
        "Cock",
        "Peacock",
    }
    assert pack["summary"]["bird"]
    assert out["safety"]["note"]

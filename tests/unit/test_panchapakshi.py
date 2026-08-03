"""Unit tests for Panchapakshi (P26b/P27a / TEC-075)."""

from __future__ import annotations

from datetime import datetime, timezone

from bhava360.kernel.models import SubjectInput
from bhava360.timing.panchapakshi import (
    birth_bird_from_nakshatra,
    build_yama_clock,
    evaluate_panchapakshi,
    lookup_major_activity,
)
from bhava360.timing.panchapakshi_engine import run_panchapakshi_engine


def test_birth_bird_shukla_ashwini_vulture():
    out = birth_bird_from_nakshatra(nakshatra_index=1, paksha="Shukla")
    assert out["bird"] == "Vulture"
    assert out["element"] == "Fire"


def test_birth_bird_krishna_ashwini_peacock():
    out = birth_bird_from_nakshatra(nakshatra_index=1, paksha="Krishna")
    assert out["bird"] == "Peacock"


def test_birth_bird_pyjhora_purva_phalguni_owl_shukla():
    # Nak 11 (Pubba) is Owl in PyJHora Shukla (group 6–11).
    out = birth_bird_from_nakshatra(nakshatra_index=11, paksha="Shukla")
    assert out["bird"] == "Owl"
    # Nak 12 (Uttara) starts Crow group.
    assert birth_bird_from_nakshatra(nakshatra_index=12, paksha="Shukla")["bird"] == "Crow"


def test_birth_bird_shukla_revathi_peacock():
    out = birth_bird_from_nakshatra(nakshatra_index=27, paksha="Shukla")
    assert out["bird"] == "Peacock"


def test_yama_clock_ten_segments():
    sunrise = datetime(2024, 8, 15, 6, 0, tzinfo=timezone.utc)
    sunset = datetime(2024, 8, 15, 18, 0, tzinfo=timezone.utc)
    next_rise = datetime(2024, 8, 16, 6, 0, tzinfo=timezone.utc)
    when = datetime(2024, 8, 15, 7, 0, tzinfo=timezone.utc)
    clock = build_yama_clock(
        sunrise=sunrise,
        sunset=sunset,
        next_sunrise=next_rise,
        when_utc=when,
    )
    assert len(clock["yamas"]) == 10
    assert clock["active"]["yama_index"] == 1
    assert clock["active"]["phase"] == "day"


def test_pyjhora_shukla_sun_vulture_day1_eating():
    assert (
        lookup_major_activity(
            paksha="Shukla", weekday_sunday_index=0, bird="Vulture", yama_index=1
        )
        == "Eating"
    )


def test_evaluate_shukla_has_activity_schedule():
    sunrise = datetime(1990, 8, 15, 6, 0)
    sunset = datetime(1990, 8, 15, 18, 0)
    next_rise = datetime(1990, 8, 16, 6, 0)
    # Wednesday 1990-08-15
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
    assert out["summary"]["dark_half_activity_deferred"] is False
    # Wed Shukla Vulture yama 1 = Dying (PyJHora)
    assert out["current"]["activity"] == "Dying"
    assert out["current"]["activity_class"] == "avoid"


def test_evaluate_krishna_has_activity():
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
    assert out["summary"]["dark_half_activity_deferred"] is False
    assert out["summary"]["activity"] is not None
    assert out["summary"]["schedule_count"] == 10
    # Wed Krishna Peacock yama 3 (midday ~12:00) = Dying
    assert out["current"]["yama_index"] == 3
    assert out["current"]["activity"] == "Dying"


def test_panchapakshi_engine_live():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_id="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
    )
    out = run_panchapakshi_engine(subject)
    assert out["engine"] == "Panchapakshi"
    assert out["engine_version"] == "0.2.0-both-paksha"
    assert "TEC-075" in out["technique_ids"]
    pack = out["panchapakshi"]
    assert pack["birth_bird"]["bird"] in {
        "Vulture",
        "Owl",
        "Crow",
        "Cock",
        "Peacock",
    }
    assert pack["summary"]["schedule_count"] == 10
    assert pack["summary"]["activity"]
    assert out["safety"]["note"]

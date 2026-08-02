"""Tests for P16b muhurta windows."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from bhava360.kernel.models import SubjectInput
from bhava360.timing.muhurta import (
    compute_abhijit,
    compute_chaughadiya,
    compute_day_eighth_windows,
    compute_horas,
    compute_muhurta_pack,
    sunday_index,
)
from bhava360.timing.panchanga_engine import run_panchanga_engine


def test_wednesday_rahu_kala_is_fifth_eighth():
    # 1990-08-15 Wednesday → Rahu Kala 5th eighth
    sunrise = datetime(1990, 8, 15, 6, 0, tzinfo=timezone.utc)
    sunset = datetime(1990, 8, 15, 18, 0, tzinfo=timezone.utc)
    wd = sunday_index(sunrise)
    assert wd == 3  # Wednesday
    eighths = compute_day_eighth_windows(
        sunrise=sunrise, sunset=sunset, weekday_sunday_index=wd
    )
    assert eighths["rahu_kala"]["part"] == 5
    # 12h day / 8 = 1.5h; 5th starts at 6+6=12:00 UTC
    assert eighths["rahu_kala"]["start_utc"].startswith("1990-08-15T12:00:00")
    assert eighths["yamaganda"]["part"] == 2
    assert eighths["gulika"]["part"] == 4


def test_abhijit_centered_midday():
    sunrise = datetime(1990, 8, 15, 6, 0, tzinfo=timezone.utc)
    sunset = datetime(1990, 8, 15, 18, 0, tzinfo=timezone.utc)
    ab = compute_abhijit(sunrise=sunrise, sunset=sunset)
    assert ab["midday_utc"].startswith("1990-08-15T12:00:00")
    assert abs(ab["duration_minutes"] - 48.0) < 1e-6  # 12h/15 = 48m


def test_hora_starts_with_weekday_lord():
    sunrise = datetime(1990, 8, 15, 6, 0, tzinfo=timezone.utc)  # Wed → Mercury
    sunset = datetime(1990, 8, 15, 18, 0, tzinfo=timezone.utc)
    next_rise = datetime(1990, 8, 16, 6, 0, tzinfo=timezone.utc)
    horas = compute_horas(
        sunrise=sunrise,
        sunset=sunset,
        next_sunrise=next_rise,
        weekday_sunday_index=3,
    )
    assert horas["horas"][0]["lord"] == "Mercury"
    assert horas["horas"][1]["lord"] == "Moon"
    assert len(horas["horas"]) == 24


def test_chaughadiya_sixteen_segments():
    sunrise = datetime(1990, 8, 15, 6, 0, tzinfo=timezone.utc)
    sunset = datetime(1990, 8, 15, 18, 0, tzinfo=timezone.utc)
    next_rise = datetime(1990, 8, 16, 6, 0, tzinfo=timezone.utc)
    ch = compute_chaughadiya(
        sunrise=sunrise,
        sunset=sunset,
        next_sunrise=next_rise,
        weekday_sunday_index=3,
    )
    assert len(ch["segments"]) == 16
    assert ch["segments"][0]["label"] == "Labh"


def test_active_flags_in_pack():
    sunrise = datetime(1990, 8, 15, 6, 0, tzinfo=timezone.utc)
    sunset = datetime(1990, 8, 15, 18, 0, tzinfo=timezone.utc)
    next_rise = datetime(1990, 8, 16, 6, 0, tzinfo=timezone.utc)
    when = datetime(1990, 8, 15, 12, 30, tzinfo=timezone.utc)  # in Wed Rahu Kala
    pack = compute_muhurta_pack(
        sunrise=sunrise,
        sunset=sunset,
        next_sunrise=next_rise,
        when_utc=when,
    )
    assert pack["active"]["rahu_kala"] is True
    assert pack["active"]["hora"]["lord"]
    assert pack["active"]["chaughadiya"]["label"]


def test_engine_includes_muhurta():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_id="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
        location_label="Chennai",
    )
    out = run_panchanga_engine(subject)
    assert out["engine_version"] == "0.2.0-muhurta"
    assert "TEC-071" in out["technique_ids"]
    assert "TEC-073" in out["technique_ids"]
    assert out["muhurta"]["day_eighths"]["rahu_kala"]["name"] == "Rahu Kala"
    assert out["muhurta"]["active"]["hora"] is not None

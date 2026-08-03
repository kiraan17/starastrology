"""Unit tests for Tajika Sahams and aspects (P17c / TEC-078)."""

from __future__ import annotations

from datetime import datetime

import pytest

from bhava360.engines.tajika import run_tajika_annual_engine
from bhava360.engines.tajika.aspects_tajika import (
    circular_separation,
    compute_tajika_aspects,
    match_tajika_aspect,
)
from bhava360.engines.tajika.sahams import compute_sahams, is_day_chart, saham_longitude
from bhava360.kernel.models import SubjectInput


def test_saham_longitude_formula():
    # Asc 10 + Moon 50 − Sun 20 = 40
    assert abs(saham_longitude(asc=10.0, plus=50.0, minus=20.0) - 40.0) < 1e-9


def test_is_day_chart():
    assert is_day_chart(
        local_iso="2020-08-15 12:00:00",
        sunrise_local="2020-08-15 06:00:00",
        sunset_local="2020-08-15 18:00:00",
    )
    assert not is_day_chart(
        local_iso="2020-08-15 20:00:00",
        sunrise_local="2020-08-15 06:00:00",
        sunset_local="2020-08-15 18:00:00",
    )


def test_compute_sahams_punya_day_night_reverse():
    planets = [
        {"planet": "Sun", "longitude_sidereal_deg": 20.0},
        {"planet": "Moon", "longitude_sidereal_deg": 50.0},
        {"planet": "Mars", "longitude_sidereal_deg": 80.0},
        {"planet": "Jupiter", "longitude_sidereal_deg": 100.0},
        {"planet": "Venus", "longitude_sidereal_deg": 40.0},
        {"planet": "Saturn", "longitude_sidereal_deg": 200.0},
    ]
    day = compute_sahams(ascendant_longitude=10.0, planets=planets, is_day=True)
    night = compute_sahams(ascendant_longitude=10.0, planets=planets, is_day=False)
    punya_day = next(s for s in day["sahams"] if s["id"] == "punya")
    punya_night = next(s for s in night["sahams"] if s["id"] == "punya")
    assert punya_day["formula"]["expression"] == "Asc + Moon - Sun"
    assert punya_night["formula"]["expression"] == "Asc + Sun - Moon"
    assert abs(punya_day["longitude_sidereal_deg"] - 40.0) < 1e-9
    assert abs(punya_night["longitude_sidereal_deg"] - (-20.0 % 360.0)) < 1e-9
    assert len(day["sahams"]) == 5


def test_match_tajika_aspect_orbs():
    conj = match_tajika_aspect(3.0)
    assert conj is not None and conj["aspect"] == "conjunction"
    trine = match_tajika_aspect(122.0)
    assert trine is not None and trine["aspect"] == "trine"
    assert match_tajika_aspect(45.0) is None


def test_compute_tajika_aspects_finds_opposition():
    planets = [
        {"planet": "Sun", "longitude_sidereal_deg": 10.0, "speed_longitude": 1.0},
        {"planet": "Moon", "longitude_sidereal_deg": 40.0, "speed_longitude": 13.0},
        {"planet": "Mars", "longitude_sidereal_deg": 190.0, "speed_longitude": 0.5},
        {"planet": "Mercury", "longitude_sidereal_deg": 15.0, "speed_longitude": 1.2},
        {"planet": "Jupiter", "longitude_sidereal_deg": 100.0, "speed_longitude": 0.1},
        {"planet": "Venus", "longitude_sidereal_deg": 70.0, "speed_longitude": 1.1},
        {"planet": "Saturn", "longitude_sidereal_deg": 200.0, "speed_longitude": 0.05},
    ]
    out = compute_tajika_aspects(planets)
    assert out["variant"] == "tajika_aspects_candidate_v1"
    names = {(a["from_planet"], a["to_planet"], a["aspect"]) for a in out["aspects"]}
    assert ("Sun", "Mars", "opposition") in names
    assert circular_separation(10.0, 190.0) == 180.0


def test_engine_includes_sahams_and_aspects():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_offset_minutes=330,
        latitude=13.0827,
        longitude=80.2707,
        location_label="Chennai",
    )
    out = run_tajika_annual_engine(subject, target_year=2020)
    assert out["engine_version"] == "0.3.0-sahams-aspects"
    assert "TEC-078" in out["technique_ids"]
    assert out["sahams"]["variant"] == "tajika_saham_candidate_v1"
    assert len(out["sahams"]["sahams"]) == 5
    assert out["tajika_aspects"]["variant"] == "tajika_aspects_candidate_v1"
    assert isinstance(out["tajika_aspects"]["aspects"], list)
    assert "Sahams (TEC-078)" not in out["deferred"]

"""Unit tests for Bhrigu Bindu (P18b / TEC-081)."""

from __future__ import annotations

from datetime import datetime

from bhava360.engines.progression import run_bhrigu_bindu_engine
from bhava360.engines.progression.bhrigu_bindu import (
    circular_midpoint,
    compute_bhrigu_bindu,
    transit_hits_on_bindu,
)
from bhava360.kernel.models import SubjectInput


def test_circular_midpoint_simple():
    assert abs(circular_midpoint(10.0, 50.0) - 30.0) < 1e-9


def test_circular_midpoint_across_zero():
    # Shorter arc from 350 to 10 is +20 → mid at 0
    mid = circular_midpoint(350.0, 10.0)
    assert abs(mid - 0.0) < 1e-9 or abs(mid - 360.0) < 1e-9


def test_compute_bhrigu_bindu_fields():
    out = compute_bhrigu_bindu(
        moon_longitude=100.0,
        rahu_longitude=160.0,
        lagna_longitude=10.0,
        planet_longitudes={"Sun": 130.0, "Mars": 200.0},
        conjunction_orb_deg=1.0,
    )
    assert abs(out["longitude_sidereal_deg"] - 130.0) < 1e-9
    assert out["sign"] == "Leo"
    assert out["house_from_lagna"] == 5  # Leo from Aries lagna ~10°
    assert out["natal_conjunctions"][0]["planet"] == "Sun"
    assert out["variant"] == "bhrigu_bindu_candidate_v1"


def test_transit_hits_on_bindu():
    hits = transit_hits_on_bindu(
        bindu_longitude=130.0,
        transit_longitudes={"Jupiter": 130.4, "Saturn": 200.0},
        orb_deg=1.0,
    )
    assert len(hits) == 1
    assert hits[0]["planet"] == "Jupiter"


def test_bhrigu_bindu_engine_live():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_offset_minutes=330,
        latitude=13.0827,
        longitude=80.2707,
        location_label="Chennai",
    )
    out = run_bhrigu_bindu_engine(subject)
    assert out["engine"] == "BhriguBindu"
    assert "TEC-081" in out["technique_ids"]
    bb = out["bhrigu_bindu"]
    assert 0 <= bb["longitude_sidereal_deg"] < 360
    assert bb["sign"]
    assert bb["nakshatra_label"]
    assert 1 <= bb["house_from_lagna"] <= 12
    assert out["transit_evaluated"] is False

    # Transit using natal positions as fake transit should report Moon/Rahu near-ish only if on BB
    with_transit = run_bhrigu_bindu_engine(
        chart=None,
        subject=subject,
        transit_longitudes={
            "Jupiter": bb["longitude_sidereal_deg"],
            "Saturn": (bb["longitude_sidereal_deg"] + 90.0) % 360.0,
        },
    )
    assert with_transit["transit_evaluated"] is True
    assert any(h["planet"] == "Jupiter" for h in with_transit["transit_hits"])

"""Unit tests for Tara / Kota / Sarvatobhadra scaffolds (P18c)."""

from __future__ import annotations

from datetime import datetime

from bhava360.engines.chakra import run_nakshatra_chakra_engine
from bhava360.engines.chakra.nakshatra_chakras import (
    build_kota_chakra,
    build_sarvatobhadra_rim,
    build_tara_chakra,
)
from bhava360.kernel.models import SubjectInput


def test_tara_chakra_moon_is_janma():
    # Moon at start of Aswini; planet also Aswini → Janma
    out = build_tara_chakra(
        moon_longitude=1.0,
        planet_longitudes={"Moon": 1.0, "Sun": 1.0, "Mars": 40.0},
    )
    assert out["variant"] == "tara_chakra_candidate_v1"
    assert len(out["spokes"]) == 9
    moon = next(p for p in out["planets"] if p["planet"] == "Moon")
    assert moon["tara"] == "Janma"
    assert "Moon" in out["spokes"][0]["occupants"]


def test_kota_chakra_27_slots_eight_directions():
    out = build_kota_chakra(
        planet_longitudes={"Sun": 10.0, "Moon": 100.0},
    )
    assert out["variant"] == "kota_chakra_candidate_v1"
    assert len(out["slots"]) == 27
    assert set(out["by_direction"]) == {
        "east",
        "southeast",
        "south",
        "southwest",
        "west",
        "northwest",
        "north",
        "northeast",
    }
    assert sum(len(v) for v in out["by_direction"].values()) == 27
    sun = next(p for p in out["planets"] if p["planet"] == "Sun")
    assert sun["direction"] == "east"  # Aswini in east bank


def test_sarvatobhadra_rim_defers_vedha():
    out = build_sarvatobhadra_rim(planet_longitudes={"Jupiter": 200.0})
    assert len(out["rim"]) == 27
    assert out["vedha"]["status"] == "deferred"
    assert out["planets"][0]["planet"] == "Jupiter"


def test_nakshatra_chakra_engine_live():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_offset_minutes=330,
        latitude=13.0827,
        longitude=80.2707,
        location_label="Chennai",
    )
    out = run_nakshatra_chakra_engine(subject)
    assert out["engine"] == "NakshatraChakras"
    assert "TEC-082" in out["technique_ids"]
    assert "TEC-083" in out["technique_ids"]
    assert len(out["tara_chakra"]["spokes"]) == 9
    assert len(out["kota_chakra"]["slots"]) == 27
    assert out["sarvatobhadra"]["vedha"]["status"] == "deferred"

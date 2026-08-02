"""Unit tests for transit natal overlay (P25b / TEC-035)."""

from __future__ import annotations

from datetime import datetime

from bhava360.engines.transit import run_transit_engine
from bhava360.engines.transit.compare import house_from_reference, transit_placements
from bhava360.kernel.models import SubjectInput


def test_house_from_reference():
    assert house_from_reference("Aries", "Aries") == 1
    assert house_from_reference("Aries", "Libra") == 7
    assert house_from_reference("Cancer", "Aries") == 10


def test_transit_engine_overlay():
    natal = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_offset_minutes=330,
        latitude=13.0827,
        longitude=80.2707,
    )
    transit = SubjectInput(
        local_datetime=datetime(2024, 8, 15, 12, 0),
        timezone_offset_minutes=330,
        latitude=13.0827,
        longitude=80.2707,
    )
    out = run_transit_engine(natal, transit)
    assert out["engine"] == "Transit"
    assert "TEC-035" in out["technique_ids"]
    overlay = out["overlay"]
    assert len(overlay["placements"]) == 9
    assert len(overlay["houses_from_natal_lagna"]) == 12
    assert overlay["summary"]["placement_count"] == 9
    assert isinstance(overlay["conjunctions"], list)
    assert isinstance(overlay["aspects_transit_to_natal"], list)
    assert out["natal_ref"]["lagna_sign"]
    assert out["transit_ref"]["local_datetime"]


def test_placements_include_moon_houses():
    rows = transit_placements(
        natal_lagna_sign="Aries",
        natal_moon_sign="Cancer",
        transit_planets={
            "Jupiter": {"sign": "Aries", "sign_degree": 1.0, "longitude_sidereal_deg": 1.0},
        },
    )
    assert rows[0]["house_from_natal_lagna"] == 1
    assert rows[0]["house_from_natal_moon"] == 10

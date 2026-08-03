"""Unit tests for Lal Kitab Teva scaffold (P22a / TEC-090)."""

from __future__ import annotations

from datetime import datetime

from bhava360.engines.lal_kitab import run_lal_kitab_engine
from bhava360.engines.lal_kitab.teva import (
    annual_teva_house,
    aspect_houses_from,
    teva_house_from_sign,
)
from bhava360.kernel.models import SubjectInput


def test_teva_house_fixed_aries():
    assert teva_house_from_sign("Aries") == 1
    assert teva_house_from_sign("Cancer") == 4
    assert teva_house_from_sign("Pisces") == 12


def test_mars_aspects_from_house_3():
    # Mars in 3 aspects 6, 9, 10
    assert aspect_houses_from("Mars", 3) == [6, 9, 10]


def test_varshphal_arithmetic():
    # natal 3, age 35 → house 2
    assert annual_teva_house(3, 35) == 2
    assert annual_teva_house(1, 0) == 1
    assert annual_teva_house(12, 1) == 1


def test_engine_teva_and_varshphal():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_offset_minutes=330,
        latitude=13.0827,
        longitude=80.2707,
    )
    out = run_lal_kitab_engine(subject, target_year=2024)
    assert out["engine"] == "LalKitab"
    assert out["safety_level"] == "restricted"
    assert "TEC-090" in out["technique_ids"]
    teva = out["teva"]
    assert teva["teva_basis"] == "fixed_aries_house_1"
    assert len(teva["planets"]) == 9
    assert len(teva["houses"]) == 12
    sun = next(p for p in teva["planets"] if p["planet"] == "Sun")
    assert sun["teva_house"] == teva_house_from_sign(sun["sign"])
    assert teva["varshphal"] is not None
    assert teva["varshphal"]["age"] == 34
    assert out["safety"]["remedies_emitted"] is False
    assert teva["contradictions"]["diff_count"] >= 0


def test_engine_age_override():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_offset_minutes=330,
        latitude=13.0827,
        longitude=80.2707,
    )
    out = run_lal_kitab_engine(subject, age=12)
    assert out["teva"]["varshphal"]["age"] == 12
    # After 12 years every planet returns to natal house
    for row in out["teva"]["varshphal"]["planets"]:
        assert row["annual_teva_house"] == row["natal_teva_house"]

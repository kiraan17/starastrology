"""Unit tests for Systems Approach scaffold (P21b / TEC-091)."""

from __future__ import annotations

from datetime import datetime

from bhava360.engines.systems_approach import run_systems_approach_engine
from bhava360.engines.systems_approach.config import (
    classify_functional_natures,
    house_of_sign_from_lagna,
)
from bhava360.kernel.models import SubjectInput


def test_house_of_sign_from_lagna():
    assert house_of_sign_from_lagna("Aries", "Virgo") == 6
    assert house_of_sign_from_lagna("Taurus", "Aries") == 12


def test_functional_malefics_aries():
    out = classify_functional_natures("Aries")
    assert set(out["functional_malefics"]) == {"Mercury", "Rahu", "Ketu"}
    assert "Sun" in out["functional_benefics"]
    assert "Mars" in out["functional_benefics"]


def test_functional_malefics_gemini_only_nodes():
    out = classify_functional_natures("Gemini")
    assert set(out["functional_malefics"]) == {"Rahu", "Ketu"}
    assert len(out["functional_benefics"]) == 7


def test_functional_malefics_taurus():
    out = classify_functional_natures("Taurus")
    assert set(out["functional_malefics"]) == {
        "Venus",
        "Jupiter",
        "Mars",
        "Rahu",
        "Ketu",
    }


def test_functional_malefics_virgo():
    out = classify_functional_natures("Virgo")
    assert set(out["functional_malefics"]) == {
        "Saturn",
        "Mars",
        "Sun",
        "Rahu",
        "Ketu",
    }


def test_engine_scaffold():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_offset_minutes=330,
        latitude=13.0827,
        longitude=80.2707,
    )
    out = run_systems_approach_engine(subject)
    assert out["engine"] == "SystemsApproach"
    assert "TEC-091" in out["technique_ids"]
    profile = out["profile"]
    assert profile["lagna_sign"]
    assert len(profile["planets"]) == 9
    assert len(profile["houses"]) == 12
    assert profile["summary"]["functional_malefic_count"] >= 2
    assert out["safety"]["note"]
    assert out["config"]["moon_mooltrikona_sign"] == "Cancer"

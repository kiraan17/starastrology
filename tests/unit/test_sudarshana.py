"""Unit tests for Sudarshana Chakra scaffold (P18a / TEC-080)."""

from __future__ import annotations

from datetime import datetime

from bhava360.engines.chakra import run_sudarshana_engine
from bhava360.engines.chakra.sudarshana import (
    build_sudarshana_wheel,
    house_from_reference,
    sign_for_house,
)
from bhava360.kernel.models import SubjectInput


def test_house_from_reference():
    assert house_from_reference(reference_sign="Aries", body_sign="Aries") == 1
    assert house_from_reference(reference_sign="Aries", body_sign="Libra") == 7
    assert house_from_reference(reference_sign="Leo", body_sign="Aries") == 9


def test_sign_for_house():
    assert sign_for_house(reference_sign="Aries", house=1) == "Aries"
    assert sign_for_house(reference_sign="Aries", house=5) == "Leo"
    assert sign_for_house(reference_sign="Capricorn", house=4) == "Aries"


def test_build_sudarshana_wheel_tri_view():
    wheel = build_sudarshana_wheel(
        lagna_sign="Aries",
        sun_sign="Leo",
        moon_sign="Cancer",
        planet_signs={
            "Sun": "Leo",
            "Moon": "Cancer",
            "Mars": "Aries",
            "Mercury": "Virgo",
            "Jupiter": "Sagittarius",
            "Venus": "Libra",
            "Saturn": "Capricorn",
        },
    )
    assert wheel["variant"] == "sudarshana_thin_candidate_v1"
    assert wheel["references"]["lagna"]["sign"] == "Aries"
    assert wheel["references"]["chandra"]["sign"] == "Cancer"
    assert wheel["references"]["surya"]["sign"] == "Leo"
    mars = next(p for p in wheel["planets"] if p["planet"] == "Mars")
    assert mars["house_from_lagna"] == 1
    assert mars["house_from_chandra"] == 10  # Aries from Cancer
    assert mars["house_from_surya"] == 9  # Aries from Leo
    assert len(wheel["tri_view"]) == 12
    # House 1 from Lagna should include Mars
    assert "Mars" in wheel["tri_view"][0]["from_lagna"]["occupants"]


def test_sudarshana_engine_on_live_chart():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_offset_minutes=330,
        latitude=13.0827,
        longitude=80.2707,
        location_label="Chennai",
    )
    out = run_sudarshana_engine(subject)
    assert out["engine"] == "SudarshanaChakra"
    assert out["school"] == "chakra"
    assert "TEC-080" in out["technique_ids"]
    sud = out["sudarshana"]
    assert sud["references"]["lagna"]["sign"]
    assert sud["references"]["chandra"]["sign"]
    assert sud["references"]["surya"]["sign"]
    assert len(sud["planets"]) >= 7
    assert len(sud["wheels"]["lagna"]["houses"]) == 12

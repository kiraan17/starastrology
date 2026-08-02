"""Unit tests for Yogini dasha (P25a / TEC-031)."""

from __future__ import annotations

from datetime import datetime

from bhava360.kernel.models import SubjectInput
from bhava360.timing.yogini import (
    YOGINI_YEARS,
    yogini_balance,
    yogini_from_nakshatra_number,
)
from bhava360.timing.yogini_engine import run_yogini_dasha_engine


def test_yogini_start_ashwini_is_bhramari():
    # Ashwini=1 → (1+3)%8=4 → Bhramari
    assert yogini_from_nakshatra_number(1) == "Bhramari"


def test_yogini_start_bharani_is_bhadrika():
    assert yogini_from_nakshatra_number(2) == "Bhadrika"


def test_yogini_cycle_totals_36():
    assert sum(YOGINI_YEARS.values()) == 36


def test_yogini_balance_and_engine():
    # Moon ~ Rohini (nak 4) → number 4 → (4+3)%8=7 → Siddha
    # Rohini spans 40°–53°20'; use mid Rohini ~46.67
    bal = yogini_balance(46.67)
    assert bal.nakshatra == "Rohini"
    assert bal.nakshatra_number == 4
    assert bal.yogini == "Siddha"
    assert bal.lord.value == "Venus"
    assert 0 < bal.balance_years <= 7

    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_offset_minutes=330,
        latitude=13.0827,
        longitude=80.2707,
    )
    out = run_yogini_dasha_engine(subject, years_ahead=36, include_antar=True)
    assert out["engine"] == "YoginiDasha"
    assert "TEC-031" in out["technique_ids"]
    tree = out["yogini"]
    assert tree["balance"]["yogini"]
    assert len(tree["levels"]["maha"]) >= 1
    assert tree["levels"]["maha"][0]["yogini"] == tree["balance"]["yogini"]
    assert len(tree["levels"]["antar"]) >= 8

"""Unit tests for Ashtakoota compatibility (P20a / TEC-094)."""

from __future__ import annotations

from datetime import datetime

from bhava360.engines.compatibility import run_compatibility_engine
from bhava360.engines.compatibility.ashtakoota import compute_ashtakoota, score_nadi
from bhava360.kernel.models import SubjectInput


def test_ashtakoota_same_moon_high_some_kutas():
    # Identical moons: Nadi dosha (0) but many others full
    out = compute_ashtakoota(boy_moon_longitude=100.0, girl_moon_longitude=100.0)
    assert out["max_total"] == 36.0
    assert len(out["kutas"]) == 8
    nadi = next(k for k in out["kutas"] if k["kuta"] == "Nadi")
    assert nadi["points"] == 0.0
    assert out["total"] < 36.0


def test_nadi_different_scores_full():
    # Aswini (0)=Adi vs Bharani (1)=Madhya
    out = score_nadi(boy_nak_idx=0, girl_nak_idx=1)
    assert out["points"] == 8.0


def test_compatibility_engine_two_subjects():
    boy = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_offset_minutes=330,
        latitude=13.0827,
        longitude=80.2707,
    )
    girl = SubjectInput(
        local_datetime=datetime(1992, 3, 10, 9, 30),
        timezone_offset_minutes=330,
        latitude=12.9716,
        longitude=77.5946,
    )
    out = run_compatibility_engine(boy, girl)
    assert out["engine"] == "Compatibility"
    assert "TEC-094" in out["technique_ids"]
    ak = out["ashtakoota"]
    assert 0 <= ak["total"] <= 36
    assert ak["boy"]["nakshatra"]
    assert ak["girl"]["nakshatra"]
    assert out["safety"]["note"]


def test_compatibility_from_longitudes():
    out = run_compatibility_engine(
        boy_moon_longitude=10.0,
        girl_moon_longitude=200.0,
    )
    assert out["ashtakoota"]["total"] >= 0

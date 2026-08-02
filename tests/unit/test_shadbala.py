"""Unit tests for Shadbala partial scaffold (P27b / TEC-023)."""

from __future__ import annotations

from datetime import datetime

from bhava360.engines.shadbala import run_shadbala_engine
from bhava360.engines.shadbala.components import (
    dig_bala,
    kendradi_bala,
    naisargika_bala,
    ojayugma_rasi_bala,
    uchcha_bala,
)
from bhava360.kernel.models import SubjectInput


def test_naisargika_sun_max():
    assert naisargika_bala("Sun") == 60.0
    assert naisargika_bala("Saturn") < naisargika_bala("Mars")


def test_dig_bala_strong_and_opposite():
    assert dig_bala(planet="Sun", rasi_house=10) == 60.0
    assert dig_bala(planet="Sun", rasi_house=4) == 0.0
    assert dig_bala(planet="Jupiter", rasi_house=1) == 60.0


def test_kendradi_values():
    assert kendradi_bala(rasi_house=1) == 60.0
    assert kendradi_bala(rasi_house=2) == 30.0
    assert kendradi_bala(rasi_house=3) == 15.0


def test_uchcha_at_exaltation_sun():
    # Sun exalted Aries 10° → lon 10
    assert uchcha_bala(planet="Sun", longitude_sidereal_deg=10.0) == 60.0
    # Debilitation Libra 10° → lon 190
    assert uchcha_bala(planet="Sun", longitude_sidereal_deg=190.0) == 0.0


def test_ojayugma_male_odd():
    assert ojayugma_rasi_bala(planet="Sun", sign="Aries") == 15.0
    assert ojayugma_rasi_bala(planet="Sun", sign="Taurus") == 0.0
    assert ojayugma_rasi_bala(planet="Moon", sign="Taurus") == 15.0


def test_shadbala_engine_live():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_id="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
    )
    out = run_shadbala_engine(subject)
    assert out["engine"] == "Shadbala"
    assert "TEC-023" in out["technique_ids"]
    pack = out["shadbala"]
    assert pack["summary"]["planet_count"] == 7
    assert pack["summary"]["strongest_partial"]
    sun = next(p for p in pack["planets"] if p["planet"] == "Sun")
    assert sun["partial_total_virupa"] > 0
    assert "naisargika" in sun["components_virupa"]
    assert sun["full_minimum_comparison"] == "deferred_until_complete_shadbala"

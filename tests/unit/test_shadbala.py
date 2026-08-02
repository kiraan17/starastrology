"""Unit tests for Shadbala (P27b/P28a / TEC-023)."""

from __future__ import annotations

from datetime import datetime

from bhava360.engines.shadbala import run_shadbala_engine
from bhava360.engines.shadbala.components import (
    chesta_bala,
    dig_bala,
    drik_bala,
    kendradi_bala,
    naisargika_bala,
    natonnata_bala,
    ojayugma_rasi_bala,
    paksha_bala,
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
    assert uchcha_bala(planet="Sun", longitude_sidereal_deg=10.0) == 60.0
    assert uchcha_bala(planet="Sun", longitude_sidereal_deg=190.0) == 0.0


def test_ojayugma_male_odd():
    assert ojayugma_rasi_bala(planet="Sun", sign="Aries") == 15.0
    assert ojayugma_rasi_bala(planet="Sun", sign="Taurus") == 0.0
    assert ojayugma_rasi_bala(planet="Moon", sign="Taurus") == 15.0


def test_natonnata_and_paksha():
    assert natonnata_bala(planet="Sun", is_day=True) == 60.0
    assert natonnata_bala(planet="Sun", is_day=False) == 0.0
    assert natonnata_bala(planet="Mercury", is_day=False) == 60.0
    # Full moon elongation 180 → benefics 60, malefics 0
    assert paksha_bala(planet="Jupiter", sun_lon=0.0, moon_lon=180.0) == 60.0
    assert paksha_bala(planet="Saturn", sun_lon=0.0, moon_lon=180.0) == 0.0


def test_chesta_retrograde():
    assert chesta_bala(planet="Mars", is_retrograde=True)["value"] == 60.0
    assert chesta_bala(planet="Mars", is_retrograde=False)["value"] == 15.0
    assert chesta_bala(planet="Sun", is_retrograde=False)["basis"] == "ayana_chesta_deferred"


def test_drik_benefic_aspect():
    # Jupiter in Aries aspects Leo (5th) where Sun sits → benefic hit
    out = drik_bala(
        planet="Sun",
        planet_signs={"Sun": "Leo", "Jupiter": "Aries", "Mars": "Cancer"},
    )
    assert out["value"] > 0
    assert any(h["from"] == "Jupiter" for h in out["benefic_hits"])


def test_shadbala_engine_live():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_id="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
    )
    out = run_shadbala_engine(subject)
    assert out["engine"] == "Shadbala"
    assert out["engine_version"] == "0.2.0-kala-chesta-drik"
    assert "TEC-023" in out["technique_ids"]
    pack = out["shadbala"]
    assert pack["summary"]["planet_count"] == 7
    assert "kala_partial" in pack["summary"]["included_component_families"]
    sun = next(p for p in pack["planets"] if p["planet"] == "Sun")
    assert "kala_partial" in sun["components_virupa"]
    assert "chesta" in sun["components_virupa"]
    assert "drik" in sun["components_virupa"]
    assert sun["full_minimum_comparison"] == "deferred_until_complete_shadbala"

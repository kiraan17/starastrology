"""Unit tests for Shadbala (P27b/P28a/P29b / TEC-023)."""

from __future__ import annotations

from datetime import datetime

from bhava360.engines.shadbala import run_shadbala_engine
from bhava360.engines.shadbala.components import (
    ayana_bala,
    chesta_bala,
    dig_bala,
    drekkana_bala,
    drik_bala,
    kendradi_bala,
    naisargika_bala,
    natonnata_bala,
    ojayugma_navamsa_bala,
    ojayugma_rasi_bala,
    paksha_bala,
    saptavargaja_points,
    tribhaga_bala,
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
    assert ojayugma_rasi_bala(planet="Mercury", sign="Aries") == 15.0
    assert ojayugma_rasi_bala(planet="Mercury", sign="Taurus") == 0.0
    assert ojayugma_navamsa_bala(planet="Moon", navamsa_sign="Cancer") == 15.0


def test_drekkana_saravali():
    assert drekkana_bala(planet="Sun", longitude_sidereal_deg=5.0) == 15.0
    assert drekkana_bala(planet="Sun", longitude_sidereal_deg=15.0) == 0.0
    assert drekkana_bala(planet="Moon", longitude_sidereal_deg=15.0) == 15.0
    assert drekkana_bala(planet="Mercury", longitude_sidereal_deg=25.0) == 15.0


def test_saptavargaja_own_and_friend():
    mt = saptavargaja_points(planet="Sun", varga="D1", sign="Leo", sign_degree=5.0)
    assert mt["basis"] == "moolatrikona"
    assert mt["points"] == 45.0
    own = saptavargaja_points(planet="Sun", varga="D1", sign="Leo", sign_degree=25.0)
    assert own["points"] == 30.0
    d9 = saptavargaja_points(planet="Sun", varga="D9", sign="Leo", sign_degree=5.0)
    assert d9["points"] == 30.0
    friend = saptavargaja_points(planet="Sun", varga="D2", sign="Cancer")
    assert friend["points"] == 15.0
    enemy = saptavargaja_points(planet="Sun", varga="D2", sign="Libra")
    assert enemy["points"] == 4.0


def test_tribhaga_and_ayana():
    assert tribhaga_bala(planet="Jupiter", is_day=True, portion_index=0) == 60.0
    assert tribhaga_bala(planet="Mercury", is_day=True, portion_index=0) == 60.0
    assert tribhaga_bala(planet="Sun", is_day=True, portion_index=0) == 0.0
    assert tribhaga_bala(planet="Moon", is_day=False, portion_index=0) == 60.0
    # Sun ~10° Taurus tropical → ~49.4 (Saravali example band)
    sun_ayana = ayana_bala(planet="Sun", tropical_longitude_deg=40.367)
    assert 48.0 < sun_ayana < 51.0
    # Mercury always uses +|sin|
    mer = ayana_bala(planet="Mercury", tropical_longitude_deg=0.0)
    assert mer == 30.0


def test_natonnata_and_paksha():
    assert natonnata_bala(planet="Sun", is_day=True) == 60.0
    assert natonnata_bala(planet="Sun", is_day=False) == 0.0
    assert natonnata_bala(planet="Mercury", is_day=False) == 60.0
    assert paksha_bala(planet="Jupiter", sun_lon=0.0, moon_lon=180.0) == 60.0
    assert paksha_bala(planet="Saturn", sun_lon=0.0, moon_lon=180.0) == 0.0


def test_chesta_motion_bands():
    # Sun uses Ayana; Moon uses Paksha
    assert chesta_bala(planet="Sun", is_retrograde=False, ayana_value=42.5)["value"] == 42.5
    assert chesta_bala(planet="Sun", is_retrograde=False, ayana_value=42.5)["basis"] == "ayana_as_chesta"
    assert chesta_bala(planet="Moon", is_retrograde=False, paksha_value=33.0)["value"] == 33.0
    # Retrograde → Vakra 60
    assert chesta_bala(planet="Mars", is_retrograde=True, speed_longitude=-0.2)["value"] == 60.0
    assert chesta_bala(planet="Mars", is_retrograde=True, speed_longitude=-0.2)["motion"] == "vakra"
    # Anuvakra near 0° while retrograde
    assert (
        chesta_bala(
            planet="Mars", is_retrograde=True, speed_longitude=-0.2, sign_degree=0.5
        )["motion"]
        == "anuvakra"
    )
    # Sama ~ mean speed
    sama = chesta_bala(planet="Mars", is_retrograde=False, speed_longitude=0.55)
    assert sama["motion"] == "sama"
    assert sama["value"] == 7.5
    # Chara fast
    chara = chesta_bala(planet="Mars", is_retrograde=False, speed_longitude=1.0)
    assert chara["motion"] == "chara"
    assert chara["value"] == 45.0


def test_natonnata_and_paksha():
    assert natonnata_bala(planet="Sun", is_day=True) == 60.0
    assert natonnata_bala(planet="Sun", is_day=False) == 0.0
    assert natonnata_bala(planet="Mercury", is_day=False) == 60.0
    assert paksha_bala(planet="Jupiter", sun_lon=0.0, moon_lon=180.0) == 60.0
    assert paksha_bala(planet="Saturn", sun_lon=0.0, moon_lon=180.0) == 0.0


def test_drik_benefic_aspect():
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
    assert out["engine_version"] == "0.5.0-chesta-motion"
    assert "TEC-023" in out["technique_ids"]
    pack = out["shadbala"]
    assert pack["variant"] == "shadbala_chesta_motion_candidate_v1"
    assert pack["summary"]["planet_count"] == 7
    sun = next(p for p in pack["planets"] if p["planet"] == "Sun")
    kala = sun["components_virupa"]["kala_partial"]
    chesta = sun["components_virupa"]["chesta"]
    assert chesta["basis"] == "ayana_as_chesta"
    assert chesta["value"] == kala["ayana"]
    moon = next(p for p in pack["planets"] if p["planet"] == "Moon")
    assert moon["components_virupa"]["chesta"]["basis"] == "paksha_as_chesta"
    mars = next(p for p in pack["planets"] if p["planet"] == "Mars")
    assert mars["components_virupa"]["chesta"]["motion"] in {
        "vakra",
        "anuvakra",
        "vikala",
        "mandatara",
        "manda",
        "sama",
        "chara",
        "atichara",
    }
    assert sun["full_minimum_comparison"] == "deferred_until_complete_shadbala"

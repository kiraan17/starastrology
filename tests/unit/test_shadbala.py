"""Unit tests for Shadbala (P27b/P28a/P29b / TEC-023)."""

from __future__ import annotations

from datetime import datetime

from bhava360.engines.shadbala import run_shadbala_engine
from bhava360.engines.shadbala.components import (
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
    # Neutrals follow odd-sign rule (Saravali), not always-15.
    assert ojayugma_rasi_bala(planet="Mercury", sign="Aries") == 15.0
    assert ojayugma_rasi_bala(planet="Mercury", sign="Taurus") == 0.0
    assert ojayugma_navamsa_bala(planet="Moon", navamsa_sign="Cancer") == 15.0


def test_drekkana_saravali():
    # Male first, female middle, neutral last
    assert drekkana_bala(planet="Sun", longitude_sidereal_deg=5.0) == 15.0
    assert drekkana_bala(planet="Sun", longitude_sidereal_deg=15.0) == 0.0
    assert drekkana_bala(planet="Moon", longitude_sidereal_deg=15.0) == 15.0
    assert drekkana_bala(planet="Mercury", longitude_sidereal_deg=25.0) == 15.0


def test_saptavargaja_own_and_friend():
    # Sun moolatrikona Leo 0–20 in D1 → 45
    mt = saptavargaja_points(planet="Sun", varga="D1", sign="Leo", sign_degree=5.0)
    assert mt["basis"] == "moolatrikona"
    assert mt["points"] == 45.0
    # Beyond moolatrikona window but still own → 30
    own = saptavargaja_points(planet="Sun", varga="D1", sign="Leo", sign_degree=25.0)
    assert own["points"] == 30.0
    # In D9, Leo is own=30 not moolatrikona 45
    d9 = saptavargaja_points(planet="Sun", varga="D9", sign="Leo", sign_degree=5.0)
    assert d9["points"] == 30.0
    friend = saptavargaja_points(planet="Sun", varga="D2", sign="Cancer")
    assert friend["points"] == 15.0
    enemy = saptavargaja_points(planet="Sun", varga="D2", sign="Libra")
    assert enemy["points"] == 4.0


def test_natonnata_and_paksha():
    assert natonnata_bala(planet="Sun", is_day=True) == 60.0
    assert natonnata_bala(planet="Sun", is_day=False) == 0.0
    assert natonnata_bala(planet="Mercury", is_day=False) == 60.0
    assert paksha_bala(planet="Jupiter", sun_lon=0.0, moon_lon=180.0) == 60.0
    assert paksha_bala(planet="Saturn", sun_lon=0.0, moon_lon=180.0) == 0.0


def test_chesta_retrograde():
    assert chesta_bala(planet="Mars", is_retrograde=True)["value"] == 60.0
    assert chesta_bala(planet="Mars", is_retrograde=False)["value"] == 15.0
    assert chesta_bala(planet="Sun", is_retrograde=False)["basis"] == "ayana_chesta_deferred"


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
    assert out["engine_version"] == "0.3.0-saptavargaja"
    assert "TEC-023" in out["technique_ids"]
    pack = out["shadbala"]
    assert pack["variant"] == "shadbala_saptavargaja_candidate_v1"
    assert pack["summary"]["planet_count"] == 7
    sun = next(p for p in pack["planets"] if p["planet"] == "Sun")
    sth = sun["components_virupa"]["sthana_partial"]
    assert "saptavargaja" in sth
    assert sth["saptavargaja"]["value"] > 0
    assert "ojayugma_navamsa" in sth
    assert "drekkana" in sth
    assert sun["full_minimum_comparison"] == "deferred_until_complete_shadbala"

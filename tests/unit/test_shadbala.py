"""Unit tests for Shadbala (P27b–P31b / TEC-023)."""

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
    sankranti_hora_lord,
    saptavargaja_points,
    sphuta_drishti,
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


def test_sphuta_drishti_angles():
    # Opposition → general 60 (Candidate 150–180 fix)
    assert sphuta_drishti(aspector="Sun", from_longitude=10.0, to_longitude=190.0) == 60.0
    # Mid 165° → 2*(165-150)=30
    assert sphuta_drishti(aspector="Sun", from_longitude=0.0, to_longitude=165.0) == 30.0
    # Jupiter exact trine → special 60
    assert sphuta_drishti(aspector="Jupiter", from_longitude=0.0, to_longitude=120.0) == 60.0
    # Saturn exact 3rd → special 60
    assert sphuta_drishti(aspector="Saturn", from_longitude=0.0, to_longitude=60.0) == 60.0
    # Within 30° → 0
    assert sphuta_drishti(aspector="Venus", from_longitude=0.0, to_longitude=20.0) == 0.0


def test_drik_classical_fallback_and_sphuta():
    # Without longitudes → whole-sign classical table fallback
    out = drik_bala(
        planet="Sun",
        planet_signs={"Sun": "Leo", "Jupiter": "Aries", "Mars": "Cancer"},
        sun_lon=120.0,
        moon_lon=200.0,
    )
    assert out["basis"] == "classical_graha_drishti_table_fallback"
    assert any(h["from"] == "Jupiter" for h in out["benefic_hits"])
    jup = next(h for h in out["benefic_hits"] if h["from"] == "Jupiter")
    assert jup["base_virupa"] == 60.0
    assert jup["weight"] == 75.0
    assert out["value"] == 75.0

    # Mars 4th onto a planet: Aries→Cancer is 4th → Mars special 60 × 0.75 malefic
    out2 = drik_bala(
        planet="Moon",
        planet_signs={"Moon": "Cancer", "Mars": "Aries", "Venus": "Capricorn"},
        sun_lon=0.0,
        moon_lon=90.0,
    )
    assert any(h["from"] == "Mars" for h in out2["malefic_hits"])
    mars = next(h for h in out2["malefic_hits"] if h["from"] == "Mars")
    assert mars["base_virupa"] == 60.0
    assert mars["weight"] == 45.0
    assert any(h["from"] == "Venus" for h in out2["benefic_hits"])

    # With longitudes → Sphuta; Jupiter 0° → Sun 120° trine = 60 × 1.25
    longs = {"Sun": 120.0, "Jupiter": 0.0}
    out3 = drik_bala(
        planet="Sun",
        planet_signs={"Sun": "Leo", "Jupiter": "Aries"},
        sun_lon=120.0,
        moon_lon=200.0,
        planet_longitudes=longs,
    )
    assert out3["basis"] == "sphuta_drishti_candidate"
    jup_s = next(h for h in out3["benefic_hits"] if h["from"] == "Jupiter")
    assert jup_s["base_virupa"] == 60.0
    assert jup_s["aspect_angle_deg"] == 120.0
    assert jup_s["weight"] == 75.0


def test_sankranti_hora_lord_mean_sun():
    birth = datetime(1990, 8, 15, 12, 0)
    rise = datetime(1990, 8, 15, 6, 0)
    sett = datetime(1990, 8, 15, 18, 0)
    # Sun at 0° → sankranti ≈ birth; midday → day hora after sunrise
    meta = sankranti_hora_lord(
        birth_local=birth,
        sun_sidereal_lon=0.0,
        target_lon=0.0,
        sunrise_local=rise,
        sunset_local=sett,
    )
    assert meta["basis"] == "sankranti_hora_mean_sun_candidate"
    assert meta["lord"] in {
        "Sun",
        "Moon",
        "Mars",
        "Mercury",
        "Jupiter",
        "Venus",
        "Saturn",
    }
    assert meta["hora_period"] == "day"
    # Without day window → weekday fallback
    fb = sankranti_hora_lord(
        birth_local=birth,
        sun_sidereal_lon=10.0,
        target_lon=0.0,
    )
    assert fb["basis"] == "sankranti_weekday_fallback"
    assert fb["lord"] in {
        "Sun",
        "Moon",
        "Mars",
        "Mercury",
        "Jupiter",
        "Venus",
        "Saturn",
    }


def test_shadbala_engine_live():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_id="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
    )
    out = run_shadbala_engine(subject)
    assert out["engine"] == "Shadbala"
    assert out["engine_version"] == "0.8.0-abda-masa-hora"
    assert "TEC-023" in out["technique_ids"]
    pack = out["shadbala"]
    assert pack["variant"] == "shadbala_abda_masa_hora_candidate_v1"
    assert pack["summary"]["planet_count"] == 7
    assert "kala_abda_masa_hora_at_sankranti" not in pack["summary"]["deferred_component_families"]
    assert pack["context"]["abda_meta"]["basis"] == "sankranti_hora_mean_sun_candidate"
    assert pack["context"]["masa_meta"]["basis"] == "sankranti_hora_mean_sun_candidate"
    assert pack["context"]["abda_lord"]
    assert pack["context"]["masa_lord"]
    sun = next(p for p in pack["planets"] if p["planet"] == "Sun")
    assert sun["components_virupa"]["drik"]["basis"] == "sphuta_drishti_candidate"
    chesta = sun["components_virupa"]["chesta"]
    assert chesta["basis"] == "ayana_as_chesta"
    assert sun["full_minimum_comparison"] == "deferred_until_complete_shadbala"

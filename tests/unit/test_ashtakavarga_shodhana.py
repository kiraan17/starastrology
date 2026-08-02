"""Unit tests for Ashtakavarga Shodhana / Sodhya Pinda (P12b)."""

from __future__ import annotations

from datetime import datetime

from bhava360.engines.ashtakavarga.engine import run_ashtakavarga_engine
from bhava360.engines.ashtakavarga.shodhana import (
    apply_ekadhipatya_shodhana,
    apply_mandala_shodhana,
    apply_trikona_shodhana,
    compute_sodhya_pinda,
    reduce_bhinna_ashtakavarga,
    reduce_sarva_ashtakavarga,
)
from bhava360.kernel.models import SubjectInput


def test_trikona_rules_a_b_c_d():
    # Rule (a): unequal → subtract min
    fire = apply_trikona_shodhana(
        {
            "Aries": 5,
            "Leo": 4,
            "Sagittarius": 5,
            "Taurus": 0,
            "Virgo": 0,
            "Capricorn": 0,
            "Gemini": 0,
            "Libra": 0,
            "Aquarius": 0,
            "Cancer": 0,
            "Scorpio": 0,
            "Pisces": 0,
        }
    )
    assert fire["after"]["Aries"] == 1
    assert fire["after"]["Leo"] == 0
    assert fire["after"]["Sagittarius"] == 1
    assert fire["steps"][0]["rule"] == "a_subtract_minimum"

    # Rule (b): one zero → no reduction
    earth = apply_trikona_shodhana(
        {
            "Aries": 0,
            "Leo": 0,
            "Sagittarius": 0,
            "Taurus": 3,
            "Virgo": 4,
            "Capricorn": 0,
            "Gemini": 0,
            "Libra": 0,
            "Aquarius": 0,
            "Cancer": 0,
            "Scorpio": 0,
            "Pisces": 0,
        }
    )
    assert earth["after"]["Taurus"] == 3
    assert earth["after"]["Virgo"] == 4
    assert earth["after"]["Capricorn"] == 0
    assert earth["steps"][1]["rule"] == "b_one_zero_no_reduction"

    # Rule (c): two zeros → eliminate remaining
    air = apply_trikona_shodhana(
        {
            "Aries": 0,
            "Leo": 0,
            "Sagittarius": 0,
            "Taurus": 0,
            "Virgo": 0,
            "Capricorn": 0,
            "Gemini": 5,
            "Libra": 0,
            "Aquarius": 0,
            "Cancer": 0,
            "Scorpio": 0,
            "Pisces": 0,
        }
    )
    assert air["after"]["Gemini"] == 0
    assert air["steps"][2]["rule"] == "c_two_zeros_eliminate_group"

    # Rule (d): all equal → eliminate
    water = apply_trikona_shodhana(
        {
            "Aries": 0,
            "Leo": 0,
            "Sagittarius": 0,
            "Taurus": 0,
            "Virgo": 0,
            "Capricorn": 0,
            "Gemini": 0,
            "Libra": 0,
            "Aquarius": 0,
            "Cancer": 3,
            "Scorpio": 3,
            "Pisces": 3,
        }
    )
    assert water["after"]["Cancer"] == 0
    assert water["steps"][3]["rule"] == "d_all_equal_eliminate_group"


def test_trikona_sun_worked_example():
    """Sun BAV Trikona from Raman/VedAstro comparator worked example."""
    raw = {
        "Aries": 5,
        "Taurus": 3,
        "Gemini": 5,
        "Cancer": 4,
        "Leo": 4,
        "Virgo": 4,
        "Libra": 3,
        "Scorpio": 5,
        "Sagittarius": 5,
        "Capricorn": 0,
        "Aquarius": 5,
        "Pisces": 5,
    }
    out = apply_trikona_shodhana(raw)
    assert out["after"] == {
        "Aries": 1,
        "Taurus": 3,
        "Gemini": 2,
        "Cancer": 0,
        "Leo": 0,
        "Virgo": 4,
        "Libra": 0,
        "Scorpio": 1,
        "Sagittarius": 1,
        "Capricorn": 0,
        "Aquarius": 2,
        "Pisces": 1,
    }


def test_ekadhipatya_sun_worked_example():
    after_trikona = {
        "Aries": 1,
        "Taurus": 3,
        "Gemini": 2,
        "Cancer": 0,
        "Leo": 0,
        "Virgo": 4,
        "Libra": 0,
        "Scorpio": 1,
        "Sagittarius": 1,
        "Capricorn": 0,
        "Aquarius": 2,
        "Pisces": 1,
    }
    # Standard horoscope occupations used in comparator article.
    occupied = {"Virgo", "Aquarius", "Scorpio", "Libra", "Gemini", "Leo"}
    out = apply_ekadhipatya_shodhana(after_trikona, occupied)
    assert out["after"] == {
        "Aries": 0,
        "Taurus": 3,
        "Gemini": 2,
        "Cancer": 0,
        "Leo": 0,
        "Virgo": 4,
        "Libra": 0,
        "Scorpio": 1,
        "Sagittarius": 0,
        "Capricorn": 0,
        "Aquarius": 2,
        "Pisces": 0,
    }


def test_ekadhipatya_scenario_ii_b_and_iii_b():
    # II(b): occupied smaller than unoccupied → equalise unoccupied down
    one = apply_ekadhipatya_shodhana(
        {
            "Aries": 1,
            "Scorpio": 4,
            "Taurus": 0,
            "Libra": 0,
            "Gemini": 0,
            "Virgo": 0,
            "Sagittarius": 0,
            "Pisces": 0,
            "Capricorn": 0,
            "Aquarius": 0,
            "Cancer": 0,
            "Leo": 0,
        },
        occupied_signs={"Aries"},
    )
    assert one["after"]["Aries"] == 1
    assert one["after"]["Scorpio"] == 1
    assert one["steps"][0]["rule"] == "II_b_equalise_unoccupied_to_occupied"

    # III(b): both empty unequal → both become smaller
    both = apply_ekadhipatya_shodhana(
        {
            "Aries": 5,
            "Scorpio": 2,
            "Taurus": 0,
            "Libra": 0,
            "Gemini": 0,
            "Virgo": 0,
            "Sagittarius": 0,
            "Pisces": 0,
            "Capricorn": 0,
            "Aquarius": 0,
            "Cancer": 0,
            "Leo": 0,
        },
        occupied_signs=set(),
    )
    assert both["after"]["Aries"] == 2
    assert both["after"]["Scorpio"] == 2
    assert both["steps"][0]["rule"] == "III_b_both_unoccupied_equalise_to_smaller"


def test_mandala_leave_twelve_on_exact_multiple():
    out = apply_mandala_shodhana(
        {
            "Aries": 33,
            "Taurus": 25,
            "Gemini": 24,
            "Cancer": 12,
            "Leo": 0,
            "Virgo": 23,
            "Libra": 11,
            "Scorpio": 29,
            "Sagittarius": 30,
            "Capricorn": 24,
            "Aquarius": 27,
            "Pisces": 31,
        }
    )
    assert out["after"]["Aries"] == 9
    assert out["after"]["Taurus"] == 1
    assert out["after"]["Gemini"] == 12
    assert out["after"]["Cancer"] == 12
    assert out["after"]["Leo"] == 0
    assert out["after"]["Virgo"] == 11
    assert out["after"]["Capricorn"] == 12


def test_sodhya_pinda_products():
    reduced = {s: 0 for s in (
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
    )}
    reduced["Aries"] = 2  # 2 * 7 = 14
    reduced["Leo"] = 1  # 1 * 10 = 10
    planet_signs = {
        "Sun": "Leo",
        "Moon": "Aries",
        "Mars": "Taurus",
        "Mercury": "Gemini",
        "Jupiter": "Cancer",
        "Venus": "Virgo",
        "Saturn": "Libra",
    }
    out = compute_sodhya_pinda(reduced, planet_signs)
    assert out["rasi_pinda"] == 14 + 10
    # Sun in Leo: 1*5=5; Moon in Aries: 2*5=10; others 0
    assert out["graha_pinda"] == 15
    assert out["sodhya_pinda"] == 39


def test_reduce_bhinna_and_sav_pipeline():
    raw = {
        "Aries": 5,
        "Taurus": 3,
        "Gemini": 5,
        "Cancer": 4,
        "Leo": 4,
        "Virgo": 4,
        "Libra": 3,
        "Scorpio": 5,
        "Sagittarius": 5,
        "Capricorn": 0,
        "Aquarius": 5,
        "Pisces": 5,
    }
    planet_signs = {
        "Sun": "Virgo",
        "Moon": "Aquarius",
        "Mars": "Scorpio",
        "Mercury": "Libra",
        "Jupiter": "Gemini",
        "Venus": "Virgo",
        "Saturn": "Leo",
    }
    bav = reduce_bhinna_ashtakavarga(sign_bindus=raw, planet_signs=planet_signs)
    assert bav["reduced_bindus"]["Scorpio"] == 1
    assert bav["sodhya_pinda"]["sodhya_pinda"] == (
        bav["sodhya_pinda"]["rasi_pinda"] + bav["sodhya_pinda"]["graha_pinda"]
    )

    sav_raw = {s: 30 for s in raw}
    sav = reduce_sarva_ashtakavarga(sign_bindus=sav_raw, planet_signs=planet_signs)
    assert "mandala" in sav
    assert sav["mandala"]["after"]["Aries"] == 6  # 30 % 12 = 6
    assert "sodhya_pinda" in sav["sodhya_pinda"]


def test_engine_includes_shodhana_and_sodhya():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_offset_minutes=330,
        latitude=13.0827,
        longitude=80.2707,
        location_label="Chennai",
    )
    out = run_ashtakavarga_engine(subject)
    assert out["engine_version"] == "0.2.0-shodhana"
    assert out["sarvashtakavarga"]["total_bindus"] == 337
    assert "shodhana" in out["sarvashtakavarga"]
    assert "mandala" in out["sarvashtakavarga"]["shodhana"]
    assert "Sun" in out["bhinnashtakavarga_shodhana"]
    sun_sp = out["bhinnashtakavarga_shodhana"]["Sun"]["sodhya_pinda"]
    assert sun_sp["sodhya_pinda"] == sun_sp["rasi_pinda"] + sun_sp["graha_pinda"]
    assert "TEC-051" in out["technique_ids"]
    assert "TEC-052" in out["technique_ids"]

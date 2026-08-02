"""Unit tests for Jaimini thin-slice engine (never labeled Gemini)."""

from __future__ import annotations

from datetime import datetime

import pytest

from bhava360.chart.builder import ChartConstructor
from bhava360.engines.jaimini import CharaKarakaScheme, run_jaimini_engine
from bhava360.engines.jaimini.calculations import (
    compute_argala,
    compute_arudha_pada,
    compute_arudha_padas,
    compute_chara_karakas,
    compute_karakamsa_swamsa,
)
from bhava360.kernel.errors import KernelError
from bhava360.kernel.models import SubjectInput


def _longitudes() -> dict[str, float]:
    # Distinct degree-in-sign ranks (highest deg → Atmakaraka).
    return {
        "Sun": 10.0,  # 10°
        "Moon": 45.0,  # 15° Taurus
        "Mars": 80.0,  # 20° Gemini
        "Mercury": 25.0,  # 25° Aries → AK in seven scheme
        "Jupiter": 100.0,  # 10° Cancer
        "Venus": 200.0,  # 20° Libra
        "Saturn": 301.0,  # 1° Aquarius
        "Rahu": 185.0,  # 5° Libra → reverse key 25° in eight scheme
    }


def test_chara_karakas_seven_ranks_by_degree():
    out = compute_chara_karakas(_longitudes(), scheme=CharaKarakaScheme.SEVEN)
    assert out["scheme"] == "seven"
    assert len(out["karakas"]) == 7
    assert out["atmakaraka"]["planet"] == "Mercury"
    assert out["atmakaraka"]["name"] == "Atmakaraka"
    assert out["karakas"][-1]["name"] == "Darakaraka"
    assert "Pitrikaraka" not in {k["name"] for k in out["karakas"]}


def test_chara_karakas_eight_includes_rahu_and_pitri():
    out = compute_chara_karakas(_longitudes(), scheme=CharaKarakaScheme.EIGHT)
    assert out["scheme"] == "eight"
    assert len(out["karakas"]) == 8
    names = [k["name"] for k in out["karakas"]]
    assert "Pitrikaraka" in names
    planets = [k["planet"] for k in out["karakas"]]
    assert "Rahu" in planets
    # Rahu reverse key 25° ties Mercury 25° — sort is stable enough that both rank high.
    assert out["karakas"][0]["degree_in_sign_used"] >= out["karakas"][1]["degree_in_sign_used"]


def test_arudha_exception_when_pada_falls_on_reference():
    # Lord in same sign as reference → count 0 → pada = lord = ref → exception → +9
    detail = compute_arudha_pada("Aries", "Aries")
    assert detail["exception_applied"] is True
    assert detail["arudha_sign"] == "Capricorn"  # 10th from Aries after exception from Aries


def test_arudha_exception_when_pada_is_seventh():
    # Aries ref, lord in Cancer (count 3) → pada = Cancer+3 = Libra (7th) → exception
    detail = compute_arudha_pada("Aries", "Cancer")
    assert detail["exception_applied"] is True
    assert detail["arudha_sign"] == "Cancer"  # Libra + 9 = Cancer


def test_arudha_padas_a1_to_a12():
    signs = {
        "Sun": "Leo",
        "Moon": "Cancer",
        "Mars": "Aries",
        "Mercury": "Virgo",
        "Jupiter": "Sagittarius",
        "Venus": "Libra",
        "Saturn": "Capricorn",
    }
    out = compute_arudha_padas(lagna_sign="Aries", planet_signs=signs)
    assert len(out["padas"]) == 12
    assert out["arudha_lagna"]["label"] == "A1"
    assert out["system"] == "jaimini_arudha"


def test_karakamsa_swamsa_navamsa():
    # AK at 0° Aries → D9 Aries; Asc at 3.5° Aries → second navamsa → Taurus
    out = compute_karakamsa_swamsa(
        atmakaraka_longitude=0.0,
        ascendant_longitude=3.5,
    )
    assert out["karakamsa"]["sign"] == "Aries"
    assert out["swamsa"]["sign"] == "Taurus"
    assert out["swamsa"]["varga"] == "D9"


def test_argala_houses_from_reference():
    out = compute_argala("Aries")
    assert out["argala_signs"] == ["Taurus", "Cancer", "Aquarius"]
    assert out["virodha_argala_signs"] == ["Pisces", "Capricorn", "Gemini"]


def test_engine_never_named_gemini():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_offset_minutes=330,
        latitude=13.0827,
        longitude=80.2707,
        location_label="Chennai",
    )
    chart = ChartConstructor().build(subject, include_vimshottari=False).to_dict()
    out = run_jaimini_engine(chart=chart, chara_karaka_scheme="seven")
    blob = str(out).lower()
    assert out["engine"] == "Jaimini"
    assert "gemini" not in out["engine"].lower()
    # Zodiac sign Gemini may appear in chart data; engine label must not.
    assert out["school"] == "jaimini"
    assert "TEC-028" in out["technique_ids"]
    assert out["config"]["jaimini.chara_karaka.scheme"] == "seven"
    assert out["chara_karakas"]["atmakaraka"]["planet"]
    assert "A1" in out["arudha"]["padas"]
    assert out["karakamsa_swamsa"]["karakamsa"]["sign"]
    assert out["argala"]["argala_signs"]
    assert any("never gemini" in n.lower() for n in out["notes"])


def test_engine_eight_scheme_via_live_chart():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_offset_minutes=330,
        latitude=13.0827,
        longitude=80.2707,
        location_label="Chennai",
    )
    out = run_jaimini_engine(subject, chara_karaka_scheme=CharaKarakaScheme.EIGHT)
    assert out["config"]["jaimini.chara_karaka.scheme"] == "eight"
    assert len(out["chara_karakas"]["karakas"]) == 8


def test_invalid_scheme_raises():
    with pytest.raises(KernelError):
        run_jaimini_engine(
            chart={
                "planets": [],
                "angles": {"whole_sign": {"ascendant": {"sign": "Aries", "longitude_sidereal_deg": 0}}},
            },
            chara_karaka_scheme="nine",
        )

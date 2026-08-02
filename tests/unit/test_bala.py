"""Tests for Tara Bala and Chandra Bala (P16c)."""

from __future__ import annotations

from datetime import datetime

from bhava360.kernel.models import SubjectInput
from bhava360.timing.bala import (
    compute_chandra_bala,
    compute_tara_bala,
    compute_tara_chandra_pack,
)
from bhava360.timing.panchanga_engine import run_panchanga_engine


def test_tara_same_nakshatra_is_janma():
    t = compute_tara_bala(reference_nakshatra_index=0, target_nakshatra_index=0)
    assert t["tara"] == "Janma"
    assert t["tara_number"] == 1
    assert t["auspicious"] is False


def test_tara_cycle_sampat_and_vipat():
    sampat = compute_tara_bala(reference_nakshatra_index=0, target_nakshatra_index=1)
    assert sampat["tara"] == "Sampat"
    assert sampat["auspicious"] is True
    vipat = compute_tara_bala(reference_nakshatra_index=0, target_nakshatra_index=2)
    assert vipat["tara"] == "Vipat"
    assert vipat["auspicious"] is False


def test_chandra_bala_favorable_counts():
    good = compute_chandra_bala(reference_sign_index=0, target_sign_index=2)  # 3rd
    assert good["bala"] == "present"
    bad = compute_chandra_bala(reference_sign_index=0, target_sign_index=1)  # 2nd
    assert bad["bala"] == "absent"


def test_pack_includes_planets_and_lagna():
    pack = compute_tara_chandra_pack(
        moon_longitude_sidereal=40.0,  # Taurus-ish
        lagna_longitude_sidereal=10.0,  # Aries
        planet_longitudes={"Sun": 100.0, "Moon": 40.0},
    )
    assert pack["tara_from_moon"]["Moon"]["tara"] == "Janma"
    assert "Lagna" in pack["tara_from_moon"]
    assert pack["chandra_bala"]["moon_from_lagna"]["count_from_reference"] >= 1


def test_engine_includes_bala():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_id="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
        location_label="Chennai",
    )
    out = run_panchanga_engine(subject)
    assert out["engine_version"] == "0.3.0-bala"
    assert "TEC-072" in out["technique_ids"]
    assert out["bala"]["tara_from_moon"]["Moon"]["tara"] == "Janma"
    assert out["bala"]["chandra_bala"]["moon_from_lagna"]["bala"] in {"present", "absent"}

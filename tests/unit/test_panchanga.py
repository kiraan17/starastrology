"""Unit tests for P16a panchanga core."""

from __future__ import annotations

from datetime import datetime, timezone

from bhava360.kernel.models import SubjectInput
from bhava360.timing.panchanga import (
    compute_karana,
    compute_panchanga_core,
    compute_tithi,
    compute_vara_from_local,
    compute_yoga,
)
from bhava360.timing.panchanga_engine import run_panchanga_engine


def test_tithi_new_moon_amavasya():
    # Moon == Sun → elong 0 → Shukla Pratipada start; elong just under 360 → Amavasya
    t0 = compute_tithi(10.0, 10.0)
    assert t0["paksha"] == "Shukla"
    assert t0["name"] == "Pratipada"
    t_ama = compute_tithi(10.0, 10.0 + 359.0)
    assert t_ama["name"] == "Amavasya"
    assert t_ama["paksha"] == "Krishna"


def test_tithi_purnima():
    # elong in [168°, 180°) → index 15 → Purnima (idx 14)
    t = compute_tithi(0.0, 174.0)
    assert t["name"] == "Purnima"
    assert t["index"] == 15


def test_karana_kimstughna_and_movable():
    k0 = compute_karana(0.0, 0.0)
    assert k0["name"] == "Kimstughna"
    # elong 6° → second karana → Bava
    k1 = compute_karana(0.0, 6.0)
    assert k1["name"] == "Bava"


def test_yoga_index_wrap():
    y = compute_yoga(0.0, 0.0)
    assert y["name"] == "Vishkambha"
    assert y["index"] == 1


def test_vara_sunday_index():
    # 1990-08-15 was a Wednesday
    v = compute_vara_from_local(datetime(1990, 8, 15, 5, 50))
    assert v["name"] == "Wednesday"
    assert v["lord"] == "Mercury"


def test_panchanga_engine_chennai():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_id="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
        location_label="Chennai",
    )
    out = run_panchanga_engine(subject)
    assert out["engine"] == "Panchanga"
    p = out["panchanga"]
    assert p["tithi"]["label"]
    assert p["vara"]["name"] == "Wednesday"
    assert p["nakshatra"]["name"]
    assert p["yoga"]["name"]
    assert p["karana"]["name"]
    assert "TEC-070" in out["technique_ids"]


def test_compute_panchanga_core_smoke():
    core = compute_panchanga_core(
        sun_lon_sidereal=120.0,
        moon_lon_sidereal=200.0,
        sunrise_local=datetime(1990, 8, 15, 6, 0, tzinfo=timezone.utc),
    )
    assert set(core) >= {"tithi", "vara", "nakshatra", "yoga", "karana"}

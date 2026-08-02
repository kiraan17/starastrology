"""Unit tests for classification: Gandanta / Chandra Kriya / Avastha (P19a)."""

from __future__ import annotations

from datetime import datetime

from bhava360.engines.classification import run_classification_engine
from bhava360.engines.classification.conditions import (
    classify_baladi_avastha,
    classify_chandra_kriya,
    classify_gandanta,
)
from bhava360.kernel.derived import NAKSHATRA_SPAN, PADA_SPAN
from bhava360.kernel.models import SubjectInput


def test_gandanta_aswini_pada1():
    # Start of Aswini
    out = classify_gandanta(1.0)
    assert out["active"] is True
    assert out["nakshatra_gandanta"] is True
    assert out["junction"] == "Pisces-Aries"


def test_gandanta_aslesha_pada4():
    # Aslesha is nakshatra index 8; pada 4 starts at 8*NAKSHATRA_SPAN + 3*PADA_SPAN
    lon = 8 * NAKSHATRA_SPAN + 3 * PADA_SPAN + 0.1
    out = classify_gandanta(lon)
    assert out["nakshatra_gandanta"] is True
    assert out["junction"] == "Cancer-Leo"


def test_gandanta_mid_sign_clear():
    # Mid Taurus — not gandanta
    out = classify_gandanta(45.0)
    assert out["active"] is False


def test_chandra_kriya_zones():
    out = classify_chandra_kriya(0.5)
    assert out["index"] == 1
    assert out["name"] == "Nivritti"
    out2 = classify_chandra_kriya(6.0)
    assert out2["index"] == 2


def test_baladi_avastha_odd_even():
    # Aries (odd) 1° → Bala
    a = classify_baladi_avastha(longitude_sidereal_deg=1.0, planet="Sun")
    assert a["avastha"] == "Bala"
    # Taurus (even) 1° → Mrita (reverse)
    b = classify_baladi_avastha(longitude_sidereal_deg=31.0, planet="Moon")
    assert b["avastha"] == "Mrita"


def test_classification_engine_live():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_offset_minutes=330,
        latitude=13.0827,
        longitude=80.2707,
        location_label="Chennai",
    )
    out = run_classification_engine(subject)
    assert out["engine"] == "Classification"
    assert "TEC-084" in out["technique_ids"]
    assert "TEC-085" in out["technique_ids"]
    assert out["moon"]["chandra_kriya"]["index"] >= 1
    assert out["moon"]["chandra_vela"]["index"] >= 1
    assert out["moon"]["baladi_avastha"]["avastha"] in {
        "Bala",
        "Kumara",
        "Yuva",
        "Vriddha",
        "Mrita",
    }
    assert isinstance(out["gandanta_hits"], list)
    assert out["safety"]["note"]

"""Unit tests for Bhava Bala (P28b / TEC-024)."""

from __future__ import annotations

from datetime import datetime

from bhava360.engines.bhava_bala import run_bhava_bala_engine
from bhava360.engines.bhava_bala.components import lagna_class
from bhava360.kernel.models import SubjectInput


def test_lagna_class_mapping():
    assert lagna_class("Libra") == "nara"
    assert lagna_class("Cancer") == "jalachara"
    assert lagna_class("Aries") == "chatushpada"
    assert lagna_class("Scorpio") == "keeta"


def test_bhava_bala_engine_live():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_id="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
    )
    out = run_bhava_bala_engine(subject)
    assert out["engine"] == "BhavaBala"
    assert out["engine_version"] == "0.1.0-partial-scaffold"
    assert "TEC-024" in out["technique_ids"]
    pack = out["bhava_bala"]
    assert pack["variant"] == "bhava_bala_partial_candidate_v1"
    assert pack["lagna_sign"] == "Libra"
    assert pack["lagna_class"] == "nara"
    assert pack["dig_strong_house"] == 1
    assert pack["summary"]["house_count"] == 12
    h1 = next(h for h in pack["houses"] if h["house"] == 1)
    assert h1["components_virupa"]["dig"] == 60.0
    h2 = next(h for h in pack["houses"] if h["house"] == 2)
    assert h2["components_virupa"]["dig"] == 0.0
    assert h1["lord"] == "Venus"
    assert h1["components_virupa"]["bhavadhipati"] > 0
    assert pack["summary"]["strongest_house"] is not None

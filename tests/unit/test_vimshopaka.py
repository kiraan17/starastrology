"""Unit tests for Vimshopaka (P29a / TEC-025)."""

from __future__ import annotations

from datetime import datetime

from bhava360.chart.vargas import VargaId, varga_sign
from bhava360.engines.vimshopaka import run_vimshopaka_engine
from bhava360.engines.vimshopaka.components import (
    SHODASHAVARGA_WEIGHTS,
    permanent_relation,
    varga_vishwa,
)
from bhava360.kernel.models import SubjectInput


def test_shodashavarga_weights_sum_20():
    assert abs(sum(SHODASHAVARGA_WEIGHTS.values()) - 20.0) < 1e-9
    assert len(SHODASHAVARGA_WEIGHTS) == 16


def test_d4_chaturthamsa():
    # 0° Aries → part 0 → Aries; 8° Aries → part 1 → Taurus
    assert varga_sign(0.0, VargaId.D4).sign == "Aries"
    assert varga_sign(8.0, VargaId.D4).sign == "Taurus"
    assert varga_sign(15.0, VargaId.D4).sign == "Gemini"
    assert varga_sign(23.0, VargaId.D4).sign == "Cancer"


def test_varga_vishwa_own_and_friend():
    own = varga_vishwa(planet="Sun", sign="Leo")
    assert own["points"] == 20.0
    exalted = varga_vishwa(planet="Sun", sign="Aries")
    assert exalted["points"] == 20.0
    # Sun in Cancer → Moon friend → 15
    friend = varga_vishwa(planet="Sun", sign="Cancer")
    assert friend["points"] == 15.0
    assert friend["basis"] == "friend"
    # Sun in Libra → Venus enemy → 7
    enemy = varga_vishwa(planet="Sun", sign="Libra")
    assert enemy["points"] == 7.0
    assert "debilitation" in enemy["basis"]


def test_permanent_relation():
    assert permanent_relation("Sun", "Jupiter") == "friend"
    assert permanent_relation("Sun", "Mercury") == "neutral"
    assert permanent_relation("Sun", "Venus") == "enemy"


def test_vimshopaka_engine_live():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_id="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
    )
    out = run_vimshopaka_engine(subject)
    assert out["engine"] == "Vimshopaka"
    assert out["engine_version"] == "0.1.0-shodashavarga"
    assert "TEC-025" in out["technique_ids"]
    pack = out["vimshopaka"]
    assert pack["variant"] == "vimshopaka_shodashavarga_candidate_v1"
    assert pack["summary"]["planet_count"] == 7
    assert pack["summary"]["strongest"]
    sun = next(p for p in pack["planets"] if p["planet"] == "Sun")
    assert 0.0 < sun["vimshopaka"] <= 20.0
    assert len(sun["contributions"]) == 16
    assert any(c["varga"] == "D4" for c in sun["contributions"])

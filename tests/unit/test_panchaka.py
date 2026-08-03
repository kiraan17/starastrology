"""Unit tests for Panchaka / Bhadra (P26a / TEC-074)."""

from __future__ import annotations

from datetime import datetime

from bhava360.kernel.models import SubjectInput
from bhava360.timing.panchaka import (
    bhadra_from_karana,
    evaluate_panchaka_bhadra,
    moon_panchak_window,
    panchaka_rahita,
)
from bhava360.timing.panchaka_engine import run_panchaka_bhadra_engine


def test_moon_panchak_inactive_before_300():
    out = moon_panchak_window(299.9)
    assert out["active"] is False
    assert out["segment"] is None
    assert out["deferred_activity_labels"] == []


def test_moon_panchak_active_dhanishta_pada3():
    out = moon_panchak_window(300.0)
    assert out["active"] is True
    assert out["segment"] == "Dhanishta"
    assert "southward_travel" in out["deferred_activity_labels"]


def test_moon_panchak_revathi():
    out = moon_panchak_window(350.0)
    assert out["active"] is True
    assert out["segment"] == "Revathi"


def test_panchaka_rahita_clear():
    # sum 3+5+7+9 = 24 → rem 6 → Chora (afflicted)
    afflicted = panchaka_rahita(
        tithi_index=3, vara_index=5, nakshatra_index=7, lagna_sign_index=9
    )
    assert afflicted["afflicted"] is True
    assert afflicted["type"] == "Chora"
    assert afflicted["rahita"] is False

    # rem 0 → Rahita
    clear = panchaka_rahita(
        tithi_index=1, vara_index=1, nakshatra_index=1, lagna_sign_index=6
    )
    assert clear["sum"] % 9 == 0
    assert clear["rahita"] is True
    assert clear["type"] is None


def test_bhadra_vishti():
    assert bhadra_from_karana("Vishti")["active"] is True
    assert bhadra_from_karana("Bava")["active"] is False


def test_evaluate_combined_flags():
    out = evaluate_panchaka_bhadra(
        moon_lon_sidereal=305.0,
        lagna_lon_sidereal=10.0,  # Aries = 1
        tithi_index=1,
        vara_index=1,
        nakshatra_index=1,
        karana_name="Vishti",
    )
    assert out["summary"]["moon_panchak_active"] is True
    assert out["summary"]["bhadra_active"] is True
    assert "bhadra_vishti" in out["summary"]["caution_flags"]
    assert "moon_panchak" in out["summary"]["caution_flags"]


def test_panchaka_engine_live():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_id="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
    )
    out = run_panchaka_bhadra_engine(subject)
    assert out["engine"] == "PanchakaBhadra"
    assert "TEC-074" in out["technique_ids"]
    pack = out["panchaka_bhadra"]
    assert "moon_panchak" in pack
    assert "panchaka_rahita" in pack
    assert "bhadra" in pack
    assert isinstance(pack["summary"]["caution_flag_count"], int)
    assert out["safety"]["note"]

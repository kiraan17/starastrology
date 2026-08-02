"""Unit tests for Prashna scaffold (P19b / TEC-086..088)."""

from __future__ import annotations

from datetime import datetime

import pytest

from bhava360.engines.prashna import run_prashna_engine
from bhava360.engines.prashna.manual import normalize_ashtamangala_counts
from bhava360.engines.prashna.sphutas import compute_prashna_sphutas, trisphuta
from bhava360.kernel.errors import KernelError
from bhava360.kernel.models import SubjectInput


def test_trisphuta_sum():
    out = trisphuta(lagna_longitude=10.0, moon_longitude=20.0, sun_longitude=30.0)
    assert abs(out["longitude_sidereal_deg"] - 60.0) < 1e-9


def test_chatusphuta_with_gulika():
    out = compute_prashna_sphutas(
        lagna_longitude=10.0,
        moon_longitude=20.0,
        sun_longitude=30.0,
        gulika_longitude=40.0,
    )
    assert abs(out["trisphuta"]["longitude_sidereal_deg"] - 60.0) < 1e-9
    assert abs(out["chatusphuta"]["longitude_sidereal_deg"] - 100.0) < 1e-9


def test_ashtamangala_awaits_manual_when_missing():
    out = normalize_ashtamangala_counts(None)
    assert out["provided"] is False
    assert out["status"] == "awaiting_manual_input"


def test_ashtamangala_records_operator_counts():
    out = normalize_ashtamangala_counts("3,5,2,7")
    assert out["provided"] is True
    assert out["counts"] == [3, 5, 2, 7]
    assert out["count_total"] == 17


def test_ashtamangala_rejects_negative():
    with pytest.raises(KernelError):
        normalize_ashtamangala_counts([-1, 2])


def test_prashna_engine_live_without_manual():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_offset_minutes=330,
        latitude=13.0827,
        longitude=80.2707,
        location_label="Chennai",
    )
    out = run_prashna_engine(subject, question_text="Will the trip succeed?")
    assert out["engine"] == "Prashna"
    assert "TEC-086" in out["technique_ids"]
    assert out["prashna_lagna"]["sign"]
    assert out["sphutas"]["trisphuta"]["sign"]
    assert out["sphutas"]["chatusphuta"] is not None
    assert out["sphutas"]["gulika"] is not None
    assert out["manual_inputs"]["ashtamangala"]["provided"] is False
    assert out["question"]["text"] == "Will the trip succeed?"
    assert out["arudha_lagna"]["arudha_sign"]


def test_prashna_engine_with_manual_counts():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_id="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
    )
    out = run_prashna_engine(subject, ashtamangala_counts=[1, 2, 3, 4])
    ash = out["manual_inputs"]["ashtamangala"]
    assert ash["provided"] is True
    assert ash["counts"] == [1, 2, 3, 4]

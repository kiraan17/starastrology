"""Unit tests for Numerology thin slice (P21a / TEC-092)."""

from __future__ import annotations

from datetime import date, datetime

import pytest

from bhava360.engines.numerology import run_numerology_engine
from bhava360.engines.numerology.numbers import (
    birth_number,
    destiny_number,
    name_number_chaldean,
    reduce_to_single_digit,
)
from bhava360.kernel.errors import KernelError
from bhava360.kernel.models import SubjectInput


def test_reduce_multiples_of_nine():
    assert reduce_to_single_digit(9) == 9
    assert reduce_to_single_digit(18) == 9
    assert reduce_to_single_digit(1990) == 1  # 1+9+9+0 → 19 → 10 → 1
    assert reduce_to_single_digit(27) == 9


def test_birth_number_day_28():
    out = birth_number(28)
    assert out["raw"] == 28
    assert out["value"] == 1  # 2+8=10 → 1
    assert out["ruling_planet"] == "Sun"


def test_destiny_number_known_date():
    # 15 + 8 + 1990 = 2013 → 6
    out = destiny_number(1990, 8, 15)
    assert out["raw"] == 2013
    assert out["value"] == 6
    assert out["ruling_planet"] == "Venus"


def test_name_number_chaldean_rama():
    # R=2 A=1 M=4 A=1 → 8
    out = name_number_chaldean("Rama")
    assert out["raw"] == 8
    assert out["value"] == 8
    assert out["ruling_planet"] == "Saturn"


def test_name_ignores_spaces_and_punctuation():
    a = name_number_chaldean("John Doe")
    b = name_number_chaldean("John-Doe")
    assert a["value"] == b["value"]
    assert a["raw"] == b["raw"]


def test_empty_name_raises():
    with pytest.raises(ValueError):
        name_number_chaldean("   ")


def test_engine_from_subject_without_name():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_offset_minutes=330,
        latitude=13.0827,
        longitude=80.2707,
    )
    out = run_numerology_engine(subject)
    assert out["engine"] == "Numerology"
    assert "TEC-092" in out["technique_ids"]
    profile = out["profile"]
    assert profile["birth_number"]["value"] == 6  # 1+5
    assert profile["destiny_number"]["value"] == 6
    assert profile["birth_destiny_aligned"] is True
    assert profile["name_number"] is None
    assert out["config"]["name_provided"] is False
    assert out["safety"]["note"]


def test_engine_with_name_and_civil_date():
    out = run_numerology_engine(civil_date=date(1992, 10, 25), name="John Doe")
    profile = out["profile"]
    assert profile["birth_number"]["value"] == 7  # 2+5
    assert profile["name_number"]["value"] >= 1
    assert profile["name_birth_aligned"] in (True, False)
    assert out["config"]["name_provided"] is True


def test_engine_requires_input():
    with pytest.raises(KernelError):
        run_numerology_engine()

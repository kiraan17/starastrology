from __future__ import annotations

from datetime import datetime, timezone

import pytest

from bhava360.kernel.models import PlanetName
from bhava360.timing.vimshottari import (
    DashaLevel,
    MEAN_YEAR_DAYS,
    VIMSHOTTARI_YEARS,
    assert_timeline_continuous,
    build_maha_timeline,
    build_vimshottari_tree,
    expand_subperiods,
    nakshatra_lord,
    vimshottari_balance,
)


def test_ashwini_lord_is_ketu():
    assert nakshatra_lord(0) == PlanetName.KETU
    assert nakshatra_lord(3) == PlanetName.MOON  # Rohini


def test_balance_at_nakshatra_start_is_full():
    # Exact start of Rohini (nakshatra index 3): 3 * 13°20' (+ epsilon for float edges)
    span = 360.0 / 27.0
    lon = 3 * span + 1e-12
    bal = vimshottari_balance(lon)
    assert bal.lord == PlanetName.MOON
    assert bal.elapsed_fraction == pytest.approx(0.0, abs=1e-9)
    assert bal.balance_years == pytest.approx(10.0, abs=1e-9)


def test_balance_at_nakshatra_end_near_zero():
    span = 360.0 / 27.0
    lon = 4 * span - 1e-9
    bal = vimshottari_balance(lon)
    assert bal.lord == PlanetName.MOON
    assert bal.balance_years == pytest.approx(0.0, abs=1e-6)


def test_maha_timeline_continuous_and_ordered():
    birth = datetime(1990, 8, 15, 6, 30, tzinfo=timezone.utc)
    # Chennai moon ~49.82 (Rohini)
    bal, mahas = build_maha_timeline(birth, 49.82142086935811, years_ahead=120.0)
    assert bal.lord == PlanetName.MOON
    assert_timeline_continuous(mahas)
    assert mahas[0].lord == PlanetName.MOON
    assert mahas[1].lord == PlanetName.MARS
    # First period shorter than full Moon dasha
    assert mahas[0].duration_days < 10 * MEAN_YEAR_DAYS


def test_antar_spans_match_parent():
    birth = datetime(1990, 8, 15, 6, 30, tzinfo=timezone.utc)
    _bal, mahas = build_maha_timeline(birth, 49.82142086935811, years_ahead=40.0)
    parent = mahas[0]
    kids = expand_subperiods(parent, DashaLevel.ANTAR)
    assert len(kids) == 9
    assert_timeline_continuous(kids)
    assert kids[0].lord == parent.lord
    assert kids[0].start_utc == parent.start_utc
    assert abs((kids[-1].end_utc - parent.end_utc).total_seconds()) <= 1.0
    # Proportional durations sum to parent
    assert sum(k.duration_days for k in kids) == pytest.approx(parent.duration_days, abs=1e-6)


def test_tree_to_pratyantar():
    birth = datetime(2000, 1, 1, 12, 0, tzinfo=timezone.utc)
    tree = build_vimshottari_tree(
        birth,
        0.0,  # Aswini start → Ketu balance full 7y
        depth=DashaLevel.PRATYANTAR,
        years_ahead=7.0,
    )
    assert tree["balance"]["lord"] == "Ketu"
    assert "maha" in tree["levels"]
    assert "antar" in tree["levels"]
    assert "pratyantar" in tree["levels"]
    assert len(tree["levels"]["maha"]) >= 1
    assert len(tree["levels"]["antar"]) == len(tree["levels"]["maha"]) * 9

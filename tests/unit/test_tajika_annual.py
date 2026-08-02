"""Unit tests for Tajika annual thin slice (P17a)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from bhava360.engines.tajika.annual import (
    completed_years_at,
    compute_muntha,
    resolve_annual_location,
)
from bhava360.engines.tajika import run_tajika_annual_engine
from bhava360.kernel.errors import KernelError
from bhava360.kernel.models import SubjectInput


def _subject() -> SubjectInput:
    return SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_offset_minutes=330,
        latitude=13.0827,
        longitude=80.2707,
        location_label="Chennai",
    )


def test_muntha_advances_from_lagna():
    out = compute_muntha(natal_lagna_sign="Aries", completed_years=0)
    assert out["sign"] == "Aries"
    assert out["lord"] == "Mars"

    out30 = compute_muntha(natal_lagna_sign="Aries", completed_years=30)
    assert out30["sign"] == "Libra"  # 0+30 = 6 mod 12
    assert out30["lord"] == "Venus"


def test_muntha_rejects_negative_years():
    with pytest.raises(KernelError):
        compute_muntha(natal_lagna_sign="Aries", completed_years=-1)


def test_completed_years_at():
    birth = datetime(1990, 8, 15, 6, 30, tzinfo=timezone.utc)
    assert completed_years_at(birth, datetime(2020, 8, 15, 7, 0, tzinfo=timezone.utc)) == 30
    assert completed_years_at(birth, datetime(2020, 8, 14, 7, 0, tzinfo=timezone.utc)) == 29


def test_resolve_annual_location_birth_place():
    loc = resolve_annual_location(
        location_rule="birth_place",
        natal_lat=13.0,
        natal_lon=80.0,
    )
    assert loc["location_rule"] == "birth_place"
    assert loc["latitude"] == 13.0


def test_resolve_annual_location_residence_requires_coords():
    with pytest.raises(KernelError):
        resolve_annual_location(
            location_rule="residence",
            natal_lat=13.0,
            natal_lon=80.0,
        )
    loc = resolve_annual_location(
        location_rule="residence",
        natal_lat=13.0,
        natal_lon=80.0,
        residence_lat=28.6,
        residence_lon=77.2,
    )
    assert loc["latitude"] == 28.6


def test_tajika_annual_engine_solar_return_and_muntha():
    out = run_tajika_annual_engine(_subject(), target_year=2020)
    assert out["engine"] == "TajikaAnnual"
    assert out["engine_version"] == "0.3.0-sahams-aspects"
    assert out["school"] == "tajika"
    assert out["target_year"] == 2020
    assert out["completed_years"] == 30
    assert out["config"]["annual.location_rule"] == "birth_place"
    assert out["annual_location"]["variant_id"] == "VARIANT-002"
    assert out["solar_return"]["sun_longitude_error_deg"] < 0.01
    assert out["muntha"]["sign"]
    assert out["muntha"]["year_lord_candidate"]
    assert 1 <= out["muntha"]["house_from_varsha_lagna"] <= 12
    assert out["varsha_chart"]["lagna_sign"]
    assert out["school"] == "tajika"
    assert "TEC-079" in out["technique_ids"]
    assert "TEC-078" in out["technique_ids"]
    tp = out["tithi_pravesh"]
    assert tp["elongation_error_deg"] < 0.01
    assert tp["tithi"]["index"] == out["natal_tithi"]["index"]
    assert abs(tp["days_from_solar_return"]) <= 20
    assert len(out["sahams"]["sahams"]) == 5
    assert "Full Saham catalog" in " ".join(out["deferred"])
    assert "Sahams (TEC-078)" not in out["deferred"]


def test_tithi_pravesh_search_helper():
    from bhava360.engines.tajika.tithi_pravesh import find_tithi_pravesh_jd, moon_sun_elongation
    from bhava360.kernel.provider import SwissEphemerisProvider

    provider = SwissEphemerisProvider()
    flags = provider._flags(sidereal=True)
    # Use a known JD near 2020-08-15 and a synthetic natal elongation.
    center = 2459076.0  # ~2020-08-15
    natal_elong = moon_sun_elongation(center - 3.0, flags)
    jd = find_tithi_pravesh_jd(
        natal_elongation_deg=natal_elong,
        center_jd_ut=center,
        sidereal_flags=flags,
    )
    err = abs(((moon_sun_elongation(jd, flags) - natal_elong + 180.0) % 360.0) - 180.0)
    assert err < 0.01
    assert abs(jd - center) <= 20


def test_tajika_rejects_year_before_birth():
    with pytest.raises(KernelError):
        run_tajika_annual_engine(_subject(), target_year=1980)

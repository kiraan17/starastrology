from __future__ import annotations

from datetime import datetime

import pytest

from bhava360.kernel.derived import (
    house_index_for_longitude,
    whole_sign_cusp_longitudes,
)
from bhava360.kernel.errors import KernelError, KernelErrorCode
from bhava360.kernel.models import ChartConfig, HouseSystem, PlanetName, SubjectInput
from bhava360.kernel.provider import SwissEphemerisProvider
from bhava360.kernel.snapshot import build_planet_snapshot

CHENNAI = SubjectInput(
    local_datetime=datetime(1990, 8, 15, 12, 0),
    timezone_offset_minutes=330,
    latitude=13.0827,
    longitude=80.2707,
    location_label="Chennai",
)


def test_houses_require_coordinates():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_offset_minutes=330,
    )
    with pytest.raises(KernelError) as exc:
        SwissEphemerisProvider().houses(subject)
    assert exc.value.code == KernelErrorCode.INVALID_LOCATION


def test_whole_sign_cusps_from_asc_sign():
    # Asc in Libra (205°) → house 1 starts at 180°
    cusps = whole_sign_cusp_longitudes(205.68)
    assert cusps[0] == 180.0
    assert cusps[1] == 210.0
    assert len(cusps) == 12
    # Continuity: each step +30
    for i in range(11):
        assert (cusps[i + 1] - cusps[i]) % 360 == 30.0


def test_whole_sign_boundary_just_below_and_above_sign_change():
    below = whole_sign_cusp_longitudes(209.999)
    above = whole_sign_cusp_longitudes(210.0001)
    assert below[0] == 180.0  # still Libra
    assert above[0] == 210.0  # Scorpio


def test_chennai_whole_sign_and_placidus():
    provider = SwissEphemerisProvider(ChartConfig(house_system=HouseSystem.WHOLE_SIGN))
    whole = provider.houses(CHENNAI, HouseSystem.WHOLE_SIGN)
    plac = provider.houses(CHENNAI, HouseSystem.PLACIDUS)

    assert whole.system == HouseSystem.WHOLE_SIGN
    assert plac.system == HouseSystem.PLACIDUS
    # Same Asc/MC source
    assert whole.ascendant.longitude_sidereal_deg == pytest.approx(
        plac.ascendant.longitude_sidereal_deg, abs=1e-8
    )
    assert plac.cusps[0].longitude_sidereal_deg == pytest.approx(
        plac.ascendant.longitude_sidereal_deg, abs=1e-6
    )
    assert plac.cusps[9].longitude_sidereal_deg == pytest.approx(
        plac.midheaven.longitude_sidereal_deg, abs=1e-6
    )
    # Whole-sign house 1 is 0° of Asc sign
    asc = whole.ascendant.longitude_sidereal_deg
    assert whole.cusps[0].longitude_sidereal_deg == float(int(asc // 30) * 30)


def test_planet_house_whole_sign_sun_in_chennai():
    provider = SwissEphemerisProvider()
    house = provider.planet_house(CHENNAI, PlanetName.SUN, HouseSystem.WHOLE_SIGN)
    assert 1 <= house <= 12
    # Consistency with cusp helper
    houses = provider.houses(CHENNAI, HouseSystem.WHOLE_SIGN)
    sun = provider.planet_position(CHENNAI, PlanetName.SUN)
    expected = house_index_for_longitude(
        sun.longitude_sidereal_deg,
        [c.longitude_sidereal_deg for c in houses.cusps],
    )
    assert house == expected


def test_day_window_chennai_sunrise_before_sunset():
    window = SwissEphemerisProvider().day_window(CHENNAI)
    assert window.sunrise_jd_ut < window.sunset_jd_ut
    # Local sunrise should be on 15 Aug 1990 morning IST-ish
    assert "1990-08-15" in window.sunrise_local
    assert "1990-08-15" in window.sunset_local or "1990-08-16" in window.sunset_local


def test_day_window_differs_by_longitude():
    singapore = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_offset_minutes=480,
        latitude=1.3521,
        longitude=103.8198,
        location_label="Singapore",
    )
    provider = SwissEphemerisProvider()
    chennai_w = provider.day_window(CHENNAI)
    singapore_w = provider.day_window(singapore)
    assert chennai_w.sunrise_jd_ut != pytest.approx(singapore_w.sunrise_jd_ut, abs=1e-6)


def test_snapshot_includes_houses_and_day_window_with_coords():
    snap = build_planet_snapshot(CHENNAI).to_dict()
    assert snap["houses"] is not None
    assert len(snap["houses"]["cusps"]) == 12
    assert "Sun" in snap["houses"]["planet_houses"]
    assert snap["day_window"] is not None
    assert snap["config"]["calc_library_version"] == "bhava360-kernel-0.2.0"

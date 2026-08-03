from __future__ import annotations

import math
from datetime import datetime

import pytest

from bhava360.kernel.errors import KernelError, KernelErrorCode
from bhava360.kernel.models import ChartConfig, PlanetName, SubjectInput
from bhava360.kernel.provider import SwissEphemerisProvider
from bhava360.kernel.timeutil import parse_vedastro_time_token, resolve_subject_time


def test_resolve_chennai_offset():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_offset_minutes=330,
    )
    resolved = resolve_subject_time(subject)
    assert resolved.utc_datetime.hour == 6
    assert resolved.utc_datetime.minute == 30
    assert resolved.julian_day_ut == pytest.approx(2448118.7708333335, rel=0, abs=1e-9)


def test_rejects_aware_local_datetime():
    from datetime import timezone

    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0, tzinfo=timezone.utc),
        timezone_offset_minutes=0,
    )
    with pytest.raises(KernelError) as exc:
        resolve_subject_time(subject)
    assert exc.value.code == KernelErrorCode.INVALID_DATETIME


def test_parse_vedastro_time_token():
    local, offset = parse_vedastro_time_token("14:30/04/07/1976/-04:00")
    assert local == datetime(1976, 7, 4, 14, 30)
    assert offset == -240


def test_sun_longitude_chennai_smoke():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_offset_minutes=330,
        location_label="Chennai",
    )
    pos = SwissEphemerisProvider(ChartConfig()).planet_position(subject, PlanetName.SUN)
    assert pos.sign == "Cancer"
    assert math.isfinite(pos.longitude_sidereal_deg)
    assert 0 <= pos.longitude_sidereal_deg < 360

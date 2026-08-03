"""P07c — IANA timezone / DST history tests."""

from __future__ import annotations

from datetime import datetime

import pytest

from bhava360.chart.builder import ChartConstructor
from bhava360.kernel.errors import KernelError, KernelErrorCode
from bhava360.kernel.models import SubjectInput
from bhava360.kernel.timeutil import resolve_subject_time


def test_iana_asia_kolkata_matches_fixed_offset():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_id="Asia/Kolkata",
    )
    resolved = resolve_subject_time(subject)
    assert resolved.timezone_source == "iana"
    assert resolved.timezone_id == "Asia/Kolkata"
    assert resolved.timezone_offset_minutes == 330
    assert resolved.utc_datetime.hour == 6
    assert resolved.utc_datetime.minute == 30
    assert resolved.is_dst is False
    assert resolved.ambiguous_local_time is False


def test_iana_new_york_dst_summer_and_winter():
    summer = resolve_subject_time(
        SubjectInput(
            local_datetime=datetime(2024, 7, 4, 14, 30),
            timezone_id="America/New_York",
        )
    )
    winter = resolve_subject_time(
        SubjectInput(
            local_datetime=datetime(2024, 1, 4, 14, 30),
            timezone_id="America/New_York",
        )
    )
    assert summer.is_dst is True
    assert summer.timezone_offset_minutes == -240  # EDT
    assert winter.is_dst is False
    assert winter.timezone_offset_minutes == -300  # EST


def test_dst_gap_raises():
    # US spring forward 2024-03-10: 02:30 does not exist.
    with pytest.raises(KernelError) as exc:
        resolve_subject_time(
            SubjectInput(
                local_datetime=datetime(2024, 3, 10, 2, 30),
                timezone_id="America/New_York",
            )
        )
    assert exc.value.code == KernelErrorCode.INVALID_DATETIME
    assert "DST gap" in exc.value.message


def test_dst_ambiguous_earlier_vs_later():
    local = datetime(2024, 11, 3, 1, 30)
    earlier = resolve_subject_time(
        SubjectInput(
            local_datetime=local,
            timezone_id="America/New_York",
            dst_ambiguity_policy="earlier",
        )
    )
    later = resolve_subject_time(
        SubjectInput(
            local_datetime=local,
            timezone_id="America/New_York",
            dst_ambiguity_policy="later",
        )
    )
    assert earlier.ambiguous_local_time is True
    assert later.ambiguous_local_time is True
    assert earlier.dst_fold == 0
    assert later.dst_fold == 1
    assert earlier.timezone_offset_minutes == -240
    assert later.timezone_offset_minutes == -300
    assert earlier.utc_datetime != later.utc_datetime


def test_dst_ambiguous_raise_policy():
    with pytest.raises(KernelError) as exc:
        resolve_subject_time(
            SubjectInput(
                local_datetime=datetime(2024, 11, 3, 1, 30),
                timezone_id="America/New_York",
                dst_ambiguity_policy="raise",
            )
        )
    assert exc.value.code == KernelErrorCode.INVALID_DATETIME
    assert "ambiguous" in exc.value.message


def test_unknown_iana_id():
    with pytest.raises(KernelError) as exc:
        resolve_subject_time(
            SubjectInput(
                local_datetime=datetime(1990, 8, 15, 12, 0),
                timezone_id="Not/A_Real_Zone",
            )
        )
    assert exc.value.code == KernelErrorCode.INVALID_TIMEZONE


def test_offset_iana_disagreement_raises():
    with pytest.raises(KernelError) as exc:
        resolve_subject_time(
            SubjectInput(
                local_datetime=datetime(1990, 8, 15, 12, 0),
                timezone_id="Asia/Kolkata",
                timezone_offset_minutes=0,
            )
        )
    assert exc.value.code == KernelErrorCode.INVALID_TIMEZONE


def test_requires_timezone_or_offset():
    with pytest.raises(KernelError) as exc:
        resolve_subject_time(
            SubjectInput(local_datetime=datetime(1990, 8, 15, 12, 0))
        )
    assert exc.value.code == KernelErrorCode.INVALID_TIMEZONE


def test_chart_constructor_stamps_iana_resolved_time():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_id="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
        location_label="Chennai",
    )
    chart = ChartConstructor().build(subject, include_vimshottari=False).to_dict()
    assert chart["config"]["calc_library_version"] == "bhava360-kernel-0.6.0"
    assert chart["resolved_time"]["timezone_source"] == "iana"
    assert chart["resolved_time"]["timezone_id"] == "Asia/Kolkata"
    assert chart["resolved_time"]["timezone_offset_minutes"] == 330
    assert chart["input"]["timezone_id"] == "Asia/Kolkata"

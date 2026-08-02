from __future__ import annotations

from datetime import datetime, timedelta, timezone

import swisseph as swe

from bhava360.kernel.errors import KernelError, KernelErrorCode
from bhava360.kernel.models import ResolvedTime, SubjectInput


def resolve_subject_time(subject: SubjectInput) -> ResolvedTime:
    """Convert naive local civil time + fixed offset to UTC and Julian Day UT."""
    subject.validate()
    try:
        offset = timezone(timedelta(minutes=subject.timezone_offset_minutes))
        local_aware = subject.local_datetime.replace(tzinfo=offset)
        utc_dt = local_aware.astimezone(timezone.utc)
    except Exception as exc:  # noqa: BLE001 - normalize to kernel error
        raise KernelError(
            KernelErrorCode.INVALID_DATETIME,
            "failed to resolve timezone offset",
            {"error": str(exc)},
        ) from exc

    hour = (
        utc_dt.hour
        + utc_dt.minute / 60.0
        + utc_dt.second / 3600.0
        + utc_dt.microsecond / 3_600_000_000.0
    )
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour)
    return ResolvedTime(
        local_datetime=subject.local_datetime,
        utc_datetime=utc_dt,
        timezone_offset_minutes=subject.timezone_offset_minutes,
        julian_day_ut=jd,
    )


def julian_day_to_utc(julian_day_ut: float) -> datetime:
    year, month, day, hour = swe.revjul(julian_day_ut, swe.GREG_CAL)
    hours = int(hour)
    minutes_f = (hour - hours) * 60.0
    minutes = int(minutes_f)
    seconds_f = (minutes_f - minutes) * 60.0
    seconds = int(seconds_f)
    micros = int(round((seconds_f - seconds) * 1_000_000))
    if micros == 1_000_000:
        seconds += 1
        micros = 0
    return datetime(
        int(year),
        int(month),
        int(day),
        hours,
        minutes,
        seconds,
        micros,
        tzinfo=timezone.utc,
    )


def require_coordinates(subject: SubjectInput) -> tuple[float, float]:
    if subject.latitude is None or subject.longitude is None:
        raise KernelError(
            KernelErrorCode.INVALID_LOCATION,
            "latitude and longitude are required for houses and local day windows",
            {
                "latitude": subject.latitude,
                "longitude": subject.longitude,
            },
        )
    return float(subject.latitude), float(subject.longitude)


def parse_vedastro_time_token(token: str) -> tuple[datetime, int]:
    """Parse SPIKE-01 time token `HH:MM/DD/MM/YYYY/+HH:MM` or `-HH:MM`."""
    try:
        time_part, day, month, year, offset = token.split("/")
        hour_s, minute_s = time_part.split(":")
        sign = 1
        off = offset
        if off.startswith("+"):
            off = off[1:]
        elif off.startswith("-"):
            sign = -1
            off = off[1:]
        off_h, off_m = off.split(":")
        offset_minutes = sign * (int(off_h) * 60 + int(off_m))
        local = datetime(int(year), int(month), int(day), int(hour_s), int(minute_s))
        return local, offset_minutes
    except Exception as exc:  # noqa: BLE001
        raise KernelError(
            KernelErrorCode.INVALID_DATETIME,
            "invalid VedAstro time token",
            {"token": token, "error": str(exc)},
        ) from exc

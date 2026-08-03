from __future__ import annotations

from datetime import datetime, timedelta, timezone, tzinfo
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import swisseph as swe

from bhava360.kernel.errors import KernelError, KernelErrorCode
from bhava360.kernel.models import ResolvedTime, SubjectInput


def _offset_minutes(tz: tzinfo, aware: datetime) -> int:
    delta = aware.utcoffset()
    if delta is None:
        raise KernelError(
            KernelErrorCode.INVALID_TIMEZONE,
            "timezone produced no UTC offset",
        )
    return int(delta.total_seconds() // 60)


def _is_dst(aware: datetime) -> bool | None:
    dst = aware.dst()
    if dst is None:
        return None
    return dst != timedelta(0)


def _wall_roundtrip_matches(local_naive: datetime, aware: datetime) -> bool:
    back = aware.astimezone(timezone.utc).astimezone(aware.tzinfo)
    return back.replace(tzinfo=None) == local_naive and back.fold == aware.fold


def _is_ambiguous(local_naive: datetime, tz: ZoneInfo) -> bool:
    a0 = local_naive.replace(tzinfo=tz, fold=0)
    a1 = local_naive.replace(tzinfo=tz, fold=1)
    if not (_wall_roundtrip_matches(local_naive, a0) and _wall_roundtrip_matches(local_naive, a1)):
        return False
    return a0.utcoffset() != a1.utcoffset()


def _is_missing(local_naive: datetime, tz: ZoneInfo) -> bool:
    a0 = local_naive.replace(tzinfo=tz, fold=0)
    a1 = local_naive.replace(tzinfo=tz, fold=1)
    return not (
        _wall_roundtrip_matches(local_naive, a0) or _wall_roundtrip_matches(local_naive, a1)
    )


def load_zoneinfo(timezone_id: str) -> ZoneInfo:
    key = timezone_id.strip()
    try:
        return ZoneInfo(key)
    except ZoneInfoNotFoundError as exc:
        raise KernelError(
            KernelErrorCode.INVALID_TIMEZONE,
            "unknown IANA timezone id",
            {"timezone_id": key},
        ) from exc
    except Exception as exc:  # noqa: BLE001
        raise KernelError(
            KernelErrorCode.INVALID_TIMEZONE,
            "failed to load IANA timezone",
            {"timezone_id": key, "error": str(exc)},
        ) from exc


def subject_tzinfo(subject: SubjectInput) -> tzinfo:
    """Return tzinfo for local civil conversions (IANA preferred over fixed offset)."""
    subject.validate()
    if subject.timezone_id and subject.timezone_id.strip():
        return load_zoneinfo(subject.timezone_id)
    assert subject.timezone_offset_minutes is not None
    return timezone(timedelta(minutes=int(subject.timezone_offset_minutes)))


def _julian_day_ut(utc_dt: datetime) -> float:
    hour = (
        utc_dt.hour
        + utc_dt.minute / 60.0
        + utc_dt.second / 3600.0
        + utc_dt.microsecond / 3_600_000_000.0
    )
    return swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour)


def _resolve_fixed_offset(subject: SubjectInput) -> ResolvedTime:
    assert subject.timezone_offset_minutes is not None
    try:
        offset = timezone(timedelta(minutes=int(subject.timezone_offset_minutes)))
        local_aware = subject.local_datetime.replace(tzinfo=offset)
        utc_dt = local_aware.astimezone(timezone.utc)
    except Exception as exc:  # noqa: BLE001 - normalize to kernel error
        raise KernelError(
            KernelErrorCode.INVALID_DATETIME,
            "failed to resolve timezone offset",
            {"error": str(exc)},
        ) from exc

    return ResolvedTime(
        local_datetime=subject.local_datetime,
        utc_datetime=utc_dt,
        timezone_offset_minutes=int(subject.timezone_offset_minutes),
        julian_day_ut=_julian_day_ut(utc_dt),
        timezone_id=None,
        timezone_source="fixed_offset",
        is_dst=False,
        ambiguous_local_time=False,
        dst_fold=None,
        tzdb_key=None,
    )


def _resolve_iana(subject: SubjectInput) -> ResolvedTime:
    assert subject.timezone_id is not None
    tz = load_zoneinfo(subject.timezone_id)
    local = subject.local_datetime

    if _is_missing(local, tz):
        raise KernelError(
            KernelErrorCode.INVALID_DATETIME,
            "local civil time does not exist (DST gap)",
            {
                "timezone_id": subject.timezone_id,
                "local_datetime": local.isoformat(sep=" "),
            },
        )

    ambiguous = _is_ambiguous(local, tz)
    fold: int | None = None
    if ambiguous:
        policy = subject.dst_ambiguity_policy
        if policy == "raise":
            raise KernelError(
                KernelErrorCode.INVALID_DATETIME,
                "local civil time is ambiguous (DST overlap); set dst_ambiguity_policy",
                {
                    "timezone_id": subject.timezone_id,
                    "local_datetime": local.isoformat(sep=" "),
                    "dst_ambiguity_policy": policy,
                },
            )
        fold = 0 if policy == "earlier" else 1

    aware = local.replace(tzinfo=tz, fold=fold or 0)
    if not _wall_roundtrip_matches(local, aware):
        # Defensive: should be caught by missing/ambiguous checks.
        raise KernelError(
            KernelErrorCode.INVALID_DATETIME,
            "failed to attach IANA timezone to local civil time",
            {"timezone_id": subject.timezone_id},
        )

    utc_dt = aware.astimezone(timezone.utc)
    offset_min = _offset_minutes(tz, aware)

    # If caller also supplied a fixed offset, require agreement (audit guard).
    if subject.timezone_offset_minutes is not None and int(subject.timezone_offset_minutes) != offset_min:
        raise KernelError(
            KernelErrorCode.INVALID_TIMEZONE,
            "fixed timezone_offset_minutes disagrees with IANA-resolved offset",
            {
                "timezone_id": subject.timezone_id,
                "timezone_offset_minutes": subject.timezone_offset_minutes,
                "resolved_offset_minutes": offset_min,
                "ambiguous_local_time": ambiguous,
            },
        )

    return ResolvedTime(
        local_datetime=local,
        utc_datetime=utc_dt,
        timezone_offset_minutes=offset_min,
        julian_day_ut=_julian_day_ut(utc_dt),
        timezone_id=subject.timezone_id.strip(),
        timezone_source="iana",
        is_dst=_is_dst(aware),
        ambiguous_local_time=ambiguous,
        dst_fold=fold if ambiguous else None,
        tzdb_key=getattr(tz, "key", subject.timezone_id.strip()),
    )


def resolve_subject_time(subject: SubjectInput) -> ResolvedTime:
    """Convert naive local civil time to UTC and Julian Day UT.

    Prefer IANA `timezone_id` (DST-aware via the system/tzdata zone database).
    Fall back to fixed `timezone_offset_minutes` when no IANA id is provided.
    """
    subject.validate()
    if subject.timezone_id and subject.timezone_id.strip():
        return _resolve_iana(subject)
    return _resolve_fixed_offset(subject)


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
    except KernelError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise KernelError(
            KernelErrorCode.INVALID_DATETIME,
            "invalid VedAstro time token",
            {"token": token, "error": str(exc)},
        ) from exc

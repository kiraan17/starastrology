"""Muhurta windows: Rahu Kala, Yamaganda, Gulika, Abhijit, Hora, Chaughadiya (P16b)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Iterable

from bhava360.timing.panchanga import VARA_LORDS, VARA_NAMES

# Daytime 1-indexed eighths (sunrise→sunset) by weekday Sunday=0.
RAHU_KALA_EIGHTH: tuple[int, ...] = (8, 2, 7, 5, 6, 4, 3)
YAMAGANDA_EIGHTH: tuple[int, ...] = (5, 4, 3, 2, 1, 7, 6)
GULIKA_DAY_EIGHTH: tuple[int, ...] = (7, 6, 5, 4, 3, 2, 1)

# Planetary hora lord cycle starting from the day's vara lord.
HORA_CYCLE: tuple[str, ...] = (
    "Sun",
    "Venus",
    "Mercury",
    "Moon",
    "Saturn",
    "Jupiter",
    "Mars",
)

# Chaughadiya labels.
CH_UDVEG = "Udveg"
CH_CHAL = "Chal"
CH_LABH = "Labh"
CH_AMRIT = "Amrit"
CH_KAAL = "Kaal"
CH_SHUBH = "Shubh"
CH_ROG = "Rog"

# Day chaughadiya sequences (8) by Sunday..Saturday.
CHAUGHADIYA_DAY: tuple[tuple[str, ...], ...] = (
    (CH_UDVEG, CH_CHAL, CH_LABH, CH_AMRIT, CH_KAAL, CH_SHUBH, CH_ROG, CH_UDVEG),  # Sun
    (CH_AMRIT, CH_KAAL, CH_SHUBH, CH_ROG, CH_UDVEG, CH_CHAL, CH_LABH, CH_AMRIT),  # Mon
    (CH_ROG, CH_UDVEG, CH_CHAL, CH_LABH, CH_AMRIT, CH_KAAL, CH_SHUBH, CH_ROG),  # Tue
    (CH_LABH, CH_AMRIT, CH_KAAL, CH_SHUBH, CH_ROG, CH_UDVEG, CH_CHAL, CH_LABH),  # Wed
    (CH_SHUBH, CH_ROG, CH_UDVEG, CH_CHAL, CH_LABH, CH_AMRIT, CH_KAAL, CH_SHUBH),  # Thu
    (CH_CHAL, CH_LABH, CH_AMRIT, CH_KAAL, CH_SHUBH, CH_ROG, CH_UDVEG, CH_CHAL),  # Fri
    (CH_KAAL, CH_SHUBH, CH_ROG, CH_UDVEG, CH_CHAL, CH_LABH, CH_AMRIT, CH_KAAL),  # Sat
)

# Night chaughadiya sequences (8) by Sunday..Saturday (night following that sunrise day).
CHAUGHADIYA_NIGHT: tuple[tuple[str, ...], ...] = (
    (CH_SHUBH, CH_AMRIT, CH_CHAL, CH_ROG, CH_KAAL, CH_LABH, CH_UDVEG, CH_SHUBH),  # Sun night
    (CH_ROG, CH_KAAL, CH_LABH, CH_UDVEG, CH_SHUBH, CH_AMRIT, CH_CHAL, CH_ROG),  # Mon
    (CH_KAAL, CH_LABH, CH_UDVEG, CH_SHUBH, CH_AMRIT, CH_CHAL, CH_ROG, CH_KAAL),  # Tue
    (CH_UDVEG, CH_SHUBH, CH_AMRIT, CH_CHAL, CH_ROG, CH_KAAL, CH_LABH, CH_UDVEG),  # Wed
    (CH_AMRIT, CH_CHAL, CH_ROG, CH_KAAL, CH_LABH, CH_UDVEG, CH_SHUBH, CH_AMRIT),  # Thu
    (CH_CHAL, CH_ROG, CH_KAAL, CH_LABH, CH_UDVEG, CH_SHUBH, CH_AMRIT, CH_CHAL),  # Fri
    (CH_LABH, CH_UDVEG, CH_SHUBH, CH_AMRIT, CH_CHAL, CH_ROG, CH_KAAL, CH_LABH),  # Sat
)

MUHURTA_VARIANT = "classical_segments_candidate_v1"


def _as_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def sunday_index(local_dt: datetime) -> int:
    return (local_dt.weekday() + 1) % 7


def _segment(
    start: datetime,
    end: datetime,
    *,
    parts: int,
    part_1_indexed: int,
    name: str,
    kind: str,
) -> dict[str, Any]:
    if parts <= 0 or not (1 <= part_1_indexed <= parts):
        raise ValueError("invalid segment request")
    start_u = _as_utc(start)
    end_u = _as_utc(end)
    span = (end_u - start_u) / parts
    seg_start = start_u + span * (part_1_indexed - 1)
    seg_end = start_u + span * part_1_indexed
    return {
        "name": name,
        "kind": kind,
        "part": part_1_indexed,
        "parts": parts,
        "start_utc": _iso(seg_start),
        "end_utc": _iso(seg_end),
        "duration_minutes": (seg_end - seg_start).total_seconds() / 60.0,
    }


def compute_day_eighth_windows(
    *,
    sunrise: datetime,
    sunset: datetime,
    weekday_sunday_index: int,
) -> dict[str, Any]:
    """Rahu Kala, Yamaganda, Gulika for the daytime eighths."""
    i = weekday_sunday_index
    return {
        "rahu_kala": _segment(
            sunrise,
            sunset,
            parts=8,
            part_1_indexed=RAHU_KALA_EIGHTH[i],
            name="Rahu Kala",
            kind="inauspicious",
        ),
        "yamaganda": _segment(
            sunrise,
            sunset,
            parts=8,
            part_1_indexed=YAMAGANDA_EIGHTH[i],
            name="Yamaganda",
            kind="inauspicious",
        ),
        "gulika": _segment(
            sunrise,
            sunset,
            parts=8,
            part_1_indexed=GULIKA_DAY_EIGHTH[i],
            name="Gulika",
            kind="inauspicious",
        ),
        "weekday": VARA_NAMES[i],
        "variant": MUHURTA_VARIANT,
    }


def compute_abhijit(*, sunrise: datetime, sunset: datetime) -> dict[str, Any]:
    """Abhijit muhurta: centered on midday, duration = daytime/15."""
    rise = _as_utc(sunrise)
    sett = _as_utc(sunset)
    midday = rise + (sett - rise) / 2
    half = (sett - rise) / 30  # full muhurta = day/15 → half each side
    start = midday - half
    end = midday + half
    return {
        "name": "Abhijit",
        "kind": "auspicious",
        "start_utc": _iso(start),
        "end_utc": _iso(end),
        "midday_utc": _iso(midday),
        "duration_minutes": (end - start).total_seconds() / 60.0,
        "notes": ["Centered on sunrise–sunset midpoint; duration = daytime/15."],
    }


def _hora_lords_for_day(weekday_sunday_index: int) -> list[str]:
    start_lord = VARA_LORDS[weekday_sunday_index]
    start_idx = HORA_CYCLE.index(start_lord)
    return [HORA_CYCLE[(start_idx + i) % 7] for i in range(24)]


def compute_horas(
    *,
    sunrise: datetime,
    sunset: datetime,
    next_sunrise: datetime,
    weekday_sunday_index: int,
) -> dict[str, Any]:
    """12 day horas + 12 night horas; lords from day's vara lord cycle."""
    rise = _as_utc(sunrise)
    sett = _as_utc(sunset)
    nxt = _as_utc(next_sunrise)
    lords = _hora_lords_for_day(weekday_sunday_index)
    day_span = (sett - rise) / 12
    night_span = (nxt - sett) / 12
    horas: list[dict[str, Any]] = []
    for i in range(12):
        s = rise + day_span * i
        e = rise + day_span * (i + 1)
        horas.append(
            {
                "index": i + 1,
                "period": "day",
                "lord": lords[i],
                "start_utc": _iso(s),
                "end_utc": _iso(e),
            }
        )
    for i in range(12):
        s = sett + night_span * i
        e = sett + night_span * (i + 1)
        horas.append(
            {
                "index": i + 13,
                "period": "night",
                "lord": lords[12 + i],
                "start_utc": _iso(s),
                "end_utc": _iso(e),
            }
        )
    return {
        "horas": horas,
        "weekday": VARA_NAMES[weekday_sunday_index],
        "start_lord": VARA_LORDS[weekday_sunday_index],
        "variant": MUHURTA_VARIANT,
    }


def compute_chaughadiya(
    *,
    sunrise: datetime,
    sunset: datetime,
    next_sunrise: datetime,
    weekday_sunday_index: int,
) -> dict[str, Any]:
    """8 day + 8 night Chaughadiya segments."""
    rise = _as_utc(sunrise)
    sett = _as_utc(sunset)
    nxt = _as_utc(next_sunrise)
    day_seq = CHAUGHADIYA_DAY[weekday_sunday_index]
    night_seq = CHAUGHADIYA_NIGHT[weekday_sunday_index]
    day_span = (sett - rise) / 8
    night_span = (nxt - sett) / 8
    rows: list[dict[str, Any]] = []
    for i, label in enumerate(day_seq):
        s = rise + day_span * i
        e = rise + day_span * (i + 1)
        rows.append(
            {
                "index": i + 1,
                "period": "day",
                "label": label,
                "start_utc": _iso(s),
                "end_utc": _iso(e),
            }
        )
    for i, label in enumerate(night_seq):
        s = sett + night_span * i
        e = sett + night_span * (i + 1)
        rows.append(
            {
                "index": i + 9,
                "period": "night",
                "label": label,
                "start_utc": _iso(s),
                "end_utc": _iso(e),
            }
        )
    return {
        "segments": rows,
        "weekday": VARA_NAMES[weekday_sunday_index],
        "variant": MUHURTA_VARIANT,
    }


def _contains(now: datetime, start_iso: str, end_iso: str) -> bool:
    now_u = _as_utc(now)
    return datetime.fromisoformat(start_iso) <= now_u < datetime.fromisoformat(end_iso)


def active_window(now: datetime, windows: Iterable[dict[str, Any]]) -> dict[str, Any] | None:
    for w in windows:
        if "start_utc" in w and "end_utc" in w and _contains(now, w["start_utc"], w["end_utc"]):
            return w
    return None


def compute_muhurta_pack(
    *,
    sunrise: datetime,
    sunset: datetime,
    next_sunrise: datetime,
    when_utc: datetime,
) -> dict[str, Any]:
    """Full P16b pack + active flags at when_utc."""
    wd = sunday_index(sunrise)
    eighths = compute_day_eighth_windows(
        sunrise=sunrise, sunset=sunset, weekday_sunday_index=wd
    )
    abhijit = compute_abhijit(sunrise=sunrise, sunset=sunset)
    horas = compute_horas(
        sunrise=sunrise,
        sunset=sunset,
        next_sunrise=next_sunrise,
        weekday_sunday_index=wd,
    )
    chaugh = compute_chaughadiya(
        sunrise=sunrise,
        sunset=sunset,
        next_sunrise=next_sunrise,
        weekday_sunday_index=wd,
    )
    when = _as_utc(when_utc)
    active = {
        "rahu_kala": _contains(when, eighths["rahu_kala"]["start_utc"], eighths["rahu_kala"]["end_utc"]),
        "yamaganda": _contains(when, eighths["yamaganda"]["start_utc"], eighths["yamaganda"]["end_utc"]),
        "gulika": _contains(when, eighths["gulika"]["start_utc"], eighths["gulika"]["end_utc"]),
        "abhijit": _contains(when, abhijit["start_utc"], abhijit["end_utc"]),
        "hora": active_window(when, horas["horas"]),
        "chaughadiya": active_window(when, chaugh["segments"]),
    }
    return {
        "weekday": VARA_NAMES[wd],
        "day_eighths": eighths,
        "abhijit": abhijit,
        "horas": horas,
        "chaughadiya": chaugh,
        "active_at": _iso(when),
        "active": active,
        "variant": MUHURTA_VARIANT,
        "notes": [
            "Daytime Rahu/Yamaganda/Gulika use classical weekday eighth tables.",
            "Night Gulika not expanded in this thin slice.",
            "Hora lords cycle Sun→Venus→Mercury→Moon→Saturn→Jupiter→Mars from day's vara lord.",
            "Chaughadiya day/night sequences are Candidate classical tables.",
        ],
    }

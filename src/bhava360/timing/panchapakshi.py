"""Panchapakshi (five-bird) cycles — Candidate thin slice (TEC-075)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from bhava360.kernel.derived import NAKSHATRA_SPAN, normalize_longitude
from bhava360.kernel.models import NAKSHATRAS_VEDASTRO
from bhava360.timing.panchanga import VARA_NAMES

PANCHAPAKSHI_VARIANT = "panchapakshi_bright_half_candidate_v1"

BIRDS: tuple[str, ...] = ("Vulture", "Owl", "Crow", "Cock", "Peacock")
ACTIVITIES: tuple[str, ...] = ("Ruling", "Eating", "Walking", "Sleeping", "Dying")

ACTIVITY_RANK: dict[str, int] = {
    "Ruling": 5,
    "Eating": 4,
    "Walking": 3,
    "Sleeping": 2,
    "Dying": 1,
}

BIRD_ELEMENT_BRIGHT: dict[str, str] = {
    "Vulture": "Fire",
    "Owl": "Air",
    "Crow": "Earth",
    "Cock": "Water",
    "Peacock": "Ether",
}

# Nakshatra index 0..26 → bird for Shukla / Krishna (VedAstro Part 2 / Pulippani).
_BRIGHT_BY_NAK: tuple[str, ...] = (
    "Vulture",
    "Vulture",
    "Vulture",
    "Vulture",
    "Vulture",
    "Owl",
    "Owl",
    "Owl",
    "Owl",
    "Owl",
    "Crow",
    "Crow",
    "Crow",
    "Crow",
    "Crow",
    "Cock",
    "Cock",
    "Cock",
    "Cock",
    "Cock",
    "Peacock",
    "Peacock",
    "Peacock",
    "Peacock",
    "Peacock",
    "Peacock",
    "Peacock",
)
_DARK_BY_NAK: tuple[str, ...] = (
    "Peacock",
    "Peacock",
    "Peacock",
    "Peacock",
    "Peacock",
    "Peacock",
    "Peacock",
    "Cock",
    "Cock",
    "Cock",
    "Cock",
    "Cock",
    "Crow",
    "Crow",
    "Crow",
    "Crow",
    "Crow",
    "Owl",
    "Owl",
    "Owl",
    "Owl",
    "Owl",
    "Vulture",
    "Vulture",
    "Vulture",
    "Vulture",
    "Vulture",
)

# Bright-half weekday groups (Sunday=0). VedAstro Part 5.
_BRIGHT_GROUP_BY_WD: tuple[str, ...] = (
    "A",  # Sun
    "B",  # Mon
    "A",  # Tue
    "B",  # Wed
    "C",  # Thu
    "D",  # Fri
    "B",  # Sat
)

# Bright-half mirror: group → day|night → bird → 5 activities (Yama 1..5 / 6..10).
_BRIGHT_MIRROR: dict[str, dict[str, dict[str, tuple[str, ...]]]] = {
    "A": {
        "day": {
            "Vulture": ("Eating", "Walking", "Ruling", "Sleeping", "Dying"),
            "Owl": ("Ruling", "Dying", "Eating", "Walking", "Sleeping"),
            "Crow": ("Walking", "Sleeping", "Dying", "Ruling", "Eating"),
            "Cock": ("Dying", "Ruling", "Sleeping", "Eating", "Walking"),
            "Peacock": ("Sleeping", "Eating", "Walking", "Dying", "Ruling"),
        },
        "night": {
            "Vulture": ("Dying", "Ruling", "Sleeping", "Eating", "Walking"),
            "Owl": ("Sleeping", "Eating", "Walking", "Dying", "Ruling"),
            "Crow": ("Eating", "Walking", "Ruling", "Sleeping", "Dying"),
            "Cock": ("Walking", "Sleeping", "Dying", "Ruling", "Eating"),
            "Peacock": ("Ruling", "Dying", "Eating", "Walking", "Sleeping"),
        },
    },
    "B": {
        "day": {
            "Vulture": ("Dying", "Ruling", "Sleeping", "Eating", "Walking"),
            "Owl": ("Eating", "Walking", "Ruling", "Sleeping", "Dying"),
            "Crow": ("Sleeping", "Eating", "Walking", "Dying", "Ruling"),
            "Cock": ("Walking", "Sleeping", "Dying", "Ruling", "Eating"),
            "Peacock": ("Ruling", "Dying", "Eating", "Walking", "Sleeping"),
        },
        "night": {
            "Vulture": ("Walking", "Sleeping", "Dying", "Ruling", "Eating"),
            "Owl": ("Dying", "Ruling", "Sleeping", "Eating", "Walking"),
            "Crow": ("Ruling", "Dying", "Eating", "Walking", "Sleeping"),
            "Cock": ("Eating", "Walking", "Ruling", "Sleeping", "Dying"),
            "Peacock": ("Sleeping", "Eating", "Walking", "Dying", "Ruling"),
        },
    },
    "C": {
        "day": {
            "Vulture": ("Sleeping", "Eating", "Walking", "Dying", "Ruling"),
            "Owl": ("Walking", "Sleeping", "Dying", "Ruling", "Eating"),
            "Crow": ("Eating", "Walking", "Ruling", "Sleeping", "Dying"),
            "Cock": ("Ruling", "Dying", "Eating", "Walking", "Sleeping"),
            "Peacock": ("Dying", "Ruling", "Sleeping", "Eating", "Walking"),
        },
        "night": {
            "Vulture": ("Ruling", "Dying", "Eating", "Walking", "Sleeping"),
            "Owl": ("Eating", "Walking", "Ruling", "Sleeping", "Dying"),
            "Crow": ("Dying", "Ruling", "Sleeping", "Eating", "Walking"),
            "Cock": ("Sleeping", "Eating", "Walking", "Dying", "Ruling"),
            "Peacock": ("Walking", "Sleeping", "Dying", "Ruling", "Eating"),
        },
    },
    "D": {
        "day": {
            "Vulture": ("Walking", "Sleeping", "Dying", "Ruling", "Eating"),
            "Owl": ("Dying", "Ruling", "Sleeping", "Eating", "Walking"),
            "Crow": ("Ruling", "Dying", "Eating", "Walking", "Sleeping"),
            "Cock": ("Eating", "Walking", "Ruling", "Sleeping", "Dying"),
            "Peacock": ("Sleeping", "Eating", "Walking", "Dying", "Ruling"),
        },
        "night": {
            "Vulture": ("Eating", "Walking", "Ruling", "Sleeping", "Dying"),
            "Owl": ("Walking", "Sleeping", "Dying", "Ruling", "Eating"),
            "Crow": ("Sleeping", "Eating", "Walking", "Dying", "Ruling"),
            "Cock": ("Dying", "Ruling", "Sleeping", "Eating", "Walking"),
            "Peacock": ("Ruling", "Dying", "Eating", "Walking", "Sleeping"),
        },
    },
}


def _as_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def sunday_index(local_dt: datetime) -> int:
    # Use the civil date in the datetime's own zone when aware.
    local = local_dt
    if local.tzinfo is not None:
        local = local.replace(tzinfo=None)
    return (local.weekday() + 1) % 7


def birth_bird_from_nakshatra(*, nakshatra_index: int, paksha: str) -> dict[str, Any]:
    """Permanent birth bird from Moon nakshatra (1..27) + birth paksha."""
    idx0 = (int(nakshatra_index) - 1) % 27
    pak = paksha.strip().title()
    if pak not in {"Shukla", "Krishna"}:
        raise ValueError(f"unsupported paksha: {paksha}")
    bird = _BRIGHT_BY_NAK[idx0] if pak == "Shukla" else _DARK_BY_NAK[idx0]
    return {
        "bird": bird,
        "element": BIRD_ELEMENT_BRIGHT[bird],
        "nakshatra_index": idx0 + 1,
        "nakshatra": NAKSHATRAS_VEDASTRO[idx0],
        "paksha": pak,
        "basis": "moon_nakshatra_and_paksha",
    }


def birth_bird_from_moon_longitude(*, moon_lon_sidereal: float, paksha: str) -> dict[str, Any]:
    lon = normalize_longitude(moon_lon_sidereal)
    idx0 = int(lon // NAKSHATRA_SPAN) % 27
    return birth_bird_from_nakshatra(nakshatra_index=idx0 + 1, paksha=paksha)


def _split_yamas(start: datetime, end: datetime, *, offset: int) -> list[dict[str, Any]]:
    start_u = _as_utc(start)
    end_u = _as_utc(end)
    span = end_u - start_u
    if span.total_seconds() <= 0:
        raise ValueError("invalid yama window")
    part = span / 5
    rows: list[dict[str, Any]] = []
    for i in range(5):
        s = start_u + part * i
        e = end_u if i == 4 else start_u + part * (i + 1)
        rows.append(
            {
                "yama_index": offset + i,
                "phase": "day" if offset == 1 else "night",
                "start_utc": _iso(s),
                "end_utc": _iso(e),
            }
        )
    return rows


def build_yama_clock(
    *,
    sunrise: datetime,
    sunset: datetime,
    next_sunrise: datetime,
    when_utc: datetime,
) -> dict[str, Any]:
    """Five equal day yamas + five equal night yamas (Candidate)."""
    day = _split_yamas(sunrise, sunset, offset=1)
    night = _split_yamas(sunset, next_sunrise, offset=6)
    yamas = day + night
    when = _as_utc(when_utc)
    active = None
    for row in yamas:
        s = datetime.fromisoformat(row["start_utc"])
        e = datetime.fromisoformat(row["end_utc"])
        if s <= when < e or (row["yama_index"] == 10 and when == e):
            active = row
            break
    if active is None and when >= datetime.fromisoformat(yamas[-1]["start_utc"]):
        active = yamas[-1]
    return {
        "yamas": yamas,
        "active": active,
        "weekday": VARA_NAMES[sunday_index(sunrise)],
        "weekday_sunday_index": sunday_index(sunrise),
    }


def bright_half_group(weekday_sunday_index: int) -> str:
    return _BRIGHT_GROUP_BY_WD[weekday_sunday_index % 7]


def activity_class(activity: str) -> str:
    if activity in {"Ruling", "Eating"}:
        return "favorable"
    if activity in {"Sleeping", "Dying"}:
        return "avoid"
    return "mixed"


def lookup_bright_activity(*, bird: str, group: str, phase: str, yama_in_phase: int) -> str:
    seq = _BRIGHT_MIRROR[group][phase][bird]
    return seq[yama_in_phase]


def evaluate_panchapakshi(
    *,
    moon_lon_sidereal: float,
    paksha: str,
    sunrise: datetime,
    sunset: datetime,
    next_sunrise: datetime,
    when_utc: datetime,
) -> dict[str, Any]:
    """
    Birth bird + yama clock + activity at instant.

    Bright (Shukla) half uses VedAstro Part 5 mirror tables (Candidate).
    Dark (Krishna) half activity lookup is deferred (Source Needed — Part 6 tables inconsistent).
    """
    bird_info = birth_bird_from_moon_longitude(
        moon_lon_sidereal=moon_lon_sidereal, paksha=paksha
    )
    clock = build_yama_clock(
        sunrise=sunrise,
        sunset=sunset,
        next_sunrise=next_sunrise,
        when_utc=when_utc,
    )
    pak = paksha.strip().title()
    wd = clock["weekday_sunday_index"]
    group = bright_half_group(wd) if pak == "Shukla" else None
    active = clock["active"]
    current: dict[str, Any] | None = None
    schedule: list[dict[str, Any]] = []
    deferred: list[str] = []

    if pak == "Shukla" and active is not None and group is not None:
        phase = str(active["phase"])
        yama_idx = int(active["yama_index"])
        yama_in_phase = (yama_idx - 1) % 5
        act = lookup_bright_activity(
            bird=bird_info["bird"],
            group=group,
            phase=phase,
            yama_in_phase=yama_in_phase,
        )
        current = {
            "yama_index": yama_idx,
            "phase": phase,
            "activity": act,
            "activity_class": activity_class(act),
            "rank": ACTIVITY_RANK[act],
            "group": group,
            "start_utc": active["start_utc"],
            "end_utc": active["end_utc"],
        }
        for row in clock["yamas"]:
            p = str(row["phase"])
            yi = int(row["yama_index"])
            a = lookup_bright_activity(
                bird=bird_info["bird"],
                group=group,
                phase=p,
                yama_in_phase=(yi - 1) % 5,
            )
            schedule.append(
                {
                    **row,
                    "activity": a,
                    "activity_class": activity_class(a),
                    "rank": ACTIVITY_RANK[a],
                }
            )
    else:
        deferred.append(
            "Krishna-paksha (dark half) mirror activity tables: Source Needed "
            "(VedAstro Part 6 transcription has non-permutation rows)."
        )
        if active is not None:
            current = {
                "yama_index": active["yama_index"],
                "phase": active["phase"],
                "activity": None,
                "activity_class": None,
                "rank": None,
                "group": None,
                "start_utc": active["start_utc"],
                "end_utc": active["end_utc"],
                "status": "deferred_dark_half_activity",
            }

    return {
        "variant": PANCHAPAKSHI_VARIANT,
        "birth_bird": bird_info,
        "paksha": pak,
        "weekday": clock["weekday"],
        "bright_half_group": group,
        "yama_clock": {
            "active": clock["active"],
            "yama_count": len(clock["yamas"]),
        },
        "current": current,
        "schedule": schedule,
        "summary": {
            "bird": bird_info["bird"],
            "element": bird_info["element"],
            "paksha": pak,
            "weekday": clock["weekday"],
            "yama_index": (current or {}).get("yama_index"),
            "activity": (current or {}).get("activity"),
            "activity_class": (current or {}).get("activity_class"),
            "schedule_count": len(schedule),
            "dark_half_activity_deferred": pak == "Krishna",
        },
        "deferred": deferred
        + [
            "Sub-yama (upa-pakshi) nested activities",
            "Padu/Bharana companion birds",
            "Competitive bird-vs-bird verdicts",
        ],
        "notes": [
            "Candidate thin slice stamped from VedAstro Part 2 (bird) + Part 5 (Shukla mirrors).",
            "Yamas are equal fifths of local day and night (sunrise/sunset based).",
            "Bird is derived from the evaluated Moon nakshatra+paksha (same instant).",
            "Separate natal-bird + query-time schedule deferred.",
        ],
    }


__all__ = [
    "ACTIVITIES",
    "BIRDS",
    "PANCHAPAKSHI_VARIANT",
    "birth_bird_from_moon_longitude",
    "birth_bird_from_nakshatra",
    "build_yama_clock",
    "evaluate_panchapakshi",
]

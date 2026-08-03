"""Panchapakshi (five-bird) cycles — Candidate (TEC-075).

Major-activity mirrors derived from PyJHora V4.8.7 `pancha_pakshi_db.csv`
(AGPL-3.0; Candidate provenance). Sub-yamas / padu / bharana deferred.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from bhava360.kernel.derived import NAKSHATRA_SPAN, normalize_longitude
from bhava360.kernel.models import NAKSHATRAS_VEDASTRO
from bhava360.timing.panchanga import VARA_NAMES

PANCHAPAKSHI_VARIANT = "panchapakshi_pyjhora_major_candidate_v1"

BIRDS: tuple[str, ...] = ("Vulture", "Owl", "Crow", "Cock", "Peacock")
ACTIVITIES: tuple[str, ...] = ("Ruling", "Eating", "Walking", "Sleeping", "Dying")

ACTIVITY_RANK: dict[str, int] = {
    "Ruling": 5,
    "Eating": 4,
    "Walking": 3,
    "Sleeping": 2,
    "Dying": 1,
}

BIRD_ELEMENT: dict[str, str] = {
    "Vulture": "Fire",
    "Owl": "Air",
    "Crow": "Earth",
    "Cock": "Water",
    "Peacock": "Ether",
}

# PyJHora `pancha_pakshi_stars_birds_paksha` — (shukla_bird, krishna_bird) 0-based.
# Groups: 5, 6, 5, 5, 6.
_BIRTH_BIRD_BY_NAK: tuple[tuple[str, str], ...] = (
    *(("Vulture", "Peacock") for _ in range(5)),
    *(("Owl", "Cock") for _ in range(6)),
    *(("Crow", "Crow") for _ in range(5)),
    *(("Cock", "Owl") for _ in range(5)),
    *(("Peacock", "Vulture") for _ in range(6)),
)
assert len(_BIRTH_BIRD_BY_NAK) == 27

# Major activities (10 = day 1..5 + night 6..10) keyed by (paksha_idx, weekday_sun0, bird_idx).
# paksha: 0=Shukla, 1=Krishna. Derived from PyJHora pancha_pakshi_db.csv majors.
_MAJOR_ACTIVITIES: dict[tuple[int, int, int], tuple[str, ...]] = {
    # Shukla
    (0, 0, 0): ("Eating", "Walking", "Ruling", "Sleeping", "Dying", "Dying", "Walking", "Sleeping", "Eating", "Ruling"),
    (0, 0, 1): ("Walking", "Ruling", "Sleeping", "Dying", "Eating", "Ruling", "Dying", "Walking", "Sleeping", "Eating"),
    (0, 0, 2): ("Ruling", "Sleeping", "Dying", "Eating", "Walking", "Eating", "Ruling", "Dying", "Walking", "Sleeping"),
    (0, 0, 3): ("Sleeping", "Dying", "Eating", "Walking", "Ruling", "Sleeping", "Eating", "Ruling", "Dying", "Walking"),
    (0, 0, 4): ("Dying", "Eating", "Walking", "Ruling", "Sleeping", "Walking", "Sleeping", "Eating", "Ruling", "Dying"),
    (0, 1, 0): ("Dying", "Eating", "Walking", "Ruling", "Sleeping", "Walking", "Sleeping", "Eating", "Ruling", "Dying"),
    (0, 1, 1): ("Eating", "Walking", "Ruling", "Sleeping", "Dying", "Dying", "Walking", "Sleeping", "Eating", "Ruling"),
    (0, 1, 2): ("Walking", "Ruling", "Sleeping", "Dying", "Eating", "Ruling", "Dying", "Walking", "Sleeping", "Eating"),
    (0, 1, 3): ("Ruling", "Sleeping", "Dying", "Eating", "Walking", "Eating", "Ruling", "Dying", "Walking", "Sleeping"),
    (0, 1, 4): ("Sleeping", "Dying", "Eating", "Walking", "Ruling", "Sleeping", "Eating", "Ruling", "Dying", "Walking"),
    (0, 2, 0): ("Eating", "Walking", "Ruling", "Sleeping", "Dying", "Dying", "Walking", "Sleeping", "Eating", "Ruling"),
    (0, 2, 1): ("Walking", "Ruling", "Sleeping", "Dying", "Eating", "Ruling", "Dying", "Walking", "Sleeping", "Eating"),
    (0, 2, 2): ("Ruling", "Sleeping", "Dying", "Eating", "Walking", "Eating", "Ruling", "Dying", "Walking", "Sleeping"),
    (0, 2, 3): ("Sleeping", "Dying", "Eating", "Walking", "Ruling", "Sleeping", "Eating", "Ruling", "Dying", "Walking"),
    (0, 2, 4): ("Dying", "Eating", "Walking", "Ruling", "Sleeping", "Walking", "Sleeping", "Eating", "Ruling", "Dying"),
    (0, 3, 0): ("Dying", "Eating", "Walking", "Ruling", "Sleeping", "Walking", "Sleeping", "Eating", "Ruling", "Dying"),
    (0, 3, 1): ("Eating", "Walking", "Ruling", "Sleeping", "Dying", "Dying", "Walking", "Sleeping", "Eating", "Ruling"),
    (0, 3, 2): ("Walking", "Ruling", "Sleeping", "Dying", "Eating", "Ruling", "Dying", "Walking", "Sleeping", "Eating"),
    (0, 3, 3): ("Ruling", "Sleeping", "Dying", "Eating", "Walking", "Eating", "Ruling", "Dying", "Walking", "Sleeping"),
    (0, 3, 4): ("Sleeping", "Dying", "Eating", "Walking", "Ruling", "Sleeping", "Eating", "Ruling", "Dying", "Walking"),
    (0, 4, 0): ("Sleeping", "Dying", "Eating", "Walking", "Ruling", "Sleeping", "Eating", "Ruling", "Dying", "Walking"),
    (0, 4, 1): ("Dying", "Eating", "Walking", "Ruling", "Sleeping", "Walking", "Sleeping", "Eating", "Ruling", "Dying"),
    (0, 4, 2): ("Eating", "Walking", "Ruling", "Sleeping", "Dying", "Dying", "Walking", "Sleeping", "Eating", "Ruling"),
    (0, 4, 3): ("Walking", "Ruling", "Sleeping", "Dying", "Eating", "Ruling", "Dying", "Walking", "Sleeping", "Eating"),
    (0, 4, 4): ("Ruling", "Sleeping", "Dying", "Eating", "Walking", "Eating", "Ruling", "Dying", "Walking", "Sleeping"),
    (0, 5, 0): ("Ruling", "Sleeping", "Dying", "Eating", "Walking", "Eating", "Ruling", "Dying", "Walking", "Sleeping"),
    (0, 5, 1): ("Sleeping", "Dying", "Eating", "Walking", "Ruling", "Sleeping", "Eating", "Ruling", "Dying", "Walking"),
    (0, 5, 2): ("Dying", "Eating", "Walking", "Ruling", "Sleeping", "Walking", "Sleeping", "Eating", "Ruling", "Dying"),
    (0, 5, 3): ("Eating", "Walking", "Ruling", "Sleeping", "Dying", "Dying", "Walking", "Sleeping", "Eating", "Ruling"),
    (0, 5, 4): ("Walking", "Ruling", "Sleeping", "Dying", "Eating", "Ruling", "Dying", "Walking", "Sleeping", "Eating"),
    (0, 6, 0): ("Walking", "Ruling", "Sleeping", "Dying", "Eating", "Ruling", "Dying", "Walking", "Sleeping", "Eating"),
    (0, 6, 1): ("Ruling", "Sleeping", "Dying", "Eating", "Walking", "Eating", "Ruling", "Dying", "Walking", "Sleeping"),
    (0, 6, 2): ("Sleeping", "Dying", "Eating", "Walking", "Ruling", "Sleeping", "Eating", "Ruling", "Dying", "Walking"),
    (0, 6, 3): ("Dying", "Eating", "Walking", "Ruling", "Sleeping", "Walking", "Sleeping", "Eating", "Ruling", "Dying"),
    (0, 6, 4): ("Eating", "Walking", "Ruling", "Sleeping", "Dying", "Dying", "Walking", "Sleeping", "Eating", "Ruling"),
    # Krishna
    (1, 0, 0): ("Walking", "Eating", "Dying", "Sleeping", "Ruling", "Eating", "Sleeping", "Walking", "Dying", "Ruling"),
    (1, 0, 1): ("Dying", "Sleeping", "Ruling", "Walking", "Eating", "Ruling", "Eating", "Sleeping", "Walking", "Dying"),
    (1, 0, 2): ("Ruling", "Walking", "Eating", "Dying", "Sleeping", "Dying", "Ruling", "Eating", "Sleeping", "Walking"),
    (1, 0, 3): ("Eating", "Dying", "Sleeping", "Ruling", "Walking", "Walking", "Dying", "Ruling", "Eating", "Sleeping"),
    (1, 0, 4): ("Sleeping", "Ruling", "Walking", "Eating", "Dying", "Sleeping", "Walking", "Dying", "Ruling", "Eating"),
    (1, 1, 0): ("Sleeping", "Ruling", "Walking", "Eating", "Dying", "Dying", "Ruling", "Eating", "Sleeping", "Walking"),
    (1, 1, 1): ("Walking", "Eating", "Dying", "Sleeping", "Ruling", "Walking", "Dying", "Ruling", "Eating", "Sleeping"),
    (1, 1, 2): ("Dying", "Sleeping", "Ruling", "Walking", "Eating", "Sleeping", "Walking", "Dying", "Ruling", "Eating"),
    (1, 1, 3): ("Ruling", "Walking", "Eating", "Dying", "Sleeping", "Eating", "Sleeping", "Walking", "Dying", "Ruling"),
    (1, 1, 4): ("Eating", "Dying", "Sleeping", "Ruling", "Walking", "Ruling", "Eating", "Sleeping", "Walking", "Dying"),
    (1, 2, 0): ("Walking", "Eating", "Dying", "Sleeping", "Ruling", "Eating", "Sleeping", "Walking", "Dying", "Ruling"),
    (1, 2, 1): ("Dying", "Sleeping", "Ruling", "Walking", "Eating", "Ruling", "Eating", "Sleeping", "Walking", "Dying"),
    (1, 2, 2): ("Ruling", "Walking", "Eating", "Dying", "Sleeping", "Dying", "Ruling", "Eating", "Sleeping", "Walking"),
    (1, 2, 3): ("Eating", "Dying", "Sleeping", "Ruling", "Walking", "Walking", "Dying", "Ruling", "Eating", "Sleeping"),
    (1, 2, 4): ("Sleeping", "Ruling", "Walking", "Eating", "Dying", "Sleeping", "Walking", "Dying", "Ruling", "Eating"),
    (1, 3, 0): ("Dying", "Sleeping", "Ruling", "Walking", "Eating", "Sleeping", "Walking", "Dying", "Ruling", "Eating"),
    (1, 3, 1): ("Ruling", "Walking", "Eating", "Dying", "Sleeping", "Eating", "Sleeping", "Walking", "Dying", "Ruling"),
    (1, 3, 2): ("Eating", "Dying", "Sleeping", "Ruling", "Walking", "Ruling", "Eating", "Sleeping", "Walking", "Dying"),
    (1, 3, 3): ("Sleeping", "Ruling", "Walking", "Eating", "Dying", "Dying", "Ruling", "Eating", "Sleeping", "Walking"),
    (1, 3, 4): ("Walking", "Eating", "Dying", "Sleeping", "Ruling", "Walking", "Dying", "Ruling", "Eating", "Sleeping"),
    (1, 4, 0): ("Ruling", "Walking", "Eating", "Dying", "Sleeping", "Walking", "Dying", "Ruling", "Eating", "Sleeping"),
    (1, 4, 1): ("Eating", "Dying", "Sleeping", "Ruling", "Walking", "Sleeping", "Walking", "Dying", "Ruling", "Eating"),
    (1, 4, 2): ("Sleeping", "Ruling", "Walking", "Eating", "Dying", "Eating", "Sleeping", "Walking", "Dying", "Ruling"),
    (1, 4, 3): ("Walking", "Eating", "Dying", "Sleeping", "Ruling", "Ruling", "Eating", "Sleeping", "Walking", "Dying"),
    (1, 4, 4): ("Dying", "Sleeping", "Ruling", "Walking", "Eating", "Dying", "Ruling", "Eating", "Sleeping", "Walking"),
    (1, 5, 0): ("Eating", "Dying", "Sleeping", "Ruling", "Walking", "Ruling", "Eating", "Sleeping", "Walking", "Dying"),
    (1, 5, 1): ("Sleeping", "Ruling", "Walking", "Eating", "Dying", "Dying", "Ruling", "Eating", "Sleeping", "Walking"),
    (1, 5, 2): ("Walking", "Eating", "Dying", "Sleeping", "Ruling", "Walking", "Dying", "Ruling", "Eating", "Sleeping"),
    (1, 5, 3): ("Dying", "Sleeping", "Ruling", "Walking", "Eating", "Sleeping", "Walking", "Dying", "Ruling", "Eating"),
    (1, 5, 4): ("Ruling", "Walking", "Eating", "Dying", "Sleeping", "Eating", "Sleeping", "Walking", "Dying", "Ruling"),
    (1, 6, 0): ("Sleeping", "Ruling", "Walking", "Eating", "Dying", "Dying", "Ruling", "Eating", "Sleeping", "Walking"),
    (1, 6, 1): ("Walking", "Eating", "Dying", "Sleeping", "Ruling", "Walking", "Dying", "Ruling", "Eating", "Sleeping"),
    (1, 6, 2): ("Dying", "Sleeping", "Ruling", "Walking", "Eating", "Sleeping", "Walking", "Dying", "Ruling", "Eating"),
    (1, 6, 3): ("Ruling", "Walking", "Eating", "Dying", "Sleeping", "Eating", "Sleeping", "Walking", "Dying", "Ruling"),
    (1, 6, 4): ("Eating", "Dying", "Sleeping", "Ruling", "Walking", "Ruling", "Eating", "Sleeping", "Walking", "Dying"),
}
assert len(_MAJOR_ACTIVITIES) == 70


def _as_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def sunday_index(local_dt: datetime) -> int:
    local = local_dt
    if local.tzinfo is not None:
        local = local.replace(tzinfo=None)
    return (local.weekday() + 1) % 7


def paksha_index(paksha: str) -> int:
    pak = paksha.strip().title()
    if pak == "Shukla":
        return 0
    if pak == "Krishna":
        return 1
    raise ValueError(f"unsupported paksha: {paksha}")


def birth_bird_from_nakshatra(*, nakshatra_index: int, paksha: str) -> dict[str, Any]:
    """Permanent birth bird from Moon nakshatra (1..27) + birth paksha (PyJHora)."""
    idx0 = (int(nakshatra_index) - 1) % 27
    pk = paksha_index(paksha)
    bird = _BIRTH_BIRD_BY_NAK[idx0][pk]
    return {
        "bird": bird,
        "bird_index": BIRDS.index(bird) + 1,
        "element": BIRD_ELEMENT[bird],
        "nakshatra_index": idx0 + 1,
        "nakshatra": NAKSHATRAS_VEDASTRO[idx0],
        "paksha": "Shukla" if pk == 0 else "Krishna",
        "basis": "pyjhora_pancha_pakshi_stars_birds_paksha",
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


def activity_class(activity: str) -> str:
    if activity in {"Ruling", "Eating"}:
        return "favorable"
    if activity in {"Sleeping", "Dying"}:
        return "avoid"
    return "mixed"


def lookup_major_activity(*, paksha: str, weekday_sunday_index: int, bird: str, yama_index: int) -> str:
    pk = paksha_index(paksha)
    bi = BIRDS.index(bird)
    seq = _MAJOR_ACTIVITIES[(pk, weekday_sunday_index % 7, bi)]
    return seq[yama_index - 1]


def evaluate_panchapakshi(
    *,
    moon_lon_sidereal: float,
    paksha: str,
    sunrise: datetime,
    sunset: datetime,
    next_sunrise: datetime,
    when_utc: datetime,
) -> dict[str, Any]:
    """Birth bird + yama clock + major activity schedule for both pakshas."""
    bird_info = birth_bird_from_moon_longitude(
        moon_lon_sidereal=moon_lon_sidereal, paksha=paksha
    )
    clock = build_yama_clock(
        sunrise=sunrise,
        sunset=sunset,
        next_sunrise=next_sunrise,
        when_utc=when_utc,
    )
    pak = bird_info["paksha"]
    wd = clock["weekday_sunday_index"]
    bird = bird_info["bird"]
    active = clock["active"]

    schedule: list[dict[str, Any]] = []
    for row in clock["yamas"]:
        yi = int(row["yama_index"])
        act = lookup_major_activity(
            paksha=pak, weekday_sunday_index=wd, bird=bird, yama_index=yi
        )
        schedule.append(
            {
                **row,
                "activity": act,
                "activity_class": activity_class(act),
                "rank": ACTIVITY_RANK[act],
            }
        )

    current = None
    if active is not None:
        yi = int(active["yama_index"])
        act = lookup_major_activity(
            paksha=pak, weekday_sunday_index=wd, bird=bird, yama_index=yi
        )
        current = {
            "yama_index": yi,
            "phase": active["phase"],
            "activity": act,
            "activity_class": activity_class(act),
            "rank": ACTIVITY_RANK[act],
            "start_utc": active["start_utc"],
            "end_utc": active["end_utc"],
        }

    return {
        "variant": PANCHAPAKSHI_VARIANT,
        "birth_bird": bird_info,
        "paksha": pak,
        "weekday": clock["weekday"],
        "yama_clock": {
            "active": clock["active"],
            "yama_count": len(clock["yamas"]),
        },
        "current": current,
        "schedule": schedule,
        "summary": {
            "bird": bird,
            "element": bird_info["element"],
            "paksha": pak,
            "weekday": clock["weekday"],
            "yama_index": (current or {}).get("yama_index"),
            "activity": (current or {}).get("activity"),
            "activity_class": (current or {}).get("activity_class"),
            "schedule_count": len(schedule),
            "dark_half_activity_deferred": False,
        },
        "deferred": [
            "Sub-yama (upa-pakshi) nested activities and duration weights",
            "Padu/Bharana companion birds",
            "Competitive bird-vs-bird verdicts",
            "Separate natal-bird + query-time schedule split",
        ],
        "notes": [
            "Candidate majors derived from PyJHora V4.8.7 pancha_pakshi_db.csv.",
            "Birth bird uses PyJHora pancha_pakshi_stars_birds_paksha (5/6/5/5/6).",
            "Yamas are equal fifths of local day and night (sunrise/sunset based).",
            "Bird is derived from the evaluated Moon nakshatra+paksha (same instant).",
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
    "lookup_major_activity",
]

"""Yogini dasha — Candidate thin slice (TEC-031)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from bhava360.kernel.derived import NAKSHATRA_SPAN, nakshatra_from_longitude, normalize_longitude
from bhava360.kernel.errors import KernelError, KernelErrorCode
from bhava360.kernel.models import NAKSHATRAS_VEDASTRO, PlanetName
from bhava360.timing.vimshottari import MEAN_YEAR_DAYS, years_to_timedelta

YOGINI_VARIANT = "yogini_nak_plus_3_mod8_candidate_v1"
TOTAL_YEARS = 36

# Fixed order: Mangala … Sankata (1–8 years).
YOGINI_ORDER: tuple[str, ...] = (
    "Mangala",
    "Pingala",
    "Dhanya",
    "Bhramari",
    "Bhadrika",
    "Ulka",
    "Siddha",
    "Sankata",
)

YOGINI_YEARS: dict[str, int] = {
    "Mangala": 1,
    "Pingala": 2,
    "Dhanya": 3,
    "Bhramari": 4,
    "Bhadrika": 5,
    "Ulka": 6,
    "Siddha": 7,
    "Sankata": 8,
}

YOGINI_LORD: dict[str, PlanetName] = {
    "Mangala": PlanetName.MOON,
    "Pingala": PlanetName.SUN,
    "Dhanya": PlanetName.JUPITER,
    "Bhramari": PlanetName.MARS,
    "Bhadrika": PlanetName.MERCURY,
    "Ulka": PlanetName.SATURN,
    "Siddha": PlanetName.VENUS,
    "Sankata": PlanetName.RAHU,
}


@dataclass(slots=True)
class YoginiBalance:
    moon_longitude_sidereal_deg: float
    nakshatra: str
    nakshatra_index: int  # 0-based
    nakshatra_number: int  # 1-based Ashwini=1
    pada: int
    yogini: str
    lord: PlanetName
    elapsed_fraction: float
    remaining_fraction: float
    full_years: int
    balance_years: float
    balance_days: float
    start_rule: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "moon_longitude_sidereal_deg": self.moon_longitude_sidereal_deg,
            "nakshatra": self.nakshatra,
            "nakshatra_index": self.nakshatra_index,
            "nakshatra_number": self.nakshatra_number,
            "pada": self.pada,
            "yogini": self.yogini,
            "lord": self.lord.value,
            "elapsed_fraction": self.elapsed_fraction,
            "remaining_fraction": self.remaining_fraction,
            "full_years": self.full_years,
            "balance_years": self.balance_years,
            "balance_days": self.balance_days,
            "start_rule": self.start_rule,
        }


def yogini_from_nakshatra_number(nakshatra_number: int) -> str:
    """
    Candidate start rule: ((nakshatra_number + 3) % 8); 0 → Sankata.

    Ashwini=1 … Revati=27. Matches common North-Indian formula and
    Saravali nakshatra groupings for the eight Yoginis.
    """
    if not 1 <= nakshatra_number <= 27:
        raise KernelError(
            KernelErrorCode.UNSUPPORTED_CONFIG,
            "nakshatra_number must be 1–27",
            {"nakshatra_number": nakshatra_number},
        )
    rem = (nakshatra_number + 3) % 8
    idx = 7 if rem == 0 else rem - 1
    return YOGINI_ORDER[idx]


def yogini_sequence_from(start: str) -> list[str]:
    if start not in YOGINI_ORDER:
        raise KernelError(
            KernelErrorCode.UNSUPPORTED_CONFIG,
            f"unknown Yogini: {start}",
        )
    i = YOGINI_ORDER.index(start)
    return list(YOGINI_ORDER[i:] + YOGINI_ORDER[:i])


def yogini_balance(moon_longitude_sidereal_deg: float) -> YoginiBalance:
    lon = normalize_longitude(moon_longitude_sidereal_deg)
    name, pada, _label = nakshatra_from_longitude(lon)
    idx = NAKSHATRAS_VEDASTRO.index(name)
    number = idx + 1
    within = lon % NAKSHATRA_SPAN
    elapsed = within / NAKSHATRA_SPAN
    remaining = 1.0 - elapsed
    yogini = yogini_from_nakshatra_number(number)
    full = YOGINI_YEARS[yogini]
    balance_years = remaining * full
    return YoginiBalance(
        moon_longitude_sidereal_deg=lon,
        nakshatra=name,
        nakshatra_index=idx,
        nakshatra_number=number,
        pada=pada,
        yogini=yogini,
        lord=YOGINI_LORD[yogini],
        elapsed_fraction=elapsed,
        remaining_fraction=remaining,
        full_years=full,
        balance_years=balance_years,
        balance_days=balance_years * MEAN_YEAR_DAYS,
        start_rule=YOGINI_VARIANT,
    )


def build_yogini_maha_timeline(
    birth_utc: datetime,
    moon_longitude_sidereal_deg: float,
    *,
    years_ahead: float = 72.0,
) -> tuple[YoginiBalance, list[dict[str, Any]]]:
    """Build Maha Yogini periods from birth for ``years_ahead`` (default 2 cycles)."""
    if years_ahead <= 0:
        raise KernelError(
            KernelErrorCode.UNSUPPORTED_CONFIG,
            "years_ahead must be > 0",
        )
    balance = yogini_balance(moon_longitude_sidereal_deg)
    order = yogini_sequence_from(balance.yogini)
    periods: list[dict[str, Any]] = []
    cursor = birth_utc
    end_limit = birth_utc + years_to_timedelta(years_ahead)
    seq = 0
    first = True

    while cursor < end_limit - timedelta(seconds=0.5):
        for yogini in order:
            if first:
                years = balance.balance_years
                first = False
            else:
                years = float(YOGINI_YEARS[yogini])
            end = cursor + years_to_timedelta(years)
            if end > end_limit and seq > 0:
                end = end_limit
                years = (end - cursor).total_seconds() / (86400.0 * MEAN_YEAR_DAYS)
            periods.append(
                {
                    "system": "yogini",
                    "level": "maha",
                    "yogini": yogini,
                    "lord": YOGINI_LORD[yogini].value,
                    "start_utc": cursor.isoformat(),
                    "end_utc": end.isoformat(),
                    "duration_days": years * MEAN_YEAR_DAYS,
                    "duration_years": years,
                    "sequence_index": seq,
                }
            )
            cursor = end
            seq += 1
            if cursor >= end_limit - timedelta(seconds=0.5):
                break
        else:
            continue
        break

    return balance, periods


def expand_yogini_antardasha(maha: dict[str, Any]) -> list[dict[str, Any]]:
    """Antar periods proportional within one Maha (start from Maha Yogini)."""
    parent_years = float(maha["duration_years"])
    start = datetime.fromisoformat(str(maha["start_utc"]).replace("Z", "+00:00"))
    if start.tzinfo is not None:
        start = start.replace(tzinfo=None)
    order = yogini_sequence_from(str(maha["yogini"]))
    cursor = start
    out: list[dict[str, Any]] = []
    for i, yogini in enumerate(order):
        years = parent_years * YOGINI_YEARS[yogini] / TOTAL_YEARS
        end = cursor + years_to_timedelta(years)
        out.append(
            {
                "system": "yogini",
                "level": "antar",
                "yogini": yogini,
                "lord": YOGINI_LORD[yogini].value,
                "start_utc": cursor.isoformat(),
                "end_utc": end.isoformat(),
                "duration_days": years * MEAN_YEAR_DAYS,
                "duration_years": years,
                "parent_yogini": maha["yogini"],
                "sequence_index": i,
            }
        )
        cursor = end
    return out


def build_yogini_tree(
    birth_utc: datetime,
    moon_longitude_sidereal_deg: float,
    *,
    years_ahead: float = 72.0,
    include_antar: bool = True,
) -> dict[str, Any]:
    balance, maha = build_yogini_maha_timeline(
        birth_utc,
        moon_longitude_sidereal_deg,
        years_ahead=years_ahead,
    )
    antar: list[dict[str, Any]] = []
    if include_antar and maha:
        # Expand first few maha periods for console/tests (cap to keep payload small).
        for period in maha[:8]:
            antar.extend(expand_yogini_antardasha(period))
    return {
        "variant": YOGINI_VARIANT,
        "total_cycle_years": TOTAL_YEARS,
        "balance": balance.to_dict(),
        "levels": {
            "maha": maha,
            "antar": antar,
        },
        "yogini_table": [
            {
                "yogini": y,
                "years": YOGINI_YEARS[y],
                "lord": YOGINI_LORD[y].value,
            }
            for y in YOGINI_ORDER
        ],
    }


__all__ = [
    "TOTAL_YEARS",
    "YOGINI_LORD",
    "YOGINI_ORDER",
    "YOGINI_VARIANT",
    "YOGINI_YEARS",
    "YoginiBalance",
    "build_yogini_maha_timeline",
    "build_yogini_tree",
    "expand_yogini_antardasha",
    "yogini_balance",
    "yogini_from_nakshatra_number",
    "yogini_sequence_from",
]

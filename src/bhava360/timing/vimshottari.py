from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from bhava360.kernel.derived import NAKSHATRA_SPAN, nakshatra_from_longitude, normalize_longitude
from bhava360.kernel.errors import KernelError, KernelErrorCode
from bhava360.kernel.models import NAKSHATRAS_VEDASTRO, PlanetName

# Vimshottari order starting from Aswini (index 0) lord Ketu.
VIMSHOTTARI_ORDER: tuple[PlanetName, ...] = (
    PlanetName.KETU,
    PlanetName.VENUS,
    PlanetName.SUN,
    PlanetName.MOON,
    PlanetName.MARS,
    PlanetName.RAHU,
    PlanetName.JUPITER,
    PlanetName.SATURN,
    PlanetName.MERCURY,
)

VIMSHOTTARI_YEARS: dict[PlanetName, int] = {
    PlanetName.KETU: 7,
    PlanetName.VENUS: 20,
    PlanetName.SUN: 6,
    PlanetName.MOON: 10,
    PlanetName.MARS: 7,
    PlanetName.RAHU: 18,
    PlanetName.JUPITER: 16,
    PlanetName.SATURN: 19,
    PlanetName.MERCURY: 17,
}

TOTAL_YEARS = 120
MEAN_YEAR_DAYS = 365.2425


class DashaLevel(str, Enum):
    MAHA = "maha"
    ANTAR = "antar"
    PRATYANTAR = "pratyantar"
    SOOKSHMA = "sookshma"
    PRANA = "prana"


LEVEL_ORDER: tuple[DashaLevel, ...] = (
    DashaLevel.MAHA,
    DashaLevel.ANTAR,
    DashaLevel.PRATYANTAR,
    DashaLevel.SOOKSHMA,
    DashaLevel.PRANA,
)


@dataclass(slots=True)
class DashaPeriod:
    system: str
    level: DashaLevel
    lord: PlanetName
    start_utc: datetime
    end_utc: datetime
    duration_days: float
    parent_lords: tuple[PlanetName, ...]
    sequence_index: int

    def to_dict(self) -> dict:
        return {
            "system": self.system,
            "level": self.level.value,
            "lord": self.lord.value,
            "start_utc": self.start_utc.isoformat(),
            "end_utc": self.end_utc.isoformat(),
            "duration_days": self.duration_days,
            "parent_lords": [p.value for p in self.parent_lords],
            "sequence_index": self.sequence_index,
        }


@dataclass(slots=True)
class VimshottariBalance:
    moon_longitude_sidereal_deg: float
    nakshatra: str
    nakshatra_index: int
    pada: int
    lord: PlanetName
    elapsed_fraction: float
    remaining_fraction: float
    full_years: int
    balance_years: float
    balance_days: float

    def to_dict(self) -> dict:
        return {
            "moon_longitude_sidereal_deg": self.moon_longitude_sidereal_deg,
            "nakshatra": self.nakshatra,
            "nakshatra_index": self.nakshatra_index,
            "pada": self.pada,
            "lord": self.lord.value,
            "elapsed_fraction": self.elapsed_fraction,
            "remaining_fraction": self.remaining_fraction,
            "full_years": self.full_years,
            "balance_years": self.balance_years,
            "balance_days": self.balance_days,
        }


def years_to_timedelta(years: float) -> timedelta:
    return timedelta(days=years * MEAN_YEAR_DAYS)


def nakshatra_lord(nakshatra_index: int) -> PlanetName:
    return VIMSHOTTARI_ORDER[nakshatra_index % 9]


def lord_sequence_from(start: PlanetName) -> list[PlanetName]:
    if start not in VIMSHOTTARI_ORDER:
        raise KernelError(
            KernelErrorCode.UNSUPPORTED_PLANET,
            f"{start} is not a Vimshottari lord",
        )
    i = VIMSHOTTARI_ORDER.index(start)
    return list(VIMSHOTTARI_ORDER[i:] + VIMSHOTTARI_ORDER[:i])


def vimshottari_balance(moon_longitude_sidereal_deg: float) -> VimshottariBalance:
    lon = normalize_longitude(moon_longitude_sidereal_deg)
    name, pada, _label = nakshatra_from_longitude(lon)
    idx = NAKSHATRAS_VEDASTRO.index(name)
    within = lon % NAKSHATRA_SPAN
    elapsed = within / NAKSHATRA_SPAN
    remaining = 1.0 - elapsed
    lord = nakshatra_lord(idx)
    full = VIMSHOTTARI_YEARS[lord]
    balance_years = remaining * full
    return VimshottariBalance(
        moon_longitude_sidereal_deg=lon,
        nakshatra=name,
        nakshatra_index=idx,
        pada=pada,
        lord=lord,
        elapsed_fraction=elapsed,
        remaining_fraction=remaining,
        full_years=full,
        balance_years=balance_years,
        balance_days=balance_years * MEAN_YEAR_DAYS,
    )


def _child_duration_years(parent_years: float, child_lord: PlanetName) -> float:
    return parent_years * VIMSHOTTARI_YEARS[child_lord] / TOTAL_YEARS


def iter_level_periods(
    *,
    level: DashaLevel,
    parent_years: float,
    start_utc: datetime,
    start_lord: PlanetName,
    parent_lords: tuple[PlanetName, ...],
    first_period_years: float | None = None,
) -> list[DashaPeriod]:
    """Generate one dasha level. Optionally shorten the first period (birth balance)."""
    lords = lord_sequence_from(start_lord)
    periods: list[DashaPeriod] = []
    cursor = start_utc
    for i, lord in enumerate(lords):
        years = _child_duration_years(parent_years, lord)
        if i == 0 and first_period_years is not None:
            years = first_period_years
        delta = years_to_timedelta(years)
        end = cursor + delta
        periods.append(
            DashaPeriod(
                system="vimshottari",
                level=level,
                lord=lord,
                start_utc=cursor,
                end_utc=end,
                duration_days=years * MEAN_YEAR_DAYS,
                parent_lords=parent_lords,
                sequence_index=i,
            )
        )
        cursor = end
    return periods


def build_maha_timeline(
    birth_utc: datetime,
    moon_longitude_sidereal_deg: float,
    *,
    years_ahead: float = 120.0,
) -> tuple[VimshottariBalance, list[DashaPeriod]]:
    if years_ahead <= 0:
        raise KernelError(
            KernelErrorCode.UNSUPPORTED_CONFIG,
            "years_ahead must be > 0",
        )
    balance = vimshottari_balance(moon_longitude_sidereal_deg)
    order = lord_sequence_from(balance.lord)
    periods: list[DashaPeriod] = []
    cursor = birth_utc
    end_limit = birth_utc + years_to_timedelta(years_ahead)
    seq = 0
    first_period = True

    while cursor < end_limit - timedelta(seconds=0.5):
        for lord in order:
            if first_period:
                years = balance.balance_years
                first_period = False
            else:
                years = float(VIMSHOTTARI_YEARS[lord])
            end = cursor + years_to_timedelta(years)
            if end > end_limit and seq > 0:
                # Truncate final partial period to the requested horizon.
                end = end_limit
                years = (end - cursor).total_seconds() / (86400.0 * MEAN_YEAR_DAYS)
            periods.append(
                DashaPeriod(
                    system="vimshottari",
                    level=DashaLevel.MAHA,
                    lord=lord,
                    start_utc=cursor,
                    end_utc=end,
                    duration_days=years * MEAN_YEAR_DAYS,
                    parent_lords=tuple(),
                    sequence_index=seq,
                )
            )
            cursor = end
            seq += 1
            if cursor >= end_limit - timedelta(seconds=0.5):
                break
        else:
            continue
        break

    return balance, periods


def expand_subperiods(
    parent: DashaPeriod,
    child_level: DashaLevel,
) -> list[DashaPeriod]:
    """Expand one parent period into 9 child periods starting from parent lord."""
    parent_years = parent.duration_days / MEAN_YEAR_DAYS
    return iter_level_periods(
        level=child_level,
        parent_years=parent_years,
        start_utc=parent.start_utc,
        start_lord=parent.lord,
        parent_lords=parent.parent_lords + (parent.lord,),
        first_period_years=None,
    )


def build_vimshottari_tree(
    birth_utc: datetime,
    moon_longitude_sidereal_deg: float,
    *,
    depth: DashaLevel = DashaLevel.ANTAR,
    years_ahead: float = 120.0,
) -> dict:
    """Build Vimshottari periods down to requested depth."""
    if depth not in LEVEL_ORDER:
        raise KernelError(
            KernelErrorCode.UNSUPPORTED_CONFIG,
            f"unsupported dasha depth {depth}",
        )
    balance, mahas = build_maha_timeline(
        birth_utc,
        moon_longitude_sidereal_deg,
        years_ahead=years_ahead,
    )
    assert_timeline_continuous(mahas)
    depth_idx = LEVEL_ORDER.index(depth)
    levels: dict[str, list[DashaPeriod]] = {DashaLevel.MAHA.value: mahas}

    current = mahas
    for level in LEVEL_ORDER[1 : depth_idx + 1]:
        children: list[DashaPeriod] = []
        for parent in current:
            kids = expand_subperiods(parent, level)
            assert_timeline_continuous(kids)
            # Child span must match parent span.
            if kids:
                gap_start = abs((kids[0].start_utc - parent.start_utc).total_seconds())
                gap_end = abs((kids[-1].end_utc - parent.end_utc).total_seconds())
                if gap_start > 1.0 or gap_end > 1.0:
                    raise KernelError(
                        KernelErrorCode.CALCULATION_FAILED,
                        "subperiod span does not match parent",
                        {
                            "parent": parent.to_dict(),
                            "first_child": kids[0].to_dict(),
                            "last_child": kids[-1].to_dict(),
                        },
                    )
            children.extend(kids)
        levels[level.value] = children
        current = children

    return {
        "system": "vimshottari",
        "depth": depth.value,
        "mean_year_days": MEAN_YEAR_DAYS,
        "years_ahead": years_ahead,
        "balance": balance.to_dict(),
        "levels": {k: [p.to_dict() for p in v] for k, v in levels.items()},
    }


def assert_timeline_continuous(periods: list[DashaPeriod], *, tol_seconds: float = 1.0) -> None:
    """Raise if periods have gaps/overlaps beyond tolerance."""
    if not periods:
        raise KernelError(KernelErrorCode.CALCULATION_FAILED, "empty dasha timeline")
    for i in range(len(periods) - 1):
        a = periods[i]
        b = periods[i + 1]
        gap = (b.start_utc - a.end_utc).total_seconds()
        if abs(gap) > tol_seconds:
            raise KernelError(
                KernelErrorCode.CALCULATION_FAILED,
                "dasha timeline gap/overlap detected",
                {
                    "index": i,
                    "gap_seconds": gap,
                    "left": a.to_dict(),
                    "right": b.to_dict(),
                },
            )
    for p in periods:
        if p.end_utc < p.start_utc:
            raise KernelError(
                KernelErrorCode.CALCULATION_FAILED,
                "dasha period ends before it starts",
                p.to_dict(),
            )

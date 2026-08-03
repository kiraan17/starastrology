from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from bhava360.kernel.models import ChartConfig, PlanetName, SubjectInput
from bhava360.kernel.provider import SwissEphemerisProvider
from bhava360.kernel.timeutil import resolve_subject_time


@dataclass(slots=True)
class CalculationSnapshot:
    snapshot_id: str
    created_at_utc: str
    input: dict[str, Any]
    config: dict[str, Any]
    resolved_time: dict[str, Any]
    library: dict[str, str]
    ayanamsa_degrees: float
    planets: list[dict[str, Any]]
    houses: dict[str, Any] | None = None
    day_window: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "created_at_utc": self.created_at_utc,
            "input": self.input,
            "config": self.config,
            "resolved_time": self.resolved_time,
            "library": self.library,
            "ayanamsa_degrees": self.ayanamsa_degrees,
            "planets": self.planets,
            "houses": self.houses,
            "day_window": self.day_window,
        }


def build_planet_snapshot(
    subject: SubjectInput,
    config: ChartConfig | None = None,
    planets: list[PlanetName] | None = None,
    *,
    include_houses: bool = True,
    include_day_window: bool = True,
) -> CalculationSnapshot:
    """Build an immutable calculation snapshot for planetary longitudes (+ optional houses/day)."""
    cfg = config or ChartConfig()
    provider = SwissEphemerisProvider(cfg)
    resolved = resolve_subject_time(subject)
    positions = provider.all_planet_positions(subject, planets)

    houses = None
    day_window = None
    has_coords = subject.latitude is not None and subject.longitude is not None
    if include_houses and has_coords:
        houses = provider.houses(subject).to_dict()
        # Attach whole-sign and configured system planet house numbers for convenience.
        planet_houses = {
            p.planet.value: provider.planet_house(subject, p.planet) for p in positions
        }
        houses["planet_houses"] = planet_houses
    if include_day_window and has_coords:
        day_window = provider.day_window(subject).to_dict()

    return CalculationSnapshot(
        snapshot_id=str(uuid4()),
        created_at_utc=datetime.now(timezone.utc).isoformat(),
        input={
            "input_kind": subject.input_kind,
            "local_datetime": subject.local_datetime.isoformat(sep=" "),
            "timezone_offset_minutes": subject.timezone_offset_minutes,
            "timezone_id": subject.timezone_id,
            "dst_ambiguity_policy": subject.dst_ambiguity_policy,
            "latitude": subject.latitude,
            "longitude": subject.longitude,
            "location_label": subject.location_label,
            "birth_time_uncertainty_minutes": subject.birth_time_uncertainty_minutes,
        },
        config=cfg.stamp(),
        resolved_time=resolved.to_dict(),
        library=provider.library_stamp(),
        ayanamsa_degrees=provider.ayanamsa_degrees(resolved.julian_day_ut),
        planets=[p.to_dict() for p in positions],
        houses=houses,
        day_window=day_window,
    )

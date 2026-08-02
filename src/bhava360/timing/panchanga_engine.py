"""Panchanga engine (P16a thin slice)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from bhava360.chart.builder import ChartConstructor
from bhava360.kernel.models import ChartConfig, PlanetName, SubjectInput
from bhava360.kernel.provider import SwissEphemerisProvider
from bhava360.kernel.timeutil import resolve_subject_time
from bhava360.timing.panchanga import compute_panchanga_core

ENGINE_NAME = "Panchanga"
ENGINE_VERSION = "0.1.0-thin-slice"
TECHNIQUE_IDS = ("TEC-070",)


def _parse_sunrise_local(iso_local: str) -> datetime:
    # DayWindow stores e.g. "1990-08-15 05:52:01.123456+05:30"
    return datetime.fromisoformat(iso_local)


def run_panchanga_engine(
    subject: SubjectInput,
    *,
    config: ChartConfig | None = None,
    chart: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compute five-limb panchanga at subject instant with sunrise-based Vara."""
    cfg = config or ChartConfig()
    provider = SwissEphemerisProvider(cfg)
    resolved = resolve_subject_time(subject)

    built = chart
    if built is None and subject.latitude is not None and subject.longitude is not None:
        built = ChartConstructor(cfg).build(subject, include_vimshottari=False).to_dict()

    if built and built.get("day_window"):
        day_window = built["day_window"]
        sun = next(p for p in built["planets"] if p["planet"] == "Sun")
        moon = next(p for p in built["planets"] if p["planet"] == "Moon")
        sun_lon = float(sun["longitude_sidereal_deg"])
        moon_lon = float(moon["longitude_sidereal_deg"])
    else:
        day_window = provider.day_window(subject).to_dict()
        sun_lon = provider.planet_position(subject, PlanetName.SUN).longitude_sidereal_deg
        moon_lon = provider.planet_position(subject, PlanetName.MOON).longitude_sidereal_deg

    sunrise_local = _parse_sunrise_local(day_window["sunrise_local"])
    core = compute_panchanga_core(
        sun_lon_sidereal=sun_lon,
        moon_lon_sidereal=moon_lon,
        sunrise_local=sunrise_local,
    )

    return {
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "technique_ids": list(TECHNIQUE_IDS),
        "resolved_time": resolved.to_dict(),
        "day_window": day_window,
        "library": provider.library_stamp(),
        "panchanga": core,
        "notes": core["notes"]
        + [
            "Evaluated at subject local civil time; Vara keyed to that date's sunrise.",
            "TEC-071..076 (Rahu Kala, Hora, etc.) deferred.",
        ],
    }

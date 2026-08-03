"""Panchanga engine (P16a + P16b + P16c)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import swisseph as swe

from bhava360.chart.builder import ChartConstructor
from bhava360.kernel.errors import KernelError, KernelErrorCode
from bhava360.kernel.models import ChartConfig, PlanetName, SubjectInput
from bhava360.kernel.provider import SwissEphemerisProvider
from bhava360.kernel.timeutil import julian_day_to_utc, resolve_subject_time, subject_tzinfo
from bhava360.timing.bala import compute_tara_chandra_pack
from bhava360.timing.muhurta import compute_muhurta_pack
from bhava360.timing.panchanga import compute_panchanga_core

ENGINE_NAME = "Panchanga"
ENGINE_VERSION = "0.3.0-bala"
TECHNIQUE_IDS = ("TEC-070", "TEC-071", "TEC-072", "TEC-073")


def _parse_local(iso_local: str) -> datetime:
    return datetime.fromisoformat(iso_local)


def _next_sunrise_utc(
    *,
    after_jd: float,
    latitude: float,
    longitude: float,
) -> datetime:
    geopos = (longitude, latitude, 0.0)
    try:
        rc, vals = swe.rise_trans(
            after_jd,
            swe.SUN,
            swe.CALC_RISE | swe.BIT_DISC_CENTER,
            geopos,
        )
    except Exception as exc:  # noqa: BLE001
        raise KernelError(
            KernelErrorCode.CALCULATION_FAILED,
            "failed to compute next sunrise for muhurta night windows",
            {"error": str(exc)},
        ) from exc
    if rc < 0:
        raise KernelError(
            KernelErrorCode.CALCULATION_FAILED,
            "next sunrise not available",
            {"rise_rc": rc},
        )
    return julian_day_to_utc(float(vals[0]))


def run_panchanga_engine(
    subject: SubjectInput,
    *,
    config: ChartConfig | None = None,
    chart: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Panchanga limbs, muhurta windows, and Tara/Chandra Bala."""
    cfg = config or ChartConfig()
    provider = SwissEphemerisProvider(cfg)
    resolved = resolve_subject_time(subject)

    built = chart
    if built is None and subject.latitude is not None and subject.longitude is not None:
        built = ChartConstructor(cfg).build(subject, include_vimshottari=False).to_dict()

    if built and built.get("day_window"):
        day_window = built["day_window"]
        planets = {p["planet"]: p for p in built["planets"]}
        sun_lon = float(planets["Sun"]["longitude_sidereal_deg"])
        moon_lon = float(planets["Moon"]["longitude_sidereal_deg"])
        lagna_lon = float(
            built["angles"]["whole_sign"]["ascendant"]["longitude_sidereal_deg"]
        )
        planet_lons = {
            name: float(row["longitude_sidereal_deg"])
            for name, row in planets.items()
            if name in {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"}
        }
    else:
        day_window = provider.day_window(subject).to_dict()
        sun_lon = provider.planet_position(subject, PlanetName.SUN).longitude_sidereal_deg
        moon_lon = provider.planet_position(subject, PlanetName.MOON).longitude_sidereal_deg
        houses = provider.houses(subject)
        lagna_lon = houses.ascendant.longitude_sidereal_deg
        planet_lons = {
            p.value: provider.planet_position(subject, p).longitude_sidereal_deg
            for p in (
                PlanetName.SUN,
                PlanetName.MOON,
                PlanetName.MARS,
                PlanetName.MERCURY,
                PlanetName.JUPITER,
                PlanetName.VENUS,
                PlanetName.SATURN,
            )
        }

    sunrise_local = _parse_local(day_window["sunrise_local"])
    sunset_local = _parse_local(day_window["sunset_local"])
    core = compute_panchanga_core(
        sun_lon_sidereal=sun_lon,
        moon_lon_sidereal=moon_lon,
        sunrise_local=sunrise_local,
    )

    bala = compute_tara_chandra_pack(
        moon_longitude_sidereal=moon_lon,
        lagna_longitude_sidereal=lagna_lon,
        planet_longitudes=planet_lons,
    )

    lat = float(subject.latitude) if subject.latitude is not None else None
    lon = float(subject.longitude) if subject.longitude is not None else None
    muhurta = None
    if lat is not None and lon is not None:
        next_rise = _next_sunrise_utc(
            after_jd=float(day_window["sunset_jd_ut"]),
            latitude=lat,
            longitude=lon,
        )
        tz = subject_tzinfo(subject)
        next_rise_local = next_rise.astimezone(tz)
        muhurta = compute_muhurta_pack(
            sunrise=sunrise_local,
            sunset=sunset_local,
            next_sunrise=next_rise_local,
            when_utc=resolved.utc_datetime,
        )

    return {
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "technique_ids": list(TECHNIQUE_IDS),
        "resolved_time": resolved.to_dict(),
        "day_window": day_window,
        "library": provider.library_stamp(),
        "panchanga": core,
        "muhurta": muhurta,
        "bala": bala,
        "notes": core["notes"]
        + (muhurta["notes"] if muhurta else [])
        + bala["notes"]
        + [
            "Evaluated at subject local civil time; Vara keyed to that date's sunrise.",
            "TEC-075..076 activity cycles partially covered elsewhere; TEC-074 in PanchakaBhadra.",
        ],
    }

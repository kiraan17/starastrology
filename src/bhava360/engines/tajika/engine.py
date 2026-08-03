"""Tajika / Varshaphala annual engine (thin slice) — Candidate."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import swisseph as swe

from bhava360.chart.builder import ChartConstructor
from bhava360.engines.tajika.annual import (
    ANNUAL_VARIANT,
    completed_years_at,
    compute_muntha,
    find_solar_return_jd,
    resolve_annual_location,
)
from bhava360.engines.tajika.aspects_tajika import ASPECT_VARIANT, compute_tajika_aspects
from bhava360.engines.tajika.sahams import SAHAM_VARIANT, compute_sahams, is_day_chart
from bhava360.engines.tajika.tithi_pravesh import (
    TITHI_PRAVESH_VARIANT,
    find_tithi_pravesh_jd,
    natal_tithi_from_longitudes,
)
from bhava360.kernel.derived import house_index_for_longitude, whole_sign_cusp_longitudes
from bhava360.kernel.errors import KernelError, KernelErrorCode
from bhava360.kernel.models import ChartConfig, SubjectInput
from bhava360.kernel.provider import SwissEphemerisProvider
from bhava360.kernel.timeutil import julian_day_to_utc, require_coordinates, resolve_subject_time, subject_tzinfo

ENGINE_NAME = "TajikaAnnual"
ENGINE_VERSION = "0.3.0-sahams-aspects"
TECHNIQUE_IDS = ("TEC-077", "TEC-078", "TEC-079")
STATUS = "Candidate"


def _anniversary_local(birth_local: datetime, target_year: int) -> datetime:
    try:
        return birth_local.replace(year=int(target_year))
    except ValueError:
        # Feb 29 → Mar 1 in non-leap years
        return birth_local.replace(year=int(target_year), month=3, day=1)


def _subject_at_instant(
    natal: SubjectInput,
    *,
    utc_dt: datetime,
    latitude: float,
    longitude: float,
    location_label: str | None,
) -> SubjectInput:
    tz = subject_tzinfo(natal)
    local = utc_dt.astimezone(tz).replace(tzinfo=None)
    has_iana = bool(natal.timezone_id and natal.timezone_id.strip())
    return SubjectInput(
        local_datetime=local,
        timezone_offset_minutes=None if has_iana else natal.timezone_offset_minutes,
        timezone_id=natal.timezone_id if has_iana else None,
        dst_ambiguity_policy=natal.dst_ambiguity_policy,
        latitude=latitude,
        longitude=longitude,
        location_label=location_label,
        birth_time_uncertainty_minutes=None,
        input_kind="annual",
    )


def run_tajika_annual_engine(
    subject: SubjectInput,
    *,
    config: ChartConfig | None = None,
    chart: dict[str, Any] | None = None,
    target_year: int | None = None,
    location_rule: str = "birth_place",
    residence_lat: float | None = None,
    residence_lon: float | None = None,
    event_lat: float | None = None,
    event_lon: float | None = None,
) -> dict[str, Any]:
    """
    Varsha Pravesh + Muntha + Tithi Pravesh + Candidate Sahams/aspects.

    Year-lord candidate = Muntha-sign lord (full Varshesh deferred).
    Full Tajika yogas beyond Ithasala-candidate flag deferred.
    """
    cfg = config or ChartConfig()
    provider = SwissEphemerisProvider(cfg)
    natal_lat, natal_lon = require_coordinates(subject)
    natal_resolved = resolve_subject_time(subject)
    birth_utc = natal_resolved.utc_datetime

    year = int(target_year) if target_year is not None else int(birth_utc.year) + 1
    if year < int(birth_utc.year):
        raise KernelError(
            KernelErrorCode.UNSUPPORTED_CONFIG,
            "target_year must be >= birth year",
            {"target_year": year, "birth_year": birth_utc.year},
        )

    built = chart or ChartConstructor(cfg).build(subject, include_vimshottari=False).to_dict()
    planets = {p["planet"]: p for p in built["planets"]}
    natal_sun = float(planets["Sun"]["longitude_sidereal_deg"])
    natal_moon = float(planets["Moon"]["longitude_sidereal_deg"])
    lagna_sign = built["angles"]["whole_sign"]["ascendant"]["sign"]
    natal_tithi = natal_tithi_from_longitudes(sun_lon=natal_sun, moon_lon=natal_moon)
    natal_elong = float(natal_tithi["elongation_deg"])

    approx_local = _anniversary_local(subject.local_datetime, year)
    approx_subject = SubjectInput(
        local_datetime=approx_local,
        timezone_offset_minutes=subject.timezone_offset_minutes,
        timezone_id=subject.timezone_id,
        dst_ambiguity_policy=subject.dst_ambiguity_policy,
        latitude=subject.latitude,
        longitude=subject.longitude,
        location_label=subject.location_label,
        input_kind="annual_approx",
    )
    approx_jd = resolve_subject_time(approx_subject).julian_day_ut

    sidereal_flags = provider._flags(sidereal=True)
    return_jd = find_solar_return_jd(
        natal_sun_longitude_sidereal=natal_sun,
        search_start_jd=approx_jd - 5.0,
        sidereal_flags=sidereal_flags,
        search_days=20.0,
    )
    return_utc = julian_day_to_utc(return_jd)

    loc = resolve_annual_location(
        location_rule=location_rule,
        natal_lat=natal_lat,
        natal_lon=natal_lon,
        residence_lat=residence_lat,
        residence_lon=residence_lon,
        event_lat=event_lat,
        event_lon=event_lon,
    )
    annual_subject = _subject_at_instant(
        subject,
        utc_dt=return_utc,
        latitude=float(loc["latitude"]),
        longitude=float(loc["longitude"]),
        location_label=f"annual:{loc['location_rule']}",
    )
    varsha = ChartConstructor(cfg).build(annual_subject, include_vimshottari=False).to_dict()
    varsha_planets = {p["planet"]: p for p in varsha["planets"]}
    varsha_sun = float(varsha_planets["Sun"]["longitude_sidereal_deg"])
    varsha_lagna = float(varsha["angles"]["whole_sign"]["ascendant"]["longitude_sidereal_deg"])

    # Varsha of calendar target_year uses completed years = target_year - birth_year.
    completed = year - int(birth_utc.year)
    # Cross-check against solar-return instant (should usually match).
    completed_at_return = completed_years_at(birth_utc, return_utc)
    if abs(completed_at_return - completed) > 1:
        completed = completed_at_return

    muntha = compute_muntha(natal_lagna_sign=lagna_sign, completed_years=completed)
    muntha_mid = muntha["sign_index"] * 30.0 + 15.0
    cusps = whole_sign_cusp_longitudes(varsha_lagna)
    muntha_house = house_index_for_longitude(muntha_mid, cusps)

    sun_err = abs(((varsha_sun - natal_sun + 180.0) % 360.0) - 180.0)

    tp_jd = find_tithi_pravesh_jd(
        natal_elongation_deg=natal_elong,
        center_jd_ut=return_jd,
        sidereal_flags=sidereal_flags,
    )
    tp_utc = julian_day_to_utc(tp_jd)
    tp_subject = _subject_at_instant(
        subject,
        utc_dt=tp_utc,
        latitude=float(loc["latitude"]),
        longitude=float(loc["longitude"]),
        location_label=f"tithi_pravesh:{loc['location_rule']}",
    )
    tp_chart = ChartConstructor(cfg).build(tp_subject, include_vimshottari=False).to_dict()
    tp_planets = {p["planet"]: p for p in tp_chart["planets"]}
    tp_sun = float(tp_planets["Sun"]["longitude_sidereal_deg"])
    tp_moon = float(tp_planets["Moon"]["longitude_sidereal_deg"])
    tp_tithi = natal_tithi_from_longitudes(sun_lon=tp_sun, moon_lon=tp_moon)
    tp_elong_err = abs(
        ((float(tp_tithi["elongation_deg"]) - natal_elong + 180.0) % 360.0) - 180.0
    )
    tp_lagna = float(tp_chart["angles"]["whole_sign"]["ascendant"]["longitude_sidereal_deg"])

    day_window = varsha.get("day_window") or {}
    local_iso = annual_subject.local_datetime.isoformat(sep=" ")
    chart_is_day = False
    if day_window.get("sunrise_local") and day_window.get("sunset_local"):
        chart_is_day = is_day_chart(
            local_iso=local_iso,
            sunrise_local=str(day_window["sunrise_local"]),
            sunset_local=str(day_window["sunset_local"]),
        )

    sahams = compute_sahams(
        ascendant_longitude=varsha_lagna,
        planets=varsha["planets"],
        is_day=chart_is_day,
    )
    aspects = compute_tajika_aspects(varsha["planets"])

    return {
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "technique_ids": list(TECHNIQUE_IDS),
        "status": STATUS,
        "school": "tajika",
        "config": {
            "annual.location_rule": loc["location_rule"],
            "target_year": year,
            "variant": ANNUAL_VARIANT,
            "tithi_pravesh.variant": TITHI_PRAVESH_VARIANT,
            "sahams.variant": SAHAM_VARIANT,
            "aspects.variant": ASPECT_VARIANT,
        },
        "target_year": year,
        "completed_years": completed,
        "solar_return": {
            "jd_ut": return_jd,
            "datetime_utc": return_utc.isoformat().replace("+00:00", "Z"),
            "datetime_local": annual_subject.local_datetime.isoformat(sep=" "),
            "sun_longitude_error_deg": round(sun_err, 6),
            "natal_sun_longitude_sidereal_deg": natal_sun,
            "varsha_sun_longitude_sidereal_deg": varsha_sun,
        },
        "annual_location": {
            **loc,
            "variant_id": "VARIANT-002",
        },
        "varsha_chart": {
            "lagna_sign": varsha["angles"]["whole_sign"]["ascendant"]["sign"],
            "lagna_longitude_sidereal_deg": varsha_lagna,
            "is_day": chart_is_day,
            "planets": [
                {
                    "planet": p["planet"],
                    "longitude_sidereal_deg": p["longitude_sidereal_deg"],
                    "speed_longitude": p.get("speed_longitude"),
                    "sign": p["sign"],
                    "rasi_house": (p.get("houses") or {}).get("rasi_house"),
                }
                for p in varsha["planets"]
            ],
        },
        "muntha": {
            **muntha,
            "house_from_varsha_lagna": muntha_house,
            "year_lord_candidate": muntha["lord"],
        },
        "natal_tithi": natal_tithi,
        "tithi_pravesh": {
            "variant": TITHI_PRAVESH_VARIANT,
            "jd_ut": tp_jd,
            "datetime_utc": tp_utc.isoformat().replace("+00:00", "Z"),
            "datetime_local": tp_subject.local_datetime.isoformat(sep=" "),
            "days_from_solar_return": round(tp_jd - return_jd, 6),
            "elongation_error_deg": round(tp_elong_err, 6),
            "tithi": tp_tithi,
            "chart": {
                "lagna_sign": tp_chart["angles"]["whole_sign"]["ascendant"]["sign"],
                "lagna_longitude_sidereal_deg": tp_lagna,
                "planets": [
                    {
                        "planet": p["planet"],
                        "longitude_sidereal_deg": p["longitude_sidereal_deg"],
                        "sign": p["sign"],
                        "rasi_house": (p.get("houses") or {}).get("rasi_house"),
                    }
                    for p in tp_chart["planets"]
                ],
            },
            "notes": [
                "Annual Tithi Pravesh = natal Moon−Sun elongation return nearest solar return (±20d).",
                "Uses same annual.location_rule as Varsha chart.",
            ],
        },
        "sahams": sahams,
        "tajika_aspects": aspects,
        "deferred": [
            "Full Varshesh / multi-factor year-lord rules",
            "Full Saham catalog beyond Punya/Vidya/Yasya/Mitra/Rajya",
            "Full Ithasala/Isarpha/Nakta/Kamboola yoga suite",
            "Month/day charts",
            "Alternate Tithi Pravesh centering rules (lunar-month-only variants)",
        ],
        "provenance": {
            "status": STATUS,
            "stamp": ANNUAL_VARIANT,
            "sources": ["TEC-077", "TEC-078", "TEC-079"],
            "notes": [
                "Sidereal solar return via Swiss Ephemeris scan + bisection.",
                "Muntha advances natal Lagna by completed years (mod 12).",
                "Muntha lord is year-lord candidate only.",
                "annual.location_rule stamped per VARIANT-002 (default birth_place).",
                "Tithi Pravesh Candidate: elongation return nearest solar return.",
                "Sahams/aspects Candidate defaults pending SRC-012 edition citation.",
            ],
        },
        "ephemeris": {
            "mode": cfg.ephemeris_mode.value,
            "ayanamsa": cfg.ayanamsa.value,
            "pyswisseph_version": getattr(swe, "version", "unknown"),
        },
    }


__all__ = [
    "ENGINE_NAME",
    "ENGINE_VERSION",
    "STATUS",
    "TECHNIQUE_IDS",
    "run_tajika_annual_engine",
]

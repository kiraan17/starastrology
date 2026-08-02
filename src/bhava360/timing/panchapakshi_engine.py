"""Panchapakshi engine (P26b) — TEC-075 thin slice."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import swisseph as swe

from bhava360.chart.builder import ChartConstructor
from bhava360.kernel.errors import KernelError, KernelErrorCode
from bhava360.kernel.models import ChartConfig, SubjectInput
from bhava360.kernel.timeutil import julian_day_to_utc, resolve_subject_time, subject_tzinfo
from bhava360.timing.panchanga_engine import run_panchanga_engine
from bhava360.timing.panchapakshi import PANCHAPAKSHI_VARIANT, evaluate_panchapakshi

ENGINE_NAME = "Panchapakshi"
ENGINE_VERSION = "0.1.0-yama-bright"
TECHNIQUE_IDS = ("TEC-075",)
STATUS = "Candidate"


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
            "failed to compute next sunrise for panchapakshi night yamas",
            {"error": str(exc)},
        ) from exc
    if rc < 0:
        raise KernelError(
            KernelErrorCode.CALCULATION_FAILED,
            "next sunrise not available",
            {"rise_rc": rc},
        )
    return julian_day_to_utc(float(vals[0]))


def run_panchapakshi_engine(
    subject: SubjectInput,
    *,
    config: ChartConfig | None = None,
    chart: dict[str, Any] | None = None,
    panchanga: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Birth bird + equal yama clock; Shukla activity mirrors when applicable.

    Krishna-paksha activity lookup remains Source Needed / deferred.
    """
    cfg = config or ChartConfig()
    built = chart
    if built is None:
        built = ChartConstructor(cfg).build(
            subject, include_vimshottari=False, include_relationships=False
        ).to_dict()

    pan = panchanga or run_panchanga_engine(subject, config=cfg, chart=built)
    core = pan.get("panchanga") or {}
    tithi = core.get("tithi") or {}
    day_window = pan.get("day_window") or built.get("day_window") or {}
    if not day_window:
        raise KernelError(
            KernelErrorCode.UNSUPPORTED_CONFIG,
            "day_window required for panchapakshi yamas",
        )

    resolved = resolve_subject_time(subject)
    tz = subject_tzinfo(subject)
    sunrise = _parse_local(day_window["sunrise_local"]).replace(tzinfo=tz)
    sunset = _parse_local(day_window["sunset_local"]).replace(tzinfo=tz)
    lat = float(subject.latitude) if subject.latitude is not None else None
    lon = float(subject.longitude) if subject.longitude is not None else None
    if lat is None or lon is None:
        raise KernelError(
            KernelErrorCode.UNSUPPORTED_CONFIG,
            "latitude/longitude required for panchapakshi",
        )
    next_rise = _next_sunrise_utc(
        after_jd=float(day_window["sunset_jd_ut"]),
        latitude=lat,
        longitude=lon,
    )
    next_rise_local = next_rise.astimezone(tz)

    pack = evaluate_panchapakshi(
        moon_lon_sidereal=float(core["moon_longitude_sidereal_deg"]),
        paksha=str(tithi.get("paksha") or "Shukla"),
        sunrise=sunrise,
        sunset=sunset,
        next_sunrise=next_rise_local,
        when_utc=resolved.utc_datetime,
    )

    return {
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "technique_ids": list(TECHNIQUE_IDS),
        "status": STATUS,
        "school": "panchanga",
        "config": {
            "panchapakshi.variant": PANCHAPAKSHI_VARIANT,
        },
        "panchapakshi": pack,
        "panchanga_ref": {
            "engine": pan.get("engine"),
            "engine_version": pan.get("engine_version"),
            "tithi": tithi.get("label"),
            "paksha": tithi.get("paksha"),
            "nakshatra": (core.get("nakshatra") or {}).get("label"),
            "vara": (core.get("vara") or {}).get("name"),
        },
        "deferred": pack.get("deferred") or [],
        "provenance": {
            "status": STATUS,
            "stamp": PANCHAPAKSHI_VARIANT,
            "sources": ["TEC-075", "VedAstro Part 2/5 (Candidate)"],
            "notes": [
                "Birth bird from Moon nakshatra + paksha.",
                "Shukla mirror activities Auto-Tested thin; Krishna deferred.",
            ],
        },
        "safety": {
            "note": "Timing classification only — not predictive advice.",
        },
    }


__all__ = [
    "ENGINE_NAME",
    "ENGINE_VERSION",
    "STATUS",
    "TECHNIQUE_IDS",
    "run_panchapakshi_engine",
]

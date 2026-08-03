"""Prashna engine scaffold (P19b) — calc sphutas; manual inputs stay manual."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from bhava360.chart.builder import ChartConstructor
from bhava360.chart.dignity import sign_lord
from bhava360.engines.jaimini.calculations import compute_arudha_pada
from bhava360.engines.prashna.manual import normalize_ashtamangala_counts
from bhava360.engines.prashna.sphutas import SPHUTA_VARIANT, compute_prashna_sphutas
from bhava360.kernel.models import ChartConfig, SubjectInput
from bhava360.timing.muhurta import compute_day_eighth_windows, sunday_index

ENGINE_NAME = "Prashna"
ENGINE_VERSION = "0.1.0-sphuta-scaffold"
TECHNIQUE_IDS = ("TEC-086", "TEC-088")
STATUS = "Candidate"


def _parse_local_iso(iso: str) -> datetime:
    # day_window stores "YYYY-MM-DD HH:MM:SS" style
    return datetime.fromisoformat(iso)


def _gulika_longitude_from_chart(
    subject: SubjectInput,
    chart: dict[str, Any],
    config: ChartConfig,
) -> float | None:
    """Candidate: Gulika sphuta = whole-sign Lagna at start of daytime Gulika kala."""
    day_window = chart.get("day_window")
    if not day_window:
        return None
    sunrise = _parse_local_iso(day_window["sunrise_local"])
    sunset = _parse_local_iso(day_window["sunset_local"])
    wd = sunday_index(sunrise)
    eighths = compute_day_eighth_windows(
        sunrise=sunrise,
        sunset=sunset,
        weekday_sunday_index=wd,
    )
    # Windows were built from local sunrise/sunset; treat segment start as local civil time.
    start_raw = str(eighths["gulika"]["start_utc"]).replace("Z", "")
    gulika_local = datetime.fromisoformat(start_raw)
    if gulika_local.tzinfo is not None:
        gulika_local = gulika_local.replace(tzinfo=None)
    has_iana = bool(subject.timezone_id and subject.timezone_id.strip())
    gulika_subject = SubjectInput(
        local_datetime=gulika_local,
        timezone_offset_minutes=None if has_iana else subject.timezone_offset_minutes,
        timezone_id=subject.timezone_id if has_iana else None,
        dst_ambiguity_policy=subject.dst_ambiguity_policy,
        latitude=subject.latitude,
        longitude=subject.longitude,
        location_label=subject.location_label,
        input_kind="prashna_gulika",
    )
    gulika_chart = ChartConstructor(config).build(
        gulika_subject,
        include_vimshottari=False,
        include_relationships=False,
    ).to_dict()
    return float(
        gulika_chart["angles"]["whole_sign"]["ascendant"]["longitude_sidereal_deg"]
    )


def run_prashna_engine(
    subject: SubjectInput,
    *,
    config: ChartConfig | None = None,
    chart: dict[str, Any] | None = None,
    ashtamangala_counts: Any = None,
    question_text: str | None = None,
) -> dict[str, Any]:
    """
    Prashna thin scaffold at the query instant.

    Calculable: chart facts, Trisphuta, Gulika/Chatusphuta (Candidate), Arudha Lagna.
    Manual: Ashtamangala counts passthrough only — never invented.
    """
    cfg = config or ChartConfig()
    # Prefer explicit prashna input_kind without mutating caller's subject unexpectedly:
    query_subject = SubjectInput(
        local_datetime=subject.local_datetime,
        timezone_offset_minutes=subject.timezone_offset_minutes,
        timezone_id=subject.timezone_id,
        dst_ambiguity_policy=subject.dst_ambiguity_policy,
        latitude=subject.latitude,
        longitude=subject.longitude,
        location_label=subject.location_label,
        birth_time_uncertainty_minutes=subject.birth_time_uncertainty_minutes,
        input_kind="prashna",
    )
    built = chart or ChartConstructor(cfg).build(
        query_subject,
        include_vimshottari=False,
    ).to_dict()

    planets = {p["planet"]: p for p in built["planets"]}
    lagna_lon = float(built["angles"]["whole_sign"]["ascendant"]["longitude_sidereal_deg"])
    lagna_sign = built["angles"]["whole_sign"]["ascendant"]["sign"]
    sun_lon = float(planets["Sun"]["longitude_sidereal_deg"])
    moon_lon = float(planets["Moon"]["longitude_sidereal_deg"])

    gulika_lon = _gulika_longitude_from_chart(query_subject, built, cfg)
    sphutas = compute_prashna_sphutas(
        lagna_longitude=lagna_lon,
        moon_longitude=moon_lon,
        sun_longitude=sun_lon,
        gulika_longitude=gulika_lon,
    )

    planet_signs = {p["planet"]: p["sign"] for p in built["planets"]}
    lord = sign_lord(lagna_sign)
    arudha = None
    if lord is not None and lord.value in planet_signs:
        arudha = compute_arudha_pada(lagna_sign, planet_signs[lord.value])

    manual = normalize_ashtamangala_counts(ashtamangala_counts)

    return {
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "technique_ids": list(TECHNIQUE_IDS),
        "status": STATUS,
        "school": "prashna",
        "config": {
            "sphuta.variant": SPHUTA_VARIANT,
            "input_kind": "prashna",
        },
        "question": {
            "text": question_text,
            "query_local": query_subject.local_datetime.isoformat(sep=" "),
            "timezone_id": query_subject.timezone_id,
            "timezone_offset_minutes": query_subject.timezone_offset_minutes,
        },
        "prashna_lagna": {
            "longitude_sidereal_deg": lagna_lon,
            "sign": lagna_sign,
            "nakshatra_label": built["angles"]["whole_sign"]["ascendant"].get(
                "nakshatra_label"
            ),
        },
        "sphutas": sphutas,
        "arudha_lagna": arudha,
        "manual_inputs": {
            "ashtamangala": manual,
        },
        "chart_ref": {
            "chart_id": built.get("chart_id"),
            "planet_count": len(built.get("planets") or []),
        },
        "deferred": [
            "Full Prashna Marga interpretive rule pack (SRC-011)",
            "Panchasphuta / Prana / other advanced sphutas",
            "Tamil Aroodha Prashna (TEC-087)",
            "Ashtamangala verdict tables (TEC-088) — counts remain manual",
            "KP Horary number path",
        ],
        "provenance": {
            "status": STATUS,
            "stamp": "prashna_thin_candidate_v1",
            "sources": ["TEC-086", "TEC-088"],
            "notes": [
                "Query-time chart; input_kind stamped prashna.",
                "Trisphuta = Lagna+Moon+Sun; Gulika = Lagna at Gulika-kala start (Candidate).",
                "Ashtamangala counts are operator-supplied only — never fabricated.",
            ],
        },
    }


__all__ = [
    "ENGINE_NAME",
    "ENGINE_VERSION",
    "STATUS",
    "TECHNIQUE_IDS",
    "run_prashna_engine",
]

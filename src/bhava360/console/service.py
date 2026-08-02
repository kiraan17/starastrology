from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from bhava360.chart.builder import ChartConstructor
from bhava360.engines.ashtakavarga import run_ashtakavarga_engine
from bhava360.engines.kp import run_kp_engine
from bhava360.engines.parashara import run_parashara_engine
from bhava360.kernel.models import AyanamsaMode, ChartConfig, HouseSystem, SubjectInput


def parse_subject(
    *,
    date_str: str,
    time_str: str,
    offset_str: str,
    latitude: float,
    longitude: float,
    location_label: str,
    uncertainty_minutes: float | None,
) -> SubjectInput:
    local = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    sign = 1
    off = offset_str.strip()
    if off.startswith("-"):
        sign = -1
        off = off[1:]
    elif off.startswith("+"):
        off = off[1:]
    hh, mm = off.split(":")
    offset_minutes = sign * (int(hh) * 60 + int(mm))
    return SubjectInput(
        local_datetime=local,
        timezone_offset_minutes=offset_minutes,
        latitude=latitude,
        longitude=longitude,
        location_label=location_label or None,
        birth_time_uncertainty_minutes=uncertainty_minutes,
    )


def build_config(ayanamsa: str, house_system: str) -> ChartConfig:
    return ChartConfig(
        ayanamsa=AyanamsaMode(ayanamsa),
        house_system=HouseSystem(house_system),
    )


def run_verification(
    subject: SubjectInput,
    *,
    ayanamsa: str = "lahiri",
    house_system: str = "whole_sign",
    engines: list[str] | None = None,
) -> dict[str, Any]:
    """Run selected verification engines and return a structured report."""
    selected = engines or ["chart", "parashara", "ashtakavarga"]
    config = build_config(ayanamsa, house_system)
    report: dict[str, Any] = {
        "report_type": "bhava360_internal_verification",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input": {
            "local_datetime": subject.local_datetime.isoformat(sep=" "),
            "timezone_offset_minutes": subject.timezone_offset_minutes,
            "latitude": subject.latitude,
            "longitude": subject.longitude,
            "location_label": subject.location_label,
            "birth_time_uncertainty_minutes": subject.birth_time_uncertainty_minutes,
            "ayanamsa": ayanamsa,
            "house_system": house_system,
            "engines": selected,
        },
        "sections": {},
        "errors": [],
    }

    chart = None
    if "chart" in selected or "parashara" in selected or "ashtakavarga" in selected:
        try:
            chart = ChartConstructor(config).build(subject).to_dict()
            report["sections"]["chart"] = chart
        except Exception as exc:  # noqa: BLE001
            report["errors"].append({"section": "chart", "error": str(exc)})

    if "parashara" in selected:
        try:
            if chart is None:
                raise RuntimeError("chart required for Parashara")
            report["sections"]["parashara"] = run_parashara_engine(chart)
        except Exception as exc:  # noqa: BLE001
            report["errors"].append({"section": "parashara", "error": str(exc)})

    if "ashtakavarga" in selected:
        try:
            report["sections"]["ashtakavarga"] = run_ashtakavarga_engine(
                subject, config=config, chart=chart
            )
        except Exception as exc:  # noqa: BLE001
            report["errors"].append({"section": "ashtakavarga", "error": str(exc)})

    if "kp" in selected:
        try:
            # KP path enforces its own ayanamsa/house system.
            report["sections"]["kp"] = run_kp_engine(subject)
        except Exception as exc:  # noqa: BLE001
            report["errors"].append({"section": "kp", "error": str(exc)})

    report["summary"] = _summarize(report)
    return report


def _summarize(report: dict[str, Any]) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "sections_present": list(report["sections"].keys()),
        "error_count": len(report["errors"]),
    }
    chart = report["sections"].get("chart")
    if chart:
        summary["calc_library_version"] = chart.get("config", {}).get("calc_library_version")
        summary["ayanamsa_degrees"] = chart.get("ayanamsa_degrees")
        if chart.get("dashas"):
            summary["vimshottari_balance_lord"] = chart["dashas"]["balance"]["lord"]
            summary["vimshottari_balance_years"] = chart["dashas"]["balance"]["balance_years"]
        if chart.get("relationships"):
            summary["relationship_edge_count"] = len(chart["relationships"].get("edges", []))
            summary["graha_aspect_count"] = len(chart["relationships"].get("graha_aspects", []))
            summary["conjunction_count"] = len(chart["relationships"].get("conjunctions", []))
        planets = []
        for p in chart.get("planets", []):
            planets.append(
                {
                    "planet": p["planet"],
                    "longitude": p["longitude_sidereal_deg"],
                    "sign": p["sign"],
                    "nakshatra": p["nakshatra_label"],
                    "rasi_house": p.get("houses", {}).get("rasi_house"),
                    "dignity": p.get("dignity", {}).get("primary"),
                }
            )
        summary["planets"] = planets
        asc = chart.get("angles", {}).get("whole_sign", {}).get("ascendant", {})
        summary["ascendant"] = {
            "longitude": asc.get("longitude_sidereal_deg"),
            "sign": asc.get("sign"),
            "nakshatra": asc.get("nakshatra_label"),
        }

    para = report["sections"].get("parashara")
    if para:
        summary["parashara_rules"] = [
            {
                "rule_id": r["rule_id"],
                "name": r["name"],
                "outcome": r["outcome"],
                "version": r["version"],
                "activation_active": r.get("activation", {}).get("active"),
                "source_ids": r.get("source_ids"),
            }
            for r in para.get("results", [])
        ]

    av = report["sections"].get("ashtakavarga")
    if av:
        summary["sav_total_bindus"] = av.get("sarvashtakavarga", {}).get("total_bindus")

    kp = report["sections"].get("kp")
    if kp:
        summary["kp_config_isolation"] = kp.get("config_isolation", {}).get("outcome")
        sun = kp.get("planet_lord_chains", {}).get("Sun", {})
        summary["kp_sun_lords"] = {
            "star": sun.get("star_lord"),
            "sub": sun.get("sub_lord"),
            "sub_sub": sun.get("sub_sub_lord"),
        }
    return summary

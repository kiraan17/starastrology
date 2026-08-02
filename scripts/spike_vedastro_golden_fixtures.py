#!/usr/bin/env python3
"""SPIKE-01: Fetch VedAstro reference fixtures for golden-chart comparison.

These outputs are COMPARATORS only — not Bhava360 production truth.
Requires network access to https://api.vedastro.org
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API_ROOT = "https://api.vedastro.org/api/Calculate"
OUT_DIR = Path(__file__).resolve().parents[1] / "tests" / "golden" / "vedastro-spike"
PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

# Five fixed charts for cross-location / timezone smoke comparison.
CHARTS = [
    {
        "id": "chennai_1990_0815_1200",
        "label": "Chennai sample",
        "location": "Chennai",
        "time": "12:00/15/08/1990/+05:30",
    },
    {
        "id": "singapore_2024_0424_0000",
        "label": "Singapore sample",
        "location": "Singapore",
        "time": "00:00/24/04/2024/+08:00",
    },
    {
        "id": "london_2000_0101_1200",
        "label": "London sample",
        "location": "London",
        "time": "12:00/01/01/2000/+00:00",
    },
    {
        "id": "newyork_1976_0704_1430",
        "label": "New York sample",
        "location": "New York",
        "time": "14:30/04/07/1976/-04:00",
    },
    {
        "id": "mumbai_1950_0126_1010",
        "label": "Mumbai sample",
        "location": "Mumbai",
        "time": "10:10/26/01/1950/+05:30",
    },
]


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "Bhava360-SPIKE-01/0.1"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.loads(resp.read().decode("utf-8"))


def calc_url(calculator: str, location: str, time: str, **params: str) -> str:
    parts = [API_ROOT, calculator]
    for key, value in params.items():
        parts.extend([key, urllib.parse.quote(value, safe="")])
    # VedAstro accepts encoded spaces in Location; keep time slashes intact.
    parts.extend(["Location", urllib.parse.quote(location), "Time", time])
    return "/".join(parts)


def fetch_chart(chart: dict) -> dict:
    location = chart["location"]
    time = chart["time"]
    planets = {}
    errors = []
    for planet in PLANETS:
        entry = {"planet": planet}
        for calculator, key in [
            ("PlanetNirayanaLongitude", "PlanetName"),
            ("PlanetRasiD1Sign", "PlanetName"),
            ("PlanetConstellation", "PlanetName"),
        ]:
            url = calc_url(calculator, location, time, **{key: planet})
            try:
                payload = get_json(url)
                entry[calculator] = payload
                if payload.get("Status") != "Pass":
                    errors.append(f"{planet}:{calculator}:{payload.get('Payload')}")
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
                entry[calculator] = {"Status": "Error", "error": str(exc)}
                errors.append(f"{planet}:{calculator}:{exc}")
        planets[planet] = entry

    sun_all = None
    try:
        sun_all = get_json(
            calc_url("AllPlanetData", location, time, PlanetName="Sun")
        )
        if sun_all.get("Status") != "Pass":
            errors.append(f"Sun:AllPlanetData:{sun_all.get('Payload')}")
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
        sun_all = {"Status": "Error", "error": str(exc)}
        errors.append(f"Sun:AllPlanetData:{exc}")

    return {
        "chart": chart,
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        "api_root": API_ROOT,
        "note": "VedAstro comparator fixture only. Not Bhava360 production truth.",
        "planets": planets,
        "sun_all_planet_data": sun_all,
        "errors": errors,
    }


def summarize(result: dict) -> dict:
    rows = []
    for planet, data in result["planets"].items():
        lon = (
            data.get("PlanetNirayanaLongitude", {})
            .get("Payload", {})
            .get("PlanetNirayanaLongitude", {})
        )
        sign = (
            data.get("PlanetRasiD1Sign", {})
            .get("Payload", {})
            .get("PlanetRasiD1Sign", {})
        )
        nak = (
            data.get("PlanetConstellation", {})
            .get("Payload", {})
            .get("PlanetConstellation")
        )
        rows.append(
            {
                "planet": planet,
                "nirayana_total_degrees": lon.get("TotalDegrees"),
                "nirayana_dms": lon.get("DegreeMinuteSecond"),
                "rasi": sign.get("Name") if isinstance(sign, dict) else None,
                "nakshatra": nak,
            }
        )
    return {
        "chart_id": result["chart"]["id"],
        "location": result["chart"]["location"],
        "time": result["chart"]["time"],
        "error_count": len(result["errors"]),
        "planets": rows,
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summaries = []
    failed = 0
    for chart in CHARTS:
        print(f"Fetching {chart['id']} ...", flush=True)
        result = fetch_chart(chart)
        out = OUT_DIR / f"{chart['id']}.json"
        out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
        summary = summarize(result)
        summaries.append(summary)
        if result["errors"]:
            failed += 1
            print(f"  WARN {len(result['errors'])} errors")
        else:
            print("  OK")
    manifest = {
        "spike": "SPIKE-01",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "VedAstro golden comparator fixtures for future Bhava360 kernel tests",
        "not_production_truth": True,
        "charts": summaries,
    }
    (OUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    )
    (OUT_DIR / "README.md").write_text(
        "\n".join(
            [
                "# VedAstro SPIKE-01 fixtures",
                "",
                "Generated by `scripts/spike_vedastro_golden_fixtures.py`.",
                "",
                "These JSON files are **reference comparators** from the public VedAstro API.",
                "They are not Bhava360 approved golden truth until quality review.",
                "",
                "Do not use VedAstro AI/chat text as an astrology source.",
                "",
            ]
        )
    )
    print(json.dumps({"charts": len(CHARTS), "charts_with_errors": failed}, indent=2))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

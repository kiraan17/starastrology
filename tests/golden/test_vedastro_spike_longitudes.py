from __future__ import annotations

import json
from pathlib import Path

import pytest

from bhava360.kernel.models import ChartConfig, PlanetName, SubjectInput
from bhava360.kernel.provider import SwissEphemerisProvider
from bhava360.kernel.timeutil import parse_vedastro_time_token

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "tests" / "golden" / "vedastro-spike" / "manifest.json"

# Tight tolerance: SPIKE-01 matched Moshier/Lahiri/mean-node within ~0.0002°.
LONGITUDE_TOLERANCE_DEG = 0.01


def _charts():
    data = json.loads(MANIFEST.read_text())
    return data["charts"]


@pytest.mark.parametrize("chart", _charts(), ids=lambda c: c["chart_id"])
def test_sidereal_longitudes_match_vedastro_spike(chart):
    local, offset = parse_vedastro_time_token(chart["time"])
    subject = SubjectInput(
        local_datetime=local,
        timezone_offset_minutes=offset,
        location_label=chart["location"],
    )
    provider = SwissEphemerisProvider(ChartConfig())

    for expected in chart["planets"]:
        planet = PlanetName(expected["planet"])
        actual = provider.planet_position(subject, planet)
        exp_lon = float(expected["nirayana_total_degrees"])
        assert abs(actual.longitude_sidereal_deg - exp_lon) <= LONGITUDE_TOLERANCE_DEG, (
            f"{chart['chart_id']} {planet.value}: {actual.longitude_sidereal_deg} vs {exp_lon}"
        )
        assert actual.sign == expected["rasi"], planet.value
        assert actual.nakshatra_label == expected["nakshatra"], planet.value

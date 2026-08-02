from __future__ import annotations

from datetime import datetime

from bhava360.chart.builder import ChartConstructor
from bhava360.chart.vargas import VargaId
from bhava360.kernel.models import SubjectInput

CHENNAI = SubjectInput(
    local_datetime=datetime(1990, 8, 15, 12, 0),
    timezone_offset_minutes=330,
    latitude=13.0827,
    longitude=80.2707,
    location_label="Chennai",
    birth_time_uncertainty_minutes=0.5,
)


def test_chart_constructor_builds_vargas_dignity_and_house_maps():
    chart = ChartConstructor().build(CHENNAI).to_dict()
    assert chart["config"]["calc_library_version"] == "bhava360-kernel-0.3.0"
    assert "whole_sign" in chart["angles"]
    assert "bhava_chalit" in chart["angles"]
    assert len(chart["planets"]) == 9
    sun = next(p for p in chart["planets"] if p["planet"] == "Sun")
    assert "D1" in sun["vargas"]
    assert "D9" in sun["vargas"]
    assert sun["vargas"]["D1"]["sign"] == sun["sign"]
    assert "dignity" in sun
    assert "rasi_house" in sun["houses"]
    assert "bhava_chalit_house" in sun["houses"]
    assert chart["day_window"] is not None


def test_chart_constructor_can_include_gated_d150():
    chart = ChartConstructor().build(CHENNAI, include_d150=True).to_dict()
    sun = next(p for p in chart["planets"] if p["planet"] == "Sun")
    assert "D150" in sun["vargas"]
    assert sun["vargas"]["D150"]["varga"] == VargaId.D150.value

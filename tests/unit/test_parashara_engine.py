from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone

from bhava360.chart.builder import ChartConstructor
from bhava360.engines.evidence import RuleOutcome
from bhava360.engines.parashara.engine import active_lords_at, run_parashara_engine
from bhava360.engines.parashara.rules import evaluate_budha_aditya, evaluate_gajakesari
from bhava360.kernel.models import SubjectInput


def _base_chart() -> dict:
    # Minimal constructed-chart shaped fixture for rule unit tests.
    return {
        "angles": {
            "whole_sign": {
                "ascendant": {"longitude_sidereal_deg": 0.0},  # Aries Lagna
            }
        },
        "planets": [
            {"planet": "Sun", "longitude_sidereal_deg": 10.0, "sign": "Aries", "is_retrograde": False},
            {"planet": "Moon", "longitude_sidereal_deg": 40.0, "sign": "Taurus", "is_retrograde": False},
            {"planet": "Mercury", "longitude_sidereal_deg": 20.0, "sign": "Aries", "is_retrograde": False},
            {"planet": "Jupiter", "longitude_sidereal_deg": 130.0, "sign": "Leo", "is_retrograde": False},
            {"planet": "Venus", "longitude_sidereal_deg": 200.0, "sign": "Libra", "is_retrograde": False},
            {"planet": "Mars", "longitude_sidereal_deg": 250.0, "sign": "Sagittarius", "is_retrograde": False},
            {"planet": "Saturn", "longitude_sidereal_deg": 300.0, "sign": "Capricorn", "is_retrograde": False},
            {"planet": "Rahu", "longitude_sidereal_deg": 180.0, "sign": "Libra", "is_retrograde": True},
            {"planet": "Ketu", "longitude_sidereal_deg": 0.0, "sign": "Aries", "is_retrograde": True},
        ],
        "dashas": None,
        "resolved_time": {"utc_datetime": "1990-08-15T06:30:00+00:00"},
    }


def test_gajakesari_positive_mutual_kendra():
    # Moon house 2 (Taurus), Jupiter house 5 (Leo) → relative 4 = kendra
    chart = _base_chart()
    ev = evaluate_gajakesari(chart)
    assert ev.outcome == RuleOutcome.MATCHED
    assert ev.conditions[0].passed is True


def test_gajakesari_negative_not_kendra():
    chart = _base_chart()
    # Move Jupiter to Gemini (house 3) — 2nd from Moon house 2? Moon Taurus h2, Gemini h3 → relative 2
    for p in chart["planets"]:
        if p["planet"] == "Jupiter":
            p["longitude_sidereal_deg"] = 70.0
            p["sign"] = "Gemini"
    ev = evaluate_gajakesari(chart)
    assert ev.outcome == RuleOutcome.FAILED


def test_gajakesari_cancelled_when_jupiter_combust():
    chart = _base_chart()
    # Put Jupiter near Sun in Aries while keeping Moon in Cancer (kendra from Aries? 
    # Asc 0 Aries: Sun/Jup Aries h1, Moon Cancer h4 → kendra, Jupiter combust)
    for p in chart["planets"]:
        if p["planet"] == "Jupiter":
            p["longitude_sidereal_deg"] = 12.0
            p["sign"] = "Aries"
        if p["planet"] == "Moon":
            p["longitude_sidereal_deg"] = 100.0
            p["sign"] = "Cancer"
    ev = evaluate_gajakesari(chart)
    assert ev.outcome == RuleOutcome.CANCELLED


def test_budha_aditya_positive_and_negative():
    chart = _base_chart()
    pos = evaluate_budha_aditya(chart)
    assert pos.outcome == RuleOutcome.MATCHED
    chart2 = deepcopy(chart)
    for p in chart2["planets"]:
        if p["planet"] == "Mercury":
            p["sign"] = "Taurus"
            p["longitude_sidereal_deg"] = 40.0
    neg = evaluate_budha_aditya(chart2)
    assert neg.outcome == RuleOutcome.FAILED


def test_parashara_engine_on_live_chart_activation_fields():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_offset_minutes=330,
        latitude=13.0827,
        longitude=80.2707,
        location_label="Chennai",
    )
    chart = ChartConstructor().build(subject, dasha_years_ahead=30.0).to_dict()
    out = run_parashara_engine(chart)
    assert out["engine"] == "Parashara"
    assert out["rule_count"] == 2
    by_id = {r["rule_id"]: r for r in out["results"]}
    assert "RULE-PARASHARA-001" in by_id
    assert "RULE-PARASHARA-002" in by_id
    gaja = by_id["RULE-PARASHARA-001"]
    assert "activation" in gaja
    assert "active_lords" in gaja["activation"]
    # Birth is in Moon maha for this chart; if Gajakesari matched, activation may be true.
    lords = active_lords_at(chart["dashas"], datetime.fromisoformat(chart["resolved_time"]["utc_datetime"]))
    assert lords["maha"] == "Moon"

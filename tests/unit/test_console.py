from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Allow importing console.app from repo root.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from console.app import app  # noqa: E402
from bhava360.console.service import parse_subject, run_verification  # noqa: E402


client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["public_api_ready"] is False
    assert body["license_gate"]["public_activation"] == "blocked"


def test_index_renders():
    res = client.get("/")
    assert res.status_code == 200
    assert "Internal verification console only" in res.text


def test_api_verify_chart_and_parashara():
    res = client.post(
        "/api/verify",
        json={
            "date": "1990-08-15",
            "time": "12:00",
            "offset": "+05:30",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "location_label": "Chennai",
            "ayanamsa": "lahiri",
            "house_system": "whole_sign",
            "engines": ["chart", "parashara", "ashtakavarga"],
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert "chart" in body["sections"]
    assert "parashara" in body["sections"]
    assert body["summary"]["error_count"] == 0
    assert body["summary"]["sav_total_bindus"] == 337
    assert body["summary"]["sav_sodhya_pinda"] is not None
    assert body["summary"]["sav_reduced_total"] is not None
    assert body["summary"]["prastara_sun_ok"] is True

    export = client.get("/export.json")
    assert export.status_code == 200
    assert export.json()["summary"]["sav_total_bindus"] == 337


def test_form_verify_includes_kp():
    res = client.post(
        "/verify",
        data={
            "date": "1990-08-15",
            "time": "12:00",
            "offset": "+05:30",
            "latitude": "13.0827",
            "longitude": "80.2707",
            "location_label": "Chennai",
            "uncertainty": "",
            "ayanamsa": "lahiri",
            "house_system": "whole_sign",
            "engines": ["kp"],
        },
    )
    assert res.status_code == 200
    assert "KP" in res.text
    assert "Config isolation" in res.text


def test_api_verify_jaimini():
    res = client.post(
        "/api/verify",
        json={
            "date": "1990-08-15",
            "time": "12:00",
            "offset": "+05:30",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "location_label": "Chennai",
            "ayanamsa": "lahiri",
            "house_system": "whole_sign",
            "engines": ["jaimini"],
            "jaimini_chara_scheme": "seven",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["summary"]["error_count"] == 0
    assert body["summary"]["jaimini_engine"] == "Jaimini"
    assert body["summary"]["jaimini_atmakaraka"]
    assert "Gemini" not in body["sections"]["jaimini"]["engine"]


def test_api_verify_iana_timezone():
    res = client.post(
        "/api/verify",
        json={
            "date": "1990-08-15",
            "time": "12:00",
            "timezone_id": "Asia/Kolkata",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "location_label": "Chennai",
            "engines": ["chart"],
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["summary"]["error_count"] == 0
    assert body["summary"]["timezone_source"] == "iana"
    assert body["summary"]["timezone_id"] == "Asia/Kolkata"
    assert body["summary"]["resolved_offset_minutes"] == 330


def test_api_verify_nadi_scaffold():
    res = client.post(
        "/api/verify",
        json={
            "date": "1990-08-15",
            "time": "12:00",
            "timezone_id": "Asia/Kolkata",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "location_label": "Chennai",
            "engines": ["nadi"],
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["summary"]["error_count"] == 0
    assert body["summary"]["nadi_engine"] == "NakshatraNadi"
    assert body["summary"]["nadi_corpus_status"] == "blocked"
    assert body["summary"]["nadi_chains_blocked"] is True
    assert body["summary"]["nadi_planet_in_star_count"] >= 9


def test_run_verification_service_direct():
    subject = parse_subject(
        date_str="1990-08-15",
        time_str="12:00",
        offset_str="+05:30",
        latitude=13.0827,
        longitude=80.2707,
        location_label="Chennai",
        uncertainty_minutes=None,
    )
    report = run_verification(subject, engines=["chart"])
    assert "chart" in report["sections"]
    assert report["summary"]["ascendant"]["sign"]


def test_api_verify_panchanga():
    res = client.post(
        "/api/verify",
        json={
            "date": "1990-08-15",
            "time": "12:00",
            "timezone_id": "Asia/Kolkata",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "location_label": "Chennai",
            "engines": ["panchanga"],
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["summary"]["error_count"] == 0
    assert body["summary"]["panchanga_engine"] == "Panchanga"
    assert body["summary"]["panchanga_vara"] == "Wednesday"
    assert body["summary"]["panchanga_tithi"]
    assert body["summary"]["muhurta_hora_lord"]

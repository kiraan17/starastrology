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
    assert body["freeze_candidate"]["freeze_status"] == "candidate"
    assert body["freeze_candidate"]["frozen"] is False
    assert body["blocked_reasons"]


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
    assert body["summary"]["bala_moon_tara"] == "Janma"


def test_api_verify_tajika_annual():
    res = client.post(
        "/api/verify",
        json={
            "date": "1990-08-15",
            "time": "12:00",
            "timezone_id": "Asia/Kolkata",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "location_label": "Chennai",
            "engines": ["tajika"],
            "target_year": 2020,
            "annual_location_rule": "birth_place",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["summary"]["error_count"] == 0
    assert body["summary"]["tajika_engine"] == "TajikaAnnual"
    assert body["summary"]["tajika_target_year"] == 2020
    assert body["summary"]["tajika_muntha_sign"]
    assert body["summary"]["tajika_location_rule"] == "birth_place"
    assert body["summary"]["tajika_sun_error_deg"] < 0.01
    assert body["summary"]["tajika_tithi_pravesh_label"]
    assert body["summary"]["tajika_tithi_pravesh_error_deg"] < 0.01
    assert body["summary"]["tajika_saham_count"] == 5
    assert body["summary"]["tajika_aspect_count"] >= 0


def test_api_verify_sudarshana():
    res = client.post(
        "/api/verify",
        json={
            "date": "1990-08-15",
            "time": "12:00",
            "timezone_id": "Asia/Kolkata",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "location_label": "Chennai",
            "engines": ["sudarshana"],
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["summary"]["error_count"] == 0
    assert body["summary"]["sudarshana_engine"] == "SudarshanaChakra"
    assert body["summary"]["sudarshana_lagna"]
    assert body["summary"]["sudarshana_chandra"]
    assert body["summary"]["sudarshana_surya"]
    assert body["summary"]["sudarshana_planet_count"] >= 7


def test_api_verify_bhrigu_bindu():
    res = client.post(
        "/api/verify",
        json={
            "date": "1990-08-15",
            "time": "12:00",
            "timezone_id": "Asia/Kolkata",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "location_label": "Chennai",
            "engines": ["bhrigu_bindu"],
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["summary"]["error_count"] == 0
    assert body["summary"]["bhrigu_bindu_engine"] == "BhriguBindu"
    assert body["summary"]["bhrigu_bindu_sign"]
    assert body["summary"]["bhrigu_bindu_nakshatra"]
    assert 1 <= body["summary"]["bhrigu_bindu_house"] <= 12


def test_api_verify_nakshatra_chakra():
    res = client.post(
        "/api/verify",
        json={
            "date": "1990-08-15",
            "time": "12:00",
            "timezone_id": "Asia/Kolkata",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "location_label": "Chennai",
            "engines": ["nakshatra_chakra"],
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["summary"]["error_count"] == 0
    assert body["summary"]["nakshatra_chakra_engine"] == "NakshatraChakras"
    assert body["summary"]["tara_chakra_spoke_count"] == 9
    assert body["summary"]["kota_chakra_slot_count"] == 27
    assert body["summary"]["sarvatobhadra_rim_count"] == 27
    assert body["summary"]["sarvatobhadra_vedha_status"] == "deferred"
    assert body["summary"]["tara_chakra_moon_tara"] == "Janma"


def test_api_verify_classification():
    res = client.post(
        "/api/verify",
        json={
            "date": "1990-08-15",
            "time": "12:00",
            "timezone_id": "Asia/Kolkata",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "location_label": "Chennai",
            "engines": ["classification"],
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["summary"]["error_count"] == 0
    assert body["summary"]["classification_engine"] == "Classification"
    assert body["summary"]["chandra_kriya"]
    assert body["summary"]["chandra_kriya_index"] >= 1
    assert body["summary"]["chandra_vela_index"] >= 1
    assert body["summary"]["moon_baladi_avastha"]
    assert body["summary"]["gandanta_hit_count"] >= 0


def test_api_verify_prashna_manual_passthrough():
    res = client.post(
        "/api/verify",
        json={
            "date": "1990-08-15",
            "time": "12:00",
            "timezone_id": "Asia/Kolkata",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "location_label": "Chennai",
            "engines": ["prashna"],
            "question_text": "Test question",
            "ashtamangala_counts": "2,4,6,8",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["summary"]["error_count"] == 0
    assert body["summary"]["prashna_engine"] == "Prashna"
    assert body["summary"]["prashna_lagna_sign"]
    assert body["summary"]["prashna_trisphuta_sign"]
    assert body["summary"]["prashna_chatusphuta_sign"]
    assert body["summary"]["ashtamangala_provided"] is True
    assert body["summary"]["ashtamangala_status"] == "manual_input_recorded"
    assert body["sections"]["prashna"]["manual_inputs"]["ashtamangala"]["counts"] == [
        2,
        4,
        6,
        8,
    ]


def test_api_verify_prashna_without_manual_awaits_input():
    res = client.post(
        "/api/verify",
        json={
            "date": "1990-08-15",
            "time": "12:00",
            "offset": "+05:30",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "engines": ["prashna"],
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["summary"]["error_count"] == 0
    assert body["summary"]["ashtamangala_provided"] is False
    assert body["summary"]["ashtamangala_status"] == "awaiting_manual_input"


def test_api_verify_compatibility():
    res = client.post(
        "/api/verify",
        json={
            "date": "1990-08-15",
            "time": "12:00",
            "timezone_id": "Asia/Kolkata",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "engines": ["compatibility"],
            "partner_date": "1992-03-10",
            "partner_time": "09:30",
            "partner_timezone_id": "Asia/Kolkata",
            "partner_latitude": 12.9716,
            "partner_longitude": 77.5946,
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["summary"]["error_count"] == 0
    assert body["summary"]["compatibility_engine"] == "Compatibility"
    assert 0 <= body["summary"]["ashtakoota_total"] <= 36
    assert body["summary"]["ashtakoota_max"] == 36
    assert body["summary"]["ashtakoota_boy_nakshatra"]
    assert body["summary"]["ashtakoota_girl_nakshatra"]


def test_api_verify_muhurta_events():
    res = client.post(
        "/api/verify",
        json={
            "date": "1990-08-15",
            "time": "12:00",
            "timezone_id": "Asia/Kolkata",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "engines": ["muhurta_events"],
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["summary"]["error_count"] == 0
    assert body["summary"]["muhurta_events_engine"] == "MuhurtaEvents"
    assert body["summary"]["muhurta_events_count"] == 5
    assert isinstance(body["summary"]["muhurta_events_good"], list)
    assert isinstance(body["summary"]["muhurta_events_avoid"], list)


def test_api_verify_panchaka():
    res = client.post(
        "/api/verify",
        json={
            "date": "1990-08-15",
            "time": "12:00",
            "timezone_id": "Asia/Kolkata",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "engines": ["panchaka"],
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["summary"]["error_count"] == 0
    assert body["summary"]["panchaka_engine"] == "PanchakaBhadra"
    assert body["summary"]["panchaka_label"]
    assert isinstance(body["summary"]["panchaka_moon_active"], bool)
    assert isinstance(body["summary"]["panchaka_bhadra_active"], bool)
    assert body["summary"]["panchaka_caution_count"] >= 0
    assert "TEC-074" in body["sections"]["panchaka"]["technique_ids"]


def test_api_verify_panchapakshi():
    res = client.post(
        "/api/verify",
        json={
            "date": "1990-08-15",
            "time": "12:00",
            "timezone_id": "Asia/Kolkata",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "engines": ["panchapakshi"],
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["summary"]["error_count"] == 0
    assert body["summary"]["panchapakshi_engine"] == "Panchapakshi"
    assert body["summary"]["panchapakshi_bird"] in {
        "Vulture",
        "Owl",
        "Crow",
        "Cock",
        "Peacock",
    }
    assert body["summary"]["panchapakshi_paksha"] in {"Shukla", "Krishna"}
    assert body["summary"]["panchapakshi_yama"]
    assert body["summary"]["panchapakshi_activity"]
    assert body["summary"]["panchapakshi_schedule_count"] == 10
    assert body["summary"]["panchapakshi_dark_deferred"] is False
    assert "TEC-075" in body["sections"]["panchapakshi"]["technique_ids"]
    assert body["sections"]["panchapakshi"]["engine_version"] == "0.2.0-both-paksha"


def test_api_verify_numerology():
    res = client.post(
        "/api/verify",
        json={
            "date": "1990-08-15",
            "time": "12:00",
            "timezone_id": "Asia/Kolkata",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "engines": ["numerology"],
            "numerology_name": "Rama",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["summary"]["error_count"] == 0
    assert body["summary"]["numerology_engine"] == "Numerology"
    assert body["summary"]["numerology_birth"] == 6
    assert body["summary"]["numerology_destiny"] == 6
    assert body["summary"]["numerology_birth_destiny_aligned"] is True
    assert body["summary"]["numerology_name"] == 8
    assert body["summary"]["numerology_name_provided"] is True
    assert body["summary"]["numerology_birth_planet"] == "Venus"


def test_api_verify_systems_approach():
    res = client.post(
        "/api/verify",
        json={
            "date": "1990-08-15",
            "time": "12:00",
            "timezone_id": "Asia/Kolkata",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "engines": ["systems_approach"],
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["summary"]["error_count"] == 0
    assert body["summary"]["systems_approach_engine"] == "SystemsApproach"
    assert body["summary"]["systems_approach_lagna"]
    assert body["summary"]["systems_approach_fm_count"] >= 2
    assert body["summary"]["systems_approach_fb_count"] >= 1
    assert isinstance(body["summary"]["systems_approach_functional_malefics"], list)
    assert "Rahu" in body["summary"]["systems_approach_functional_malefics"]
    assert "Ketu" in body["summary"]["systems_approach_functional_malefics"]


def test_api_verify_shadbala():
    res = client.post(
        "/api/verify",
        json={
            "date": "1990-08-15",
            "time": "12:00",
            "timezone_id": "Asia/Kolkata",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "engines": ["shadbala"],
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["summary"]["error_count"] == 0
    assert body["summary"]["shadbala_engine"] == "Shadbala"
    assert body["summary"]["shadbala_planet_count"] == 7
    assert body["summary"]["shadbala_strongest"]
    assert body["summary"]["shadbala_strongest_virupa"] > 0
    assert "TEC-023" in body["sections"]["shadbala"]["technique_ids"]
    assert body["sections"]["shadbala"]["engine_version"] == "0.4.0-kala-remainder"
    sun = next(p for p in body["sections"]["shadbala"]["shadbala"]["planets"] if p["planet"] == "Sun")
    assert "kala_partial" in sun["components_virupa"]
    assert "drik" in sun["components_virupa"]
    assert "saptavargaja" in sun["components_virupa"]["sthana_partial"]
    assert "drekkana" in sun["components_virupa"]["sthana_partial"]
    assert "ayana" in sun["components_virupa"]["kala_partial"]
    assert "tribhaga" in sun["components_virupa"]["kala_partial"]


def test_api_verify_bhava_bala():
    res = client.post(
        "/api/verify",
        json={
            "date": "1990-08-15",
            "time": "12:00",
            "timezone_id": "Asia/Kolkata",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "engines": ["bhava_bala"],
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["summary"]["error_count"] == 0
    assert body["summary"]["bhava_bala_engine"] == "BhavaBala"
    assert body["summary"]["bhava_bala_house_count"] == 12
    assert body["summary"]["bhava_bala_lagna_class"] == "nara"
    assert body["summary"]["bhava_bala_strongest_house"] is not None
    assert body["summary"]["bhava_bala_strongest_virupa"] > 0
    assert "TEC-024" in body["sections"]["bhava_bala"]["technique_ids"]
    assert body["sections"]["bhava_bala"]["engine_version"] == "0.1.0-partial-scaffold"


def test_api_verify_vimshopaka():
    res = client.post(
        "/api/verify",
        json={
            "date": "1990-08-15",
            "time": "12:00",
            "timezone_id": "Asia/Kolkata",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "engines": ["vimshopaka"],
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["summary"]["error_count"] == 0
    assert body["summary"]["vimshopaka_engine"] == "Vimshopaka"
    assert body["summary"]["vimshopaka_planet_count"] == 7
    assert body["summary"]["vimshopaka_strongest"]
    assert body["summary"]["vimshopaka_strongest_score"] > 0
    assert "TEC-025" in body["sections"]["vimshopaka"]["technique_ids"]
    assert body["sections"]["vimshopaka"]["engine_version"] == "0.1.0-shodashavarga"


def test_api_verify_lal_kitab():
    res = client.post(
        "/api/verify",
        json={
            "date": "1990-08-15",
            "time": "12:00",
            "timezone_id": "Asia/Kolkata",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "engines": ["lal_kitab"],
            "target_year": 2024,
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["summary"]["error_count"] == 0
    assert body["summary"]["lal_kitab_engine"] == "LalKitab"
    assert body["summary"]["lal_kitab_safety_level"] == "restricted"
    assert body["summary"]["lal_kitab_remedies_emitted"] is False
    assert body["summary"]["lal_kitab_varshphal"] is True
    assert body["summary"]["lal_kitab_varshphal_age"] == 34
    assert body["summary"]["lal_kitab_aspect_edges"] >= 9
    assert isinstance(body["summary"]["lal_kitab_house_diff_count"], int)


def test_api_verify_rectification():
    res = client.post(
        "/api/verify",
        json={
            "date": "1990-08-15",
            "time": "12:00",
            "timezone_id": "Asia/Kolkata",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "uncertainty_minutes": 10,
            "engines": ["rectification"],
            "rectification_step_minutes": 5,
            "rectification_events": "Marriage|2015-06-01",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["summary"]["error_count"] == 0
    assert body["summary"]["rectification_engine"] == "Rectification"
    assert body["summary"]["rectification_safety_level"] == "restricted"
    assert body["summary"]["rectification_winner_selected"] is False
    assert body["summary"]["rectification_events_provided"] is True
    assert body["summary"]["rectification_window_minutes"] == 10
    assert body["summary"]["rectification_sample_count"] >= 3
    assert body["summary"]["rectification_baseline_lagna"]
    assert body["summary"]["rectification_baseline_kunda"]


def test_api_verify_orchestration():
    res = client.post(
        "/api/verify",
        json={
            "date": "1990-08-15",
            "time": "12:00",
            "timezone_id": "Asia/Kolkata",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "engines": ["parashara", "lal_kitab", "orchestration"],
            "target_year": 2024,
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["summary"]["error_count"] == 0
    assert body["summary"]["orchestration_engine"] == "Orchestration"
    assert body["summary"]["orchestration_blended"] is False
    assert body["summary"]["orchestration_evidence_count"] >= 2
    assert body["summary"]["orchestration_conflict_count"] >= 1
    assert body["summary"]["orchestration_candidate_count"] >= 1
    assert body["sections"]["orchestration"]["safety"]["blended_verdicts"] is False


def test_api_verify_yogini():
    res = client.post(
        "/api/verify",
        json={
            "date": "1990-08-15",
            "time": "12:00",
            "timezone_id": "Asia/Kolkata",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "engines": ["yogini"],
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["summary"]["error_count"] == 0
    assert body["summary"]["yogini_engine"] == "YoginiDasha"
    assert body["summary"]["yogini_name"]
    assert body["summary"]["yogini_lord"]
    assert body["summary"]["yogini_maha_count"] >= 1
    assert body["summary"]["yogini_antar_count"] >= 8
    assert body["summary"]["yogini_balance_years"] > 0


def test_api_verify_transit():
    res = client.post(
        "/api/verify",
        json={
            "date": "1990-08-15",
            "time": "12:00",
            "timezone_id": "Asia/Kolkata",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "engines": ["transit"],
            "transit_date": "2024-08-15",
            "transit_time": "12:00",
            "transit_timezone_id": "Asia/Kolkata",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["summary"]["error_count"] == 0
    assert body["summary"]["transit_engine"] == "Transit"
    assert body["summary"]["transit_placement_count"] == 9
    assert body["summary"]["transit_conjunction_count"] >= 0
    assert body["summary"]["transit_aspect_count"] >= 0
    assert body["summary"]["transit_natal_lagna"]
    assert body["summary"]["transit_local_datetime"]
    assert body["input"]["transit_provided"] is True
    assert "TEC-035" in body["sections"]["transit"]["technique_ids"]

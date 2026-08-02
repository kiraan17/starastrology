from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from bhava360.console.service import parse_subject, run_verification

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "console" / "templates"

app = FastAPI(
    title="Bhava360 Internal Verification Console",
    description="Internal engine verification only — not a customer product UI.",
    version="0.1.0",
)
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

# Process-local last report for simple export during a session.
_LAST_REPORT: dict[str, Any] | None = None

DEFAULT_FORM = {
    "date": "1990-08-15",
    "time": "12:00",
    "offset": "+05:30",
    "timezone_id": "Asia/Kolkata",
    "dst_ambiguity_policy": "earlier",
    "latitude": "13.0827",
    "longitude": "80.2707",
    "location_label": "Chennai",
    "uncertainty": "",
    "ayanamsa": "lahiri",
    "house_system": "whole_sign",
    "engines": ["chart", "parashara", "ashtakavarga"],
    "jaimini_chara_scheme": "seven",
    "target_year": "2024",
    "annual_location_rule": "birth_place",
    "question_text": "",
    "ashtamangala_counts": "",
    "partner_date": "1992-03-10",
    "partner_time": "09:30",
    "partner_offset": "+05:30",
    "partner_timezone_id": "Asia/Kolkata",
    "partner_latitude": "12.9716",
    "partner_longitude": "77.5946",
    "partner_location_label": "Bengaluru",
    "numerology_name": "",
}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "index.html",
        {"form": DEFAULT_FORM, "report": None, "report_json": None},
    )


@app.post("/verify", response_class=HTMLResponse)
async def verify(
    request: Request,
    date: str = Form(...),
    time: str = Form(...),
    offset: str = Form("+00:00"),
    timezone_id: str = Form(""),
    dst_ambiguity_policy: str = Form("earlier"),
    latitude: float = Form(...),
    longitude: float = Form(...),
    location_label: str = Form(""),
    uncertainty: str = Form(""),
    ayanamsa: str = Form("lahiri"),
    house_system: str = Form("whole_sign"),
    engines: list[str] = Form(default=[]),
    jaimini_chara_scheme: str = Form("seven"),
    target_year: str = Form(""),
    annual_location_rule: str = Form("birth_place"),
    question_text: str = Form(""),
    ashtamangala_counts: str = Form(""),
    partner_date: str = Form(""),
    partner_time: str = Form(""),
    partner_offset: str = Form("+05:30"),
    partner_timezone_id: str = Form(""),
    partner_latitude: str = Form(""),
    partner_longitude: str = Form(""),
    partner_location_label: str = Form(""),
    numerology_name: str = Form(""),
) -> HTMLResponse:
    global _LAST_REPORT
    form = {
        "date": date,
        "time": time,
        "offset": offset,
        "timezone_id": timezone_id,
        "dst_ambiguity_policy": dst_ambiguity_policy,
        "latitude": str(latitude),
        "longitude": str(longitude),
        "location_label": location_label,
        "uncertainty": uncertainty,
        "ayanamsa": ayanamsa,
        "house_system": house_system,
        "engines": engines or ["chart"],
        "jaimini_chara_scheme": jaimini_chara_scheme,
        "target_year": target_year,
        "annual_location_rule": annual_location_rule,
        "question_text": question_text,
        "ashtamangala_counts": ashtamangala_counts,
        "partner_date": partner_date,
        "partner_time": partner_time,
        "partner_offset": partner_offset,
        "partner_timezone_id": partner_timezone_id,
        "partner_latitude": partner_latitude,
        "partner_longitude": partner_longitude,
        "partner_location_label": partner_location_label,
        "numerology_name": numerology_name,
    }
    uncertainty_val = float(uncertainty) if uncertainty.strip() else None
    target_year_val = int(target_year) if str(target_year).strip() else None
    subject = parse_subject(
        date_str=date,
        time_str=time,
        offset_str=offset,
        latitude=latitude,
        longitude=longitude,
        location_label=location_label,
        uncertainty_minutes=uncertainty_val,
        timezone_id=timezone_id,
        dst_ambiguity_policy=dst_ambiguity_policy,
    )
    partner_subject = None
    if "compatibility" in form["engines"] and partner_date.strip() and partner_time.strip():
        partner_subject = parse_subject(
            date_str=partner_date,
            time_str=partner_time,
            offset_str=partner_offset or offset,
            latitude=float(partner_latitude or latitude),
            longitude=float(partner_longitude or longitude),
            location_label=partner_location_label,
            uncertainty_minutes=None,
            timezone_id=partner_timezone_id or timezone_id,
            dst_ambiguity_policy=dst_ambiguity_policy,
        )
    report = run_verification(
        subject,
        ayanamsa=ayanamsa,
        house_system=house_system,
        engines=form["engines"],
        jaimini_chara_scheme=jaimini_chara_scheme,
        target_year=target_year_val,
        annual_location_rule=annual_location_rule,
        ashtamangala_counts=ashtamangala_counts or None,
        question_text=question_text or None,
        partner_subject=partner_subject,
        numerology_name=numerology_name or None,
    )
    _LAST_REPORT = report
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "form": form,
            "report": report,
            "report_json": json.dumps(report, indent=2, default=str),
        },
    )


@app.get("/export.json")
async def export_json() -> JSONResponse:
    if _LAST_REPORT is None:
        return JSONResponse({"error": "No report yet. Submit /verify first."}, status_code=404)
    return JSONResponse(_LAST_REPORT)


@app.get("/health")
async def health() -> dict[str, object]:
    from bhava360.api import public_api_readiness

    readiness = public_api_readiness()
    return {
        "status": "ok",
        "service": "bhava360-verification-console",
        "mode": "internal_verification_only",
        "public_api_ready": readiness["ready"],
        "license_gate": readiness["license_gate"],
    }


@app.post("/api/verify")
async def api_verify(payload: dict[str, Any]) -> JSONResponse:
    """JSON API for automated verification / future console clients."""
    global _LAST_REPORT
    subject = parse_subject(
        date_str=payload["date"],
        time_str=payload["time"],
        offset_str=payload.get("offset", "+00:00"),
        latitude=float(payload["latitude"]),
        longitude=float(payload["longitude"]),
        location_label=payload.get("location_label", ""),
        uncertainty_minutes=(
            float(payload["uncertainty_minutes"])
            if payload.get("uncertainty_minutes") not in (None, "")
            else None
        ),
        timezone_id=payload.get("timezone_id"),
        dst_ambiguity_policy=payload.get("dst_ambiguity_policy", "earlier"),
    )
    ty = payload.get("target_year")
    target_year_val = int(ty) if ty not in (None, "") else None
    partner_subject = None
    if "compatibility" in (payload.get("engines") or []) and payload.get("partner_date"):
        partner_subject = parse_subject(
            date_str=payload["partner_date"],
            time_str=payload.get("partner_time", "12:00"),
            offset_str=payload.get("partner_offset", payload.get("offset", "+00:00")),
            latitude=float(payload.get("partner_latitude", payload["latitude"])),
            longitude=float(payload.get("partner_longitude", payload["longitude"])),
            location_label=payload.get("partner_location_label", ""),
            uncertainty_minutes=None,
            timezone_id=payload.get("partner_timezone_id", payload.get("timezone_id")),
            dst_ambiguity_policy=payload.get("dst_ambiguity_policy", "earlier"),
        )
    report = run_verification(
        subject,
        ayanamsa=payload.get("ayanamsa", "lahiri"),
        house_system=payload.get("house_system", "whole_sign"),
        engines=payload.get("engines"),
        jaimini_chara_scheme=payload.get("jaimini_chara_scheme", "seven"),
        target_year=target_year_val,
        annual_location_rule=payload.get("annual_location_rule", "birth_place"),
        ashtamangala_counts=payload.get("ashtamangala_counts"),
        question_text=payload.get("question_text"),
        partner_subject=partner_subject,
        numerology_name=payload.get("numerology_name"),
    )
    _LAST_REPORT = report
    return JSONResponse(report)


@app.get("/docs-redirect")
async def docs_redirect() -> RedirectResponse:
    return RedirectResponse("/docs")

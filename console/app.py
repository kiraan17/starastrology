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
    "latitude": "13.0827",
    "longitude": "80.2707",
    "location_label": "Chennai",
    "uncertainty": "",
    "ayanamsa": "lahiri",
    "house_system": "whole_sign",
    "engines": ["chart", "parashara", "ashtakavarga"],
    "jaimini_chara_scheme": "seven",
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
    offset: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    location_label: str = Form(""),
    uncertainty: str = Form(""),
    ayanamsa: str = Form("lahiri"),
    house_system: str = Form("whole_sign"),
    engines: list[str] = Form(default=[]),
    jaimini_chara_scheme: str = Form("seven"),
) -> HTMLResponse:
    global _LAST_REPORT
    form = {
        "date": date,
        "time": time,
        "offset": offset,
        "latitude": str(latitude),
        "longitude": str(longitude),
        "location_label": location_label,
        "uncertainty": uncertainty,
        "ayanamsa": ayanamsa,
        "house_system": house_system,
        "engines": engines or ["chart"],
        "jaimini_chara_scheme": jaimini_chara_scheme,
    }
    uncertainty_val = float(uncertainty) if uncertainty.strip() else None
    subject = parse_subject(
        date_str=date,
        time_str=time,
        offset_str=offset,
        latitude=latitude,
        longitude=longitude,
        location_label=location_label,
        uncertainty_minutes=uncertainty_val,
    )
    report = run_verification(
        subject,
        ayanamsa=ayanamsa,
        house_system=house_system,
        engines=form["engines"],
        jaimini_chara_scheme=jaimini_chara_scheme,
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
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "bhava360-verification-console"}


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
    )
    report = run_verification(
        subject,
        ayanamsa=payload.get("ayanamsa", "lahiri"),
        house_system=payload.get("house_system", "whole_sign"),
        engines=payload.get("engines"),
        jaimini_chara_scheme=payload.get("jaimini_chara_scheme", "seven"),
    )
    _LAST_REPORT = report
    return JSONResponse(report)


@app.get("/docs-redirect")
async def docs_redirect() -> RedirectResponse:
    return RedirectResponse("/docs")

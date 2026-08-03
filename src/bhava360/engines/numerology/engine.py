"""Numerology engine — mantra-shastra thin slice (P21a / TEC-092)."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from bhava360.engines.numerology.numbers import (
    NUMEROLOGY_VARIANT,
    compute_numerology_profile,
)
from bhava360.kernel.errors import KernelError, KernelErrorCode
from bhava360.kernel.models import SubjectInput

ENGINE_NAME = "Numerology"
ENGINE_VERSION = "0.1.0-mantra-shastra"
TECHNIQUE_IDS = ("TEC-092",)
STATUS = "Candidate"


def run_numerology_engine(
    subject: SubjectInput | None = None,
    *,
    civil_date: date | datetime | None = None,
    name: str | None = None,
) -> dict[str, Any]:
    """
    Birth + destiny numbers from civil date; optional Chaldean name number.

    Numbers and planet tags only — no life-aspect scores, remedies, or advice.
    Name is never fabricated; omit or pass empty to skip name number.
    """
    if civil_date is None:
        if subject is None:
            raise KernelError(
                KernelErrorCode.UNSUPPORTED_CONFIG,
                "subject or civil_date is required for numerology",
            )
        civil_date = subject.local_datetime

    try:
        profile = compute_numerology_profile(birth=civil_date, name=name)
    except ValueError as exc:
        raise KernelError(KernelErrorCode.UNSUPPORTED_CONFIG, str(exc)) from exc

    return {
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "technique_ids": list(TECHNIQUE_IDS),
        "status": STATUS,
        "school": "numerology",
        "config": {
            "numerology.variant": NUMEROLOGY_VARIANT,
            "name_provided": bool(name and str(name).strip()),
        },
        "profile": profile,
        "deferred": [
            "Master / compound number retention (11, 22, …)",
            "Life-path vs destiny formula variants",
            "Life-aspect scoring packs (finance/romance/…)",
            "Pythagorean alphabet map",
            "Remedial mantra / name-change suggestions",
        ],
        "provenance": {
            "status": STATUS,
            "stamp": NUMEROLOGY_VARIANT,
            "sources": ["TEC-092"],
            "notes": [
                "Candidate mantra-shastra style numbers (VedAstro-overlap surface).",
                "Chaldean letter map and 1–9 planet lords are Candidate tables.",
                "Digital-root reduction always to 1–9 in this thin slice.",
            ],
        },
        "safety": {
            "note": "Numerology numbers for verification only — not advice or remedies.",
        },
    }


__all__ = [
    "ENGINE_NAME",
    "ENGINE_VERSION",
    "STATUS",
    "TECHNIQUE_IDS",
    "run_numerology_engine",
]

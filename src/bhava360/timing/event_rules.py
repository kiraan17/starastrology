"""Muhurta event rule packs — Candidate thin slice (TEC-093 / TEC-076)."""

from __future__ import annotations

from typing import Any

EVENT_RULE_VARIANT = "muhurta_event_candidate_v1"

# Activity ids for the thin pack — no medical/longevity/financial certainty claims.
ACTIVITY_IDS: tuple[str, ...] = (
    "general",
    "travel",
    "education",
    "business_start",
    "meeting",
)

# Chaughadiya labels treated as supportive (Candidate).
CHAUGH_GOOD = frozenset({"Amrit", "Shubh", "Labh"})
CHAUGH_BAD = frozenset({"Udveg", "Kaal", "Rog"})

# Tithi indices 1..30 — Candidate avoid-for-travel set.
TRAVEL_AVOID_TITHI = frozenset({4, 9, 14, 19, 24, 29, 30})  # Rikta + Amavasya-ish


def _verdict(score: int) -> str:
    if score <= -2:
        return "avoid"
    if score >= 2:
        return "good"
    return "mixed"


def evaluate_activity(
    *,
    activity_id: str,
    panchanga: dict[str, Any],
    muhurta_active: dict[str, Any],
    moon_tara: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Score one activity at the evaluated instant.

    Uses only already-computed panchanga/muhurta/tara facts (Candidate weights).
    """
    reasons: list[str] = []
    score = 0

    # Hard inauspicious windows
    for key, label in (
        ("rahu_kala", "Rahu Kala active"),
        ("yamaganda", "Yamaganda active"),
        ("gulika", "Gulika active"),
    ):
        if muhurta_active.get(key):
            score -= 2
            reasons.append(label)

    if muhurta_active.get("abhijit"):
        score += 2
        reasons.append("Abhijit muhurta active")

    chaugh = muhurta_active.get("chaughadiya") or {}
    ch_label = chaugh.get("label")
    if ch_label in CHAUGH_GOOD:
        score += 1
        reasons.append(f"Chaughadiya {ch_label}")
    elif ch_label in CHAUGH_BAD:
        score -= 1
        reasons.append(f"Chaughadiya {ch_label}")

    karana = (panchanga.get("karana") or {}).get("name")
    if karana == "Vishti":
        score -= 2
        reasons.append("Vishti (Bhadra) karana")

    tithi_idx = (panchanga.get("tithi") or {}).get("index")
    if activity_id == "travel" and tithi_idx in TRAVEL_AVOID_TITHI:
        score -= 1
        reasons.append(f"Travel-sensitive tithi index {tithi_idx}")

    if moon_tara:
        tara = moon_tara.get("tara")
        if moon_tara.get("auspicious") is True:
            score += 1
            reasons.append(f"Moon Tara {tara} supportive")
        elif tara in {"Vipat", "Pratyak", "Naidhana"}:
            score -= 2
            reasons.append(f"Moon Tara {tara} inauspicious")
        elif tara == "Janma":
            score -= 1
            reasons.append("Moon Tara Janma (sensitive)")

    # Education prefers Mercury hora (Candidate soft signal)
    hora = muhurta_active.get("hora") or {}
    if activity_id == "education" and hora.get("lord") == "Mercury":
        score += 1
        reasons.append("Mercury hora")
    if activity_id == "business_start" and hora.get("lord") in {"Mercury", "Jupiter", "Sun"}:
        score += 1
        reasons.append(f"{hora.get('lord')} hora")

    verdict = _verdict(score)
    return {
        "activity_id": activity_id,
        "verdict": verdict,
        "score": score,
        "reasons": reasons,
        "safety": "Timing classification only — not professional advice.",
    }


def evaluate_event_pack(
    *,
    panchanga: dict[str, Any],
    muhurta: dict[str, Any] | None,
    bala: dict[str, Any] | None,
    activities: tuple[str, ...] | list[str] | None = None,
) -> dict[str, Any]:
    """Evaluate Candidate muhurta event pack for selected activities."""
    selected = tuple(activities) if activities else ACTIVITY_IDS
    active = (muhurta or {}).get("active") or {}
    moon_tara = None
    if bala:
        moon_tara = (bala.get("tara_from_moon") or {}).get("Moon")

    results = [
        evaluate_activity(
            activity_id=aid,
            panchanga=panchanga,
            muhurta_active=active,
            moon_tara=moon_tara,
        )
        for aid in selected
        if aid in ACTIVITY_IDS
    ]

    return {
        "variant": EVENT_RULE_VARIANT,
        "activities_evaluated": [r["activity_id"] for r in results],
        "results": results,
        "summary": {
            "good": [r["activity_id"] for r in results if r["verdict"] == "good"],
            "mixed": [r["activity_id"] for r in results if r["verdict"] == "mixed"],
            "avoid": [r["activity_id"] for r in results if r["verdict"] == "avoid"],
        },
        "notes": [
            "Candidate weighted rules over Panchanga/Muhurta/Tara facts.",
            "No medical, financial, longevity, or legal certainty claims.",
            "Full classical muhurta nibandha packs deferred.",
        ],
    }


__all__ = [
    "ACTIVITY_IDS",
    "EVENT_RULE_VARIANT",
    "evaluate_activity",
    "evaluate_event_pack",
]

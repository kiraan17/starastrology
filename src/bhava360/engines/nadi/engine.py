"""Nakshatra Nadi engine scaffold (P13) — corpus-gated interpretations."""

from __future__ import annotations

from typing import Any

from bhava360.chart.builder import ChartConstructor
from bhava360.engines.nadi.corpus_gate import (
    assert_nadi_corpus_approved,
    load_nadi_corpus_status,
)
from bhava360.kernel.errors import KernelError, KernelErrorCode
from bhava360.kernel.models import ChartConfig, SubjectInput

ENGINE_NAME = "NakshatraNadi"
ENGINE_VERSION = "0.1.0-corpus-gated"
TECHNIQUE_IDS = ("TEC-054", "TEC-055")


def planet_in_star_facts(chart: dict[str, Any]) -> list[dict[str, Any]]:
    """Deterministic planet-in-nakshatra facts from a constructed chart (no Nadi rules)."""
    rows: list[dict[str, Any]] = []
    for p in chart.get("planets", []):
        rows.append(
            {
                "planet": p["planet"],
                "longitude_sidereal_deg": p["longitude_sidereal_deg"],
                "sign": p["sign"],
                "nakshatra": p.get("nakshatra"),
                "pada": p.get("pada"),
                "nakshatra_label": p.get("nakshatra_label"),
            }
        )
    asc = (
        chart.get("angles", {})
        .get("whole_sign", {})
        .get("ascendant", {})
    )
    if asc:
        rows.append(
            {
                "planet": "Asc",
                "longitude_sidereal_deg": asc.get("longitude_sidereal_deg"),
                "sign": asc.get("sign"),
                "nakshatra": asc.get("nakshatra"),
                "pada": asc.get("pada"),
                "nakshatra_label": asc.get("nakshatra_label"),
            }
        )
    return rows


def evaluate_nadi_chains(
    chart: dict[str, Any],
    *,
    status_path=None,
) -> dict[str, Any]:
    """Interpretive chain evaluation — requires Approved SRC-009 corpus."""
    status = assert_nadi_corpus_approved(
        status_path=status_path,
        purpose="nakshatra_nadi_chains",
    )
    # No Approved corpus ships with the repo yet — keep an explicit guard.
    raise KernelError(
        KernelErrorCode.CORPUS_GATE_BLOCKED,
        "Approved corpus present in status but rule pack not loaded",
        {
            "corpus_id": status.corpus_id,
            "hint": "Load versioned rule pack for corpus_id before enabling chain evaluation",
        },
    )


def run_nakshatra_nadi_engine(
    subject: SubjectInput | None = None,
    *,
    config: ChartConfig | None = None,
    chart: dict[str, Any] | None = None,
    attempt_chains: bool = False,
) -> dict[str, Any]:
    """
    P13 scaffold:
    - Always emits planet-in-star facts from the chart.
    - Interpretive chains/triggers remain corpus-gated (SRC-009).
    """
    built = chart or ChartConstructor(config).build(
        subject,  # type: ignore[arg-type]
        include_vimshottari=False,
    ).to_dict()
    corpus = load_nadi_corpus_status()
    facts = planet_in_star_facts(built)

    chains: dict[str, Any] | None = None
    chain_error: dict[str, Any] | None = None
    if attempt_chains:
        try:
            chains = evaluate_nadi_chains(built)
        except KernelError as exc:
            chain_error = {
                "code": exc.code.value,
                "message": exc.message,
                "details": exc.details,
            }

    return {
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "technique_ids": list(TECHNIQUE_IDS),
        "school": "nakshatra_nadi",
        "corpus_gate": corpus.to_dict(),
        "planet_in_star": facts,
        "chains": chains,
        "chain_error": chain_error,
        "notes": [
            "Planet-in-star facts are chart-derived only.",
            "Supporting/blocking/mixed chain evaluation requires Approved SRC-009 corpus.",
            "Palm-leaf manuscript Nadi claims are out of scope (TEC-065).",
            "Do not invent Nadi rules when corpus is missing.",
        ],
    }

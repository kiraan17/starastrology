# Freeze candidate package v0.1 (P24a)

**Manifest:** `release/freeze-candidate-manifest-v0.1.json`  
**Status:** `freeze_status=candidate` — **not Frozen**, **not expert-approved**  
**Date:** 2026-08-02

## Purpose

Package the backend thin-slice surface for expert review (Phase 23) and document public-API readiness blockers (Phase 24 prep) **without** claiming freeze or unlocking customer APIs.

## Explicit non-claims

- Does **not** set workflow status to `Frozen` or `Approved`
- Does **not** approve SRC-009 Nadi corpus
- Does **not** file ADR-002 L1/L2 license evidence
- Does **not** enable public API (`public_api_eligible=false`)

## Expert validation checklist (empty until reviewers assigned)

| tradition / area | reviewer | decision | date | notes |
|---|---|---|---|---|
| Kernel / chart / dasha | — | pending | — | |
| Parashara / Ashtakavarga | — | pending | — | |
| KP | — | pending | — | |
| Jaimini | — | pending | — | never Gemini |
| Panchanga / Muhurta | — | pending | — | |
| Tajika / annual | — | pending | — | |
| Specialist (SA, LK, Numerology, …) | — | pending | — | LK restricted |
| Orchestration / safety | — | pending | — | SRC-014/015 |

## Known limitations (programme-level)

1. Most engines are **Candidate / thin-slice** — interpretive rule packs incomplete.
2. **Nakshatra Nadi** chains blocked until SRC-009 Approved.
3. **Public API** blocked by ADR-002 until real L1/L2 evidence.
4. **Lal Kitab** remedies/debts deferred; restricted safety.
5. **Rectification** does not select a birth-time winner.
6. **Orchestration** never blends schools (`blended_verdicts=false`).
7. Classical edition citations still Candidate for many SRC rows.
8. Customer frontend / LLM narratives out of scope.

## How to promote later (human process)

1. Complete expert checklist rows with discrepancy notes.
2. File ADR-002 Path L1 or L2 evidence; flip license status under review.
3. Approve SRC-009 if Nadi chains are required for freeze scope.
4. Issue a **new** `FREEZE-vX.Y` manifest with `frozen=true` under release authority — do not edit this candidate into Frozen in place without process.

## Machine helpers

- `bhava360.api.load_freeze_candidate_manifest`
- `bhava360.api.freeze_candidate_summary`
- `bhava360.api.public_api_readiness` includes `freeze_candidate` + `blocked_reasons`

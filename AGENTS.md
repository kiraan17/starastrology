# AGENTS.md — Permanent AI Instructions for BHAVA360

Read this file and the controlling requirements before every task.

## Project identity

- **Product:** BHAVA360 Astrology Engine Backend
- **Controlling plan:** `docs/requirements/BHAVA360-Backend-Requirements-v1.0.md`
- **Charter:** `docs/requirements/PROJECT-CHARTER.md`
- **Status workflow:** `docs/status/STATUS-WORKFLOW.md`
- **Technique registry:** `registry/TECHNIQUE-REGISTRY.md`
- **Acceptance checklist:** Section 15 of the controlling plan

## Mandatory workflow for every task

1. **Read** this file, the charter, relevant specs and existing code.
2. **Explain** current state briefly.
3. **Propose** a small bounded change.
4. **Update specification** first when behaviour or contracts change.
5. **Implement** only the approved scope.
6. **Add tests** (positive, negative, boundary where applicable).
7. **Run tests** and report results.
8. **Show evidence** (changed files, limitations, registry IDs).
9. **Stop** and wait for human approval before the next major task.

## Hard rules

1. **One repository.** Do not create disconnected projects for each prompt.
2. **One bounded task at a time.** Never “build all astrology engines” in one change.
3. **Deterministic before generative.** Do not invent planetary positions, verdicts or ritual results.
4. **No invented astrology rules.** If a source is missing, mark `Source Needed` and stop that rule.
5. **Schools stay independent.** Do not blend Parashara, KP, Jaimini, Nadi, Lal Kitab, etc.
6. **Terminology:** Jaimini ≠ Gemini. Never name the Jaimini engine “Gemini”.
7. **No silent method changes.** Version rules and calculations; keep historical outputs reproducible.
8. **No silent expected-value edits.** Never change golden/expected test values only to make failing code pass.
9. **Frontend is out of scope** until backend Phase 24 gate. Do not build consumer UI, marketing, subscriptions or polished prediction cards.
10. **Internal console only** when UI is requested — verification, not product design.
11. **Safety:** medical, financial, longevity and death-related outputs are restricted; do not present them as certain advice.
12. **Manual inputs stay manual** (e.g. Ashtamangala shell counts).
13. **Swiss Ephemeris license** must be decided before public distribution or public service activation.
14. **Do not start calculation/kernel coding** until Phases 0–5 are approved.
15. **Database is not first.** Requirements, registry and data model come before table creation.

## Task prompt requirements

Every implementation prompt must include:

- Requirement / Technique Registry IDs
- Explicit in-scope and out-of-scope
- Acceptance criteria
- Required automated tests
- Source/variant references when touching interpretive rules

## Status values (techniques and rules)

Use only: `Not Researched` → `Source Ready` → `Spec Ready` → `Implemented` → `Auto-Tested` → `Expert-Checked` → `Approved` → `Frozen`

Do not mark a technique `Approved` or `Frozen` without recorded human/expert review.

## Output expected at end of every task

- Changed-files summary
- Tests added/run and results
- Known limitations
- Whether status of any technique/rule changed
- Confirmation that unrelated modules were not modified

## Current programme constraint

Phase 0 scaffolding is complete. Technique Registry exists as **provisional v0.2** (`registry/TECHNIQUE-REGISTRY.md`) awaiting product-owner confirmation of the official 96-item inventory. ADR-001 and ADR-002 are proposed. **Do not start calculation/kernel coding** until Phases 0–5 gates pass.

# P02 — Create the Live Technique Registry (96 Techniques)

**Phase:** 1  
**Goal:** Enter all 96 approved techniques so nothing is forgotten and incomplete work cannot be marked finished.  
**Blocked until:** Product owner supplies the complete Master Technique Coverage Register inventory.

## Read first

- `AGENTS.md`
- `docs/requirements/BHAVA360-Backend-Requirements-v1.0.md` §§1, 8, 9
- `docs/requirements/PROJECT-CHARTER.md`
- `docs/status/STATUS-WORKFLOW.md`
- `registry/TECHNIQUE-REGISTRY.md`

## In scope

1. Enter all 96 top-level techniques with permanent `technique_id` values.
2. Assign `parent_engine`, `kind`, `dependencies`, `safety_level`, `expert_approval_required`.
3. Set initial status to `Not Researched` unless a documented exception exists.
4. Flag broad techniques that require child decomposition (example: Shadbala).
5. Produce a dependency map draft and coverage dashboard definition update.
6. Reject duplicate or ambiguous names; record open questions in notes.

## Out of scope

- Implementing any calculation or rule code
- Choosing Swiss Ephemeris license
- Creating database tables
- Writing customer UI
- Filling invented sources

## Required inputs from product owner

- The complete 96-item list (exact names)
- Preferred engine/school grouping where known
- Any items that are manual-input, research-only or prohibited user-facing

## Acceptance criteria

- [ ] Registry contains exactly 96 top-level rows (or documented amendment if inventory count changes)
- [ ] Every row has required fields
- [ ] No duplicate/ambiguous entries without a resolution note
- [ ] Dependency map draft exists
- [ ] Broad techniques flagged for child decomposition
- [ ] No calculation code added

## Tests required

- Validation script or checked table ensuring unique IDs and required fields
- Count assertion: 96 top-level techniques

## Stop condition

Stop for human review after registry entry and dependency map draft. Do not begin Phase 2 source digitisation beyond registry linkage until approved.

# P00 — Lock Project Scope and Working Rules

**Phase:** 0  
**Goal:** Create one controlled project so AI agents do not build disconnected features or change rules without approval.  
**Out of scope:** Calculation code, database tables, school engines, customer frontend, verification console implementation.

## Read first

- `docs/requirements/BHAVA360-Backend-Requirements-v1.0.md` (Section 19 and Phase 0)
- Existing repository files

## Do exactly this

1. Confirm project name **BHAVA360** for the astrology backend (repo may remain `starastrology`).
2. Create folders for: requirements, sources, rules, calculation specifications, tests, expert reviews, release notes, registry, backlog, docs/status, docs/prompts, docs/architecture, docs/decisions.
3. Save/confirm the controlling requirements document in `docs/requirements/`.
4. Write `docs/requirements/PROJECT-CHARTER.md`.
5. Write permanent AI instructions in `AGENTS.md`.
6. Write `docs/status/STATUS-WORKFLOW.md` with statuses: Not Researched, Source Ready, Spec Ready, Implemented, Auto-Tested, Expert-Checked, Approved, Frozen.
7. Write `backlog/INITIAL-BACKLOG.md`.
8. Create placeholder `registry/TECHNIQUE-REGISTRY.md` noting if the 96-item inventory is missing.
9. Update root `README.md` to point to charter and AGENTS.md.
10. Do **not** implement Swiss Ephemeris, APIs, or UI.

## Acceptance criteria

- [ ] Repository structure exists and is documented
- [ ] Charter, AGENTS.md, status workflow and backlog exist
- [ ] No calculation/engine code was added
- [ ] Gap for missing 96-technique inventory is explicit
- [ ] Changed-files summary provided

## Tests required

Documentation-only task: verify required paths exist (structure check script or manual path list).

## Stop condition

After outputs exist, stop for human review. Do not start P02 until approved and the 96-item inventory is available.

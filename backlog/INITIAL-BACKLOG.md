# Initial Backlog

Ordered for the backend-first programme. Do not start calculation implementation before Phases 0–5 gates.

## Now (Phase 0)

| ID | Task | Status |
|---|---|---|
| P00 | Project charter, `AGENTS.md`, repo structure, status workflow, backlog | In progress / ready for review |
| DOC-01 | Controlling requirements saved with gap notes for incomplete paste sections | Done |

## Next (Phase 1) — blocked

| ID | Task | Blocked by |
|---|---|---|
| INV-01 | Supply complete 96-item Master Technique Coverage Register | Missing inventory in source paste |
| P02 | Create live Technique Registry and enter all 96 techniques | INV-01 |
| P02b | Decompose broad techniques into child items; build dependency map | P02 |

## Then (Phases 2–5)

| ID | Task |
|---|---|
| PLAN-01 | Build plan using VedAstro as reference (`docs/architecture/BUILD-PLAN-VEDASTRO-REFERENCE.md`) | Done (draft) |
| ADR-001 | Decide VedAstro usage option A/B/C + primary runtime |
| ADR-002 | Swiss Ephemeris license path before public activation |
| SPIKE-01 | Time-boxed VedAstro API/Docker golden-fixture spike (5 charts) |
| P03 | Source Register + variant decision log process |
| P04 | Architecture diagram + technology ADRs + Swiss Ephemeris license decision |
| P05 | Canonical data dictionary, ERD, schema specification, privacy classification |
| P06 | Rule specification template, versioning policy, sample rules |

## Later (after Phase 5 approval)

| ID | Task |
|---|---|
| P07+ | Calculation kernel and subsequent engine phases per controlling plan |

## Explicitly not started

- Customer frontend
- Consumer prediction narrative / LLM user copy
- Marketing site
- Subscription/billing UX
- Polished remedies UI

## Acceptance for moving past Phase 0

Human review confirms:

1. Folder structure matches the plan.
2. `AGENTS.md` is sufficient to constrain AI work.
3. Status values are understood.
4. Inventory gap (96 techniques) is acknowledged as the next blocker.

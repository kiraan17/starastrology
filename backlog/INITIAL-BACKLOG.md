# Initial Backlog

Ordered for the backend-first programme. Do not start calculation implementation before Phases 0–5 gates.

## Now (Phase 0 / early Phase 1–3 drafts)

| ID | Task | Status |
|---|---|---|
| P00 | Project charter, `AGENTS.md`, repo structure, status workflow, backlog | Ready for review |
| DOC-01 | Controlling requirements saved with gap notes for incomplete paste sections | Done |
| PLAN-01 | Build plan using VedAstro as reference | Draft done |
| ADR-001 | Runtime + VedAstro usage mode | Proposed |
| ADR-002 | Swiss Ephemeris license path | Proposed |
| SPIKE-01 | VedAstro API 5-chart golden fixtures | Done (comparator only) |
| REG-PROV | Provisional 96-row Technique Registry reconstructed from phases | Awaiting owner confirm |

## Next (Phase 1) — partially unblocked

| ID | Task | Blocked by |
|---|---|---|
| INV-01 | Confirm or replace provisional 96-item register with official inventory | Product owner review |
| P02 | Freeze Technique Registry v1 + dependency map | INV-01 |
| P02b | Decompose broad techniques into child items | P02 |

## Then (Phases 2–5)

| ID | Task |
|---|---|
| P03 | Source Register + variant decision log process |
| P04 | Architecture diagram + remaining technology ADRs |
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

## Acceptance for moving past Phase 0 / into P02 freeze

Human review confirms:

1. Folder structure matches the plan.
2. `AGENTS.md` is sufficient to constrain AI work.
3. Status values are understood.
4. Provisional 96-technique registry is confirmed or replaced.
5. ADR-001 and ADR-002 are accepted or amended.

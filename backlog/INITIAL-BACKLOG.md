# Initial Backlog

Ordered for the backend-first programme. Do not start calculation implementation before Phases 0–5 gates.

## Done / ready for review

| ID | Task | Status |
|---|---|---|
| P00 | Project charter, `AGENTS.md`, repo structure, status workflow, backlog | Ready for review |
| DOC-01 | Controlling requirements + gap notes | Done |
| PLAN-01 | Build plan using VedAstro as reference | Draft done |
| ADR-001 | Runtime + VedAstro usage mode | Proposed |
| ADR-002 | Swiss Ephemeris license path | Proposed |
| SPIKE-01 | VedAstro API 5-chart golden fixtures | Done (comparator only) |
| REG-PROV | Provisional 96-row Technique Registry | Awaiting owner confirm |
| P03 | Source Register process + seed sources + variant log | Draft done |
| P04a | Architecture context diagram | Draft done |
| P05 | Data dictionary + privacy + schema outline | Draft done |
| P06 | Rule spec template, versioning, checklist, 3 sample rules | Draft done |

## Next

| ID | Task | Blocked by |
|---|---|---|
| INV-01 | Confirm or replace provisional 96-item register | Product owner |
| ADR-SIGN | Accept/amend ADR-001 and ADR-002 | Product + tech (+ legal for ADR-002) |
| P02 | Freeze Technique Registry v1 | INV-01 |
| P03b | Expert-fill classical source editions/citations | Domain reviewers |
| P04b | ADR-003 database/API/test framework choices | ADR-001 |
| P05b | Approve data dictionary → then allow DDL | Review |
| P06b | Approve rule standard → resume interpretive encoding | Review |
| GATE-05 | Phase 0–5 approval package | Above items |

## Later (after Phase 5 approval)

| ID | Task |
|---|---|
| P07+ | Calculation kernel and subsequent engine phases |

## Explicitly not started

- Customer frontend
- Consumer prediction narrative / LLM user copy
- Marketing site
- Subscription/billing UX
- Polished remedies UI
- Production DB migrations
- Swiss Ephemeris production integration code

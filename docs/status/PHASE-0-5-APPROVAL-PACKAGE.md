# Phase 0–5 Approval Package

Sign off these before calculation-kernel coding (P07+).

| Item | Artefact | Approver | Status |
|---|---|---|---|
| Charter / AI rules | `docs/requirements/PROJECT-CHARTER.md`, `AGENTS.md` | Product + tech | Draft ready |
| Technique Registry v1 | `registry/TECHNIQUE-REGISTRY.md` | Product | Provisional — needs confirm |
| Source process | `sources/registers/*`, `sources/variants/*` | Domain + product | Draft ready |
| ADR-001 runtime/VedAstro | `docs/decisions/ADR-001-*.md` | Product + tech | Proposed |
| ADR-002 SE license | `docs/decisions/ADR-002-*.md` | Product + tech + legal | Proposed |
| Architecture context | `docs/architecture/CONTEXT-DIAGRAM.md` | Tech | Draft ready |
| Data dictionary + privacy | `specs/data-model/*` | Tech + privacy | Draft ready |
| Rule standard + samples | `rules/templates/*`, `rules/libraries/*` | Domain + tech | Draft ready |

When all rows are Approved, open P07 (calculation kernel) as a bounded task with golden tests against SPIKE-01 fixtures.

# Database Schema Specification (Draft Outline)

**Status:** Outline only — no migrations yet  
**Depends on:** approved `DATA-DICTIONARY.md`

## Planned store groups

1. **reference_data** — planets, signs, nakshatras, dignities, technique registry mirrors
2. **source_knowledge** — sources, quotations/notes, variants, approvals
3. **rule_library** — rules + versions + status
4. **chart_inputs** — subject inputs, manual prashna inputs, privacy flags
5. **calculation_snapshots** — immutable JSON documents + index columns
6. **engine_results** — evidence rows
7. **prediction_candidates** — orchestration outputs
8. **verification** — tests, expected/actual, reviews
9. **audit_ops** — who/when/what, release manifests

## Hard rules

- Append-only for approved rule versions and snapshots
- Soft-delete vs hard-delete policy for P3 data defined before production
- Every evidence row references snapshot + rule version

## Deferred

Concrete PostgreSQL DDL, indexes and partitioning wait for dictionary approval and ADR on database engine (PostgreSQL recommended default; not yet a signed ADR).

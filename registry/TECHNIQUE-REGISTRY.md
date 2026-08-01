# Technique Registry v0.1 (Placeholder)

**Status:** Blocked — awaiting complete 96-item Master Technique Coverage Register  
**Owner phase:** Phase 1 (P02)  
**Controlling plan:** `docs/requirements/BHAVA360-Backend-Requirements-v1.0.md` §8–§9

## Purpose

Make it impossible to forget a technique or mark an incomplete technique as finished.

## Entry requirements

Every row must include the fields defined in Section 9 (provisional field set in the controlling plan and below).

| Field | Required |
|---|---|
| `technique_id` | yes |
| `name` | yes |
| `parent_engine` | yes |
| `parent_technique_id` | if child |
| `kind` | yes |
| `dependencies` | yes (may be empty list) |
| `safety_level` | yes |
| `expert_approval_required` | yes |
| `status` | yes — start at `Not Researched` |
| `primary_sources` | when Source Ready+ |
| `variants` | when known |
| `test_refs` | when tests exist |
| `notes` | as needed |

## Current inventory

| technique_id | name | parent_engine | kind | status | notes |
|---|---|---|---|---|---|
| — | — | — | — | — | **No rows yet.** Source paste omitted the 96-item table. |

## Dependency map

Not started. Will be generated after all top-level rows are entered and broad items are decomposed.

## Coverage dashboard definition

See `docs/status/STATUS-WORKFLOW.md`. Target top-level count: **96** once inventory is supplied.

## Unblock checklist

- [ ] Product owner supplies the full 96-item list (names + intended school/engine where known)
- [ ] P02 enters every row with permanent IDs
- [ ] Duplicate/ambiguity review passes
- [ ] Decomposition backlog created for broad techniques (e.g. Shadbala → six components)

# Status Workflow

Applies to techniques, child calculations, rules and shared modules.

## Status values (ordered)

| Status | Meaning | Who can set |
|---|---|---|
| `Not Researched` | Known inventory item; no approved source work yet | Product / AI under task |
| `Source Ready` | Primary/secondary sources and variants recorded | Domain researcher + reviewer |
| `Spec Ready` | Rule/calculation specification approved | Spec reviewer |
| `Implemented` | Code exists matching the approved spec | Implementer |
| `Auto-Tested` | Required automated tests exist and pass | CI / quality owner |
| `Expert-Checked` | Domain expert reviewed examples/discrepancies | Tradition reviewer |
| `Approved` | Product accepts for use in non-frozen builds | Product owner + reviewers |
| `Frozen` | Version locked in a release candidate manifest | Release authority |

## Transition rules

1. No skipping forward except product-owner exception with written reason.
2. Any behavioural change after `Approved` creates a **new version** and resets that version to `Implemented` (or earlier if source/spec changed).
3. `Frozen` items are immutable; fixes ship as new versions.
4. Interpretive rules cannot enter `Implemented` without `Source Ready` and `Spec Ready`.
5. Objective calculation modules still require specs and tests; “source” may be an approved ephemeris/algorithm decision record.
6. Failed expert review moves item to `Spec Ready` or `Source Ready` with a discrepancy note — not silent code tweaks without documentation.

## Safety overlay

Independent of status, items may carry:

- `safety_level`: `normal` | `restricted` | `research_only` | `prohibited_user_facing`
- `expert_approval_required`: boolean

Restricted/research modules must not be exposed through customer APIs until legal/safety review is recorded.

## Coverage dashboard definition (initial)

Track counts by status for:

- Top-level techniques (target: 96 once inventory supplied)
- Child techniques
- Rules
- Engines/modules

Dashboard fields (logical; implementation later):

- `id`, `name`, `parent_engine`, `kind`, `status`, `safety_level`, `blocked_reason`, `last_updated`

## Phase gates (programme-level)

| Gate | Condition |
|---|---|
| End Phase 0 | Charter, structure, `AGENTS.md`, workflow, backlog exist and reviewed |
| End Phase 1 | All 96 techniques registered, no duplicates/ambiguity |
| End Phase 5 | Architecture, data model and rule standard approved; calc coding may start |
| Backend freeze | Critical calc + agreed core rules approved, tested, traceable; limitations explicit |

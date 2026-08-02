# ADR-001: Primary Runtime and VedAstro Usage Mode

- **Status:** Proposed (awaiting product/tech approval)
- **Date:** 2026-08-02
- **Phase:** 3 (decision drafted early to unblock spikes)
- **Related:** `docs/architecture/BUILD-PLAN-VEDASTRO-REFERENCE.md`

## Context

Bhava360 needs a calculation backend that is deterministic, testable and school-isolated. VedAstro provides a mature open MIT stack (C# library, Python package, HTTP API, Docker) built on Swiss Ephemeris. We must choose:

1. Primary implementation runtime for Bhava360 services
2. How VedAstro is used (reference only / bootstrap wrapper / hybrid)

## Options considered

### Runtime

| Option | Pros | Cons |
|---|---|---|
| **R1 — Python** | Fast AI-assisted iteration; `pyswisseph`; PyPI `VedAstro`; easy golden-test scripts | VedAstro’s deepest source is C#; native wrap of NuGet is weaker |
| **R2 — .NET / C#** | Best native use of `VedAstro.Library`; same ecosystem as reference | Heavier for mixed scripting/docs workflow in this repo today |
| **R3 — Polyglot** | Python services + optional .NET calc worker | Operational complexity too early |

### VedAstro usage

| Option | Meaning |
|---|---|
| **A — Reference only** | Swiss Ephemeris owned by us; VedAstro used as comparator |
| **B — Bootstrap wrapper** | Call VedAstro library/API as temporary kernel |
| **C — Hybrid** | Target A; allow short-lived B only behind `IAstronomyProvider` |

## Decision (proposed)

1. **Runtime: Python** for Bhava360 backend services, specs tooling, tests and internal console backend.
2. **VedAstro usage: Option C (Hybrid)**.
3. **Production astronomy provider target:** direct Swiss Ephemeris binding (`pyswisseph` or equivalent), not VedAstro.
4. **VedAstro HTTP API / Docker:** approved for SPIKE-01 and ongoing golden comparison fixtures only.
5. **`VedAstro.Library` NuGet:** not a production dependency unless a later ADR explicitly reverses this.

## Consequences

- Kernel code lives under Bhava360 control and can stamp ephemeris mode/version on every snapshot.
- School engines never import VedAstro prediction/chat layers.
- Disagreement with VedAstro becomes a documented variant or bug, never a silent average.
- If Python SE bindings prove insufficient, revisit R2 for a calc worker without rewriting engines.

## Approval

- [ ] Product owner
- [ ] Technical lead
- [ ] Quality owner (testing impact)

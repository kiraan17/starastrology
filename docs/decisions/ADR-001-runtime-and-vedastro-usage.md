# ADR-001: Primary Runtime and VedAstro Usage Mode

- **Status:** Accepted
- **Date:** 2026-08-02
- **Accepted on:** 2026-08-02 (product approval via agent session "approve")
- **Phase:** 3
- **Related:** `docs/architecture/BUILD-PLAN-VEDASTRO-REFERENCE.md`

## Context

Bhava360 needs a calculation backend that is deterministic, testable and school-isolated. VedAstro provides a mature open MIT stack (C# library, Python package, HTTP API, Docker) built on Swiss Ephemeris. We must choose:

1. Primary implementation runtime for Bhava360 services
2. How VedAstro is used (reference only / bootstrap wrapper / hybrid)

## Decision

1. **Runtime: Python** for Bhava360 backend services, specs tooling, tests and internal console backend.
2. **VedAstro usage: Option C (Hybrid)**.
3. **Production astronomy provider target:** direct Swiss Ephemeris binding (`pyswisseph` or equivalent), not VedAstro.
4. **VedAstro HTTP API / Docker:** approved for SPIKE-01 and ongoing golden comparison fixtures only.
5. **`VedAstro.Library` NuGet:** not a production dependency unless a later ADR explicitly reverses this.

## Consequences

- Kernel code lives under Bhava360 control and can stamp ephemeris mode/version on every snapshot.
- School engines never import VedAstro prediction/chat layers.
- Disagreement with VedAstro becomes a documented variant or bug, never a silent average.
- Private/dev may use Swiss Ephemeris Moshier mode or SE files per ADR-002.

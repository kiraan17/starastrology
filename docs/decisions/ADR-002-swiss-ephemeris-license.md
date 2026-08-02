# ADR-002: Swiss Ephemeris Licensing Path

- **Status:** Accepted (conditional) — public gate enforced in code
- **Date:** 2026-08-02
- **Accepted on:** 2026-08-02 for private/dev programme continuation
- **Phase:** 3
- **Related:** Swiss Ephemeris General/Licensing docs; ADR-001; `docs/decisions/adr-002-evidence/`

## Context

Swiss Ephemeris is dual-licensed (AGPL vs professional/commercial). Bhava360 intends a public astrology backend later.

## Decision

1. **Private/dev (now):** authorised to use `pyswisseph` including built-in Moshier mode and/or local SE ephemeris files for development and CI.
2. **Public API or customer app activation:** blocked until Path L1 (AGPL compliance) or Path L2 (commercial SE license) evidence is recorded **and** the machine-readable gate status is flipped under review.
3. **Default product intent:** Path L2 for a commercial Bhava360 SaaS unless product owner chooses full AGPL.
4. Every calculation snapshot must record ephemeris mode/library version.
5. Kernel default for early golden tests: Moshier (`SEFLG_MOSEPH`) with Lahiri sidereal mode, because SPIKE-01 VedAstro fixtures match within tight tolerance.
6. **Enforcement:** `bhava360.licensing.assert_public_activation_allowed` / `bhava360.api.enable_public_api_surface` raise `LICENSE_GATE_BLOCKED` while status is blocked. `BHAVA360_PUBLIC_API` env cannot bypass.

## Evidence package

- Checklists: `docs/decisions/adr-002-evidence/`
- Runtime status: `src/bhava360/licensing/adr002_public_status.json` (default `blocked`)

## Approval

- [x] Product owner (session approve) — private/dev path
- [x] Technical lead — private/dev path
- [ ] Privacy/security/legal reviewer — required before public activation
- [ ] Path L1 or L2 evidence filed — required before public activation

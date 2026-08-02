# ADR-002: Swiss Ephemeris Licensing Path

- **Status:** Proposed (must be resolved before public activation)
- **Date:** 2026-08-02
- **Phase:** 3
- **Related:** Swiss Ephemeris General/Licensing docs; ADR-001

## Context

Swiss Ephemeris is dual-licensed:

1. **AGPL** — free if the distributed/networked application’s corresponding source complies with AGPL obligations
2. **Professional / commercial license** — required when AGPL terms are not acceptable (typical closed SaaS)

Bhava360 intends a public astrology backend/API and later customer app. License choice is a release gate, not a coding detail.

VedAstro’s MIT code does **not** replace Swiss Ephemeris license obligations for the ephemeris library/data used at runtime.

## Decision (proposed)

1. **Development / private spikes:** may use Swiss Ephemeris under AGPL evaluation terms; no public production traffic.
2. **Public API or customer app activation:** blocked until one path is chosen and recorded:
   - **Path L1 — AGPL:** publish Bhava360 backend source as required by AGPL and accept copyleft obligations, **or**
   - **Path L2 — Commercial SE license:** purchase/sign Astrodienst professional license before public activation
3. **Default recommendation for a commercial Bhava360 product:** **Path L2**, unless product owner explicitly chooses full AGPL compliance.
4. **Ephemeris files and library version** must be recorded on every calculation snapshot regardless of path.
5. Do not ship or host SE binaries/data in a public service until the chosen path is signed off.

## Non-goals

- This ADR does not choose ayanamsa defaults.
- This ADR does not approve redistribution of third-party ephemeris files beyond SE terms.

## Consequences

- Phase 24 / public launch checklist includes license evidence.
- CI may run SE locally in private environments now.
- Marketing/site deploy is unrelated; calc API is the regulated surface.

## Approval

- [ ] Product owner
- [ ] Technical lead
- [ ] Privacy/security/legal reviewer

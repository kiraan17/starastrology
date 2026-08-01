# BHAVA360 Project Charter

**Project name:** BHAVA360 Astrology Engine Backend  
**Repository:** starastrology  
**Charter version:** 0.1  
**Date:** 1 August 2026  
**Controlling plan:** `docs/requirements/BHAVA360-Backend-Requirements-v1.0.md`

## Mission

Build, document and validate a deterministic, source-traceable astrology calculation and rule-engine backend before any customer-facing frontend is designed or shipped.

## In scope (backend-first programme)

- Astronomical and calendrical calculation kernel.
- Chart construction and derived astrology data.
- Independent school engines (Parashara, Jaimini, KP, Nadi traditions, Ashtakavarga, Prashna, Tajika, Lal Kitab and other approved inventory items).
- Timing, transit, daily and hourly engines.
- Rule source tracking, versioning, evidence output and conflict handling.
- Database, APIs, automated tests, golden charts and expert review workflow.
- Internal verification console for raw-result inspection only.

## Out of scope until backend freeze + Phase 24 gate

- Final customer UI, branding, onboarding, subscriptions and marketing pages.
- LLM-generated user predictions before deterministic engine validation.
- Claims that palm-leaf manuscript Nadi can be recreated from an ephemeris.
- Automatic medical diagnosis, financial guarantees, death prediction or other unsafe deterministic claims.

## Non-negotiable principles

See Section 3 of the controlling requirements document. Summary:

1. Deterministic before generative.
2. Schools remain independent.
3. Every result is traceable.
4. No silent rule changes.
5. No technique is complete without tests.
6. Manual systems stay manual.
7. Uncertain traditions are labelled as variants.
8. Safety restrictions are engine-enforced.

## Terminology lock

| Term | Meaning |
|---|---|
| **Jaimini** | Classical astrology system / engine name |
| **Gemini** | AI model/product name only — never used to label the Jaimini engine |
| **Bhava360** | Product / programme name |
| **Internal verification console** | Temporary testing UI — not the customer product |

## Current programme stage

**Phase 0 — Lock project scope and working rules**

Calculation kernel, database implementation and school engines must not start until Phases 0–5 approval gates are passed.

## Immediate blockers

1. **Master Technique Coverage Register (96 items)** was missing from the source paste. Phase 1 cannot close until the full inventory is supplied.
2. Several requirement sections were incomplete in the paste (architecture narrative, wave table, field definitions detail, prompt pack, numeric estimates). Marked as gap notes in the controlling document.

## Approval authorities

| Decision type | Authority |
|---|---|
| Scope and priority | Product owner |
| Architecture, licensing, security | Technical architect / lead |
| Astrology rule/source/variant | Domain reviewer for that tradition |
| Test expectations / golden values | Quality owner + domain reviewer |
| Restricted modules (medical/financial/longevity) | Privacy/security/legal + product owner |

## Definition of Phase 0 done

- [x] Controlling requirements saved in repository
- [x] Repository structure created
- [x] `AGENTS.md` permanent AI instructions present
- [x] Status workflow defined
- [x] Initial backlog created
- [ ] Human review of folders and instructions
- [ ] Approval to start P02 (Technique Registry) after 96-item inventory is available

## Next approved task after Phase 0 review

**P02 — Technique Registry v1**, only after the complete 96-technique inventory is provided.

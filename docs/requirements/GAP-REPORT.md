# Gap Report — Requirements Paste Review (1 Aug 2026)

## Verdict

The BHAVA360 backend-first plan is **directionally correct and professionally sequenced**. The dependency order (requirements → registry → sources → architecture → data model → rule standard → kernel → engines → orchestration → tests → console → freeze → frontend) matches how a high-stakes calculation system should be built.

Phase 0 scaffolding has been created in this repository. **Calculation coding must not start yet.**

## What is strong

1. Clear executive decision against premature frontend and LLM verdicts.
2. Non-negotiable principles (determinism, school isolation, traceability, versioning, tests, manual-input gates, safety).
3. Phased gates with explicit approval criteria.
4. Correct warning that database is not step one.
5. Swiss Ephemeris dual-license callout before public activation.
6. Terminology lock: Jaimini vs Gemini.
7. Realistic “backend complete” definition and continuous testing guidance.

## Critical blockers

| ID | Gap | Impact |
|---|---|---|
| G1 | **Section 8 — 96-item technique inventory missing** from the paste | Phase 1 / P02 cannot complete |
| G2 | Section 2 narrative body missing | Low — recoverable from Phase 6 plan |
| G3 | Section 4 architecture detail missing | Medium — required before Phase 3 close |
| G4 | Section 5 register list incomplete | Low — reconstructed from phases |
| G5 | Section 7 wave table missing | Medium — provisional waves added |
| G6 | Section 9 field definitions incomplete | Medium — provisional fields added |
| G7 | Section 11 test matrix detail missing | Medium — deferred to Phase 21 with minima |
| G8 | Section 14 full prompt sequence missing | Medium — P00/P02 prompts created; rest later |
| G9 | Section 17 numeric estimates incomplete | Low — prefer phase sequencing |
| G10 | Section 18 risk register incomplete | Low — provisional risks added |

## Product / engineering risks still true even with a good plan

1. Treating “96 techniques implemented” as done — freeze requires tested + approved + traceable.
2. Mixing KP ayanamsa/houses with Lahiri/Parashara defaults.
3. Encoding yogas before the rule specification standard (Phase 5).
4. Using an LLM as an astrology source.
5. Shipping Nadiamsa/D150 without birth-time uncertainty gates.
6. Averaging contradictory schools (especially Lal Kitab vs Parashara).

## Recommended immediate human actions

1. Review Phase 0 folders and `AGENTS.md`.
2. Paste/supply the **complete 96-technique table**.
3. Approve running **P02** only after that inventory exists.
4. Keep Phases 2–5 documentation moving in parallel research only; no kernel coding until gates pass.

## Phase 0 deliverables in this change

- Controlling requirements saved with gap notes
- Charter, AGENTS.md, status workflow, backlog, repo structure doc
- Technique registry placeholder
- P00 and P02 prompt files
- Structure check script

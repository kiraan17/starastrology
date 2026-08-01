# BHAVA360 Astrology Engine App Requirements and Step-by-Step Build Plan

**Backend-first plan covering calculation, logic, rule engines, database, validation, internal testing UI and AI-assisted development**

Version 1.0 | 27 July 2026

**Decision:** Do not build the final customer frontend now. First build, document and validate the complete astrology backend. The temporary UI is only a verification console.

---

## 1. Executive Decision

Your proposed direction is correct. However, “build the backend first” does not mean starting directly with random calculation code or creating the database first. A professional development team first fixes the requirements, terminology, sources, architecture, data contracts and test method. Then it builds the calculation kernel and astrology engines in dependency order. The final frontend starts only after the backend has passed defined validation gates.

**Correct order:** Requirements → Source library → Architecture → Technique Registry → Calculation kernel → Astrology engines → Orchestration → Automated testing → Internal verification UI → Expert validation → Backend freeze → Customer frontend.

### What is included in this backend-first programme

- Astronomical and calendrical calculations.
- Chart construction and all derived astrology data.
- Independent rule engines for Parashara, Jaimini, KP, Nadi, Ashtakavarga, Prashna, Tajika, Lal Kitab and the remaining systems in the approved inventory.
- Timing engines, transit engines, daily and hourly guidance engines.
- Rule source tracking, version control, evidence output and conflict handling.
- Database, APIs, automated tests, benchmark chart library and expert review workflow.
- A simple internal testing console for checking raw results. It is not the final product UI.

### What is not included yet

- Final customer-facing screens, branding, onboarding, subscriptions or marketing pages.
- LLM-written predictions presented to users before deterministic engine validation.
- Claims that manuscript-based palm-leaf Nadi can be recreated from an ephemeris.
- Automatic medical diagnosis, financial guarantees, death prediction or other unsafe deterministic claims.

**Terminology correction:** Jaimini is the astrology system. Gemini is an AI model/product name. Keep these terms separate in every requirement, database field and prompt.

---

## 2. How a Professional App Is Built, in Simple Language

> **Gap note (paste incomplete):** Section body was not fully supplied in the source paste. Until expanded, treat Section 1 order and Section 6 phases as the controlling process narrative.

**Working summary used by this repository:**

1. Lock scope and AI working rules (Phase 0).
2. Register every technique before coding it (Phase 1).
3. Bind each rule to approved sources (Phase 2).
4. Choose architecture and licenses (Phase 3).
5. Define data contracts before tables (Phase 4).
6. Standardise rule specs (Phase 5).
7. Build calculation → chart → strengths → timing → school engines in dependency order (Phases 6–20).
8. Test continuously; use an internal verification console only (Phases 21–22).
9. Freeze only after expert validation (Phase 23).
10. Expose stable APIs before customer frontend (Phase 24).

---

## 3. Non-Negotiable Product Principles

1. **Deterministic before generative:** The astrology engine calculates and decides. An LLM may explain approved results later, but it must never calculate positions or invent verdicts.
2. **Schools remain independent:** Parashara, KP, Jaimini, Nadi, Lal Kitab and other systems use separate rules, configurations and outputs.
3. **Every result is traceable:** A result must show the technique, rule ID, source, input data, conditions matched, strength modifiers and engine version.
4. **No silent rule changes:** Every rule change creates a new version and a change note. Historical outputs must remain reproducible.
5. **No technique is “complete” without tests:** Implementation alone is insufficient. Every technique requires automated tests and expert-reviewed examples.
6. **Manual systems stay manual:** Ashtamangala shell results and other ritual/manual inputs must be entered explicitly. They cannot be fabricated from birth data.
7. **Uncertain traditions are labelled:** Where different schools or authors disagree, the app stores variants rather than pretending there is one universal rule.
8. **Safety restrictions are part of the engine:** Medical, financial, longevity and remedial outputs require disclaimers, conservative wording and restricted claim rules.

---

## 4. Backend Architecture in Plain English

> **Gap note (paste incomplete):** Full architecture narrative was not supplied. Phase 3 must produce the approved architecture diagram and ADRs. Do not invent a production topology here.

**Mandatory separation (locked by principles):**

- **Calculation kernel** — astronomical/calendrical facts only (Swiss Ephemeris / approved ephemeris interface).
- **Chart construction** — derived chart structures from kernel outputs.
- **Independent school engines** — Parashara, KP, Jaimini, Nadi, etc., never silently blended.
- **Timing platform** — dashas, transits, daily/hourly windows as shared services with school-specific adapters.
- **Evidence / orchestration** — structured evidence, conflict policy, scoring configuration.
- **Internal verification console** — inspection UI only; not the customer product.
- **Persistence** — versioned rules, snapshots, evidence, reviews; never overwrite approved history.

**Important:** The database is not the first thing to build. First define the requirements, technique registry and data model. Then create the database to match those approved definitions.

---

## 5. Documents and Registers Required Before Major Coding

> **Gap note (paste incomplete):** Expand this list as artefacts are approved.

| Artefact | Owner phase | Status location |
|---|---|---|
| Project charter | Phase 0 | `docs/requirements/PROJECT-CHARTER.md` |
| AI project instructions | Phase 0 | `AGENTS.md` |
| Status workflow | Phase 0 | `docs/status/STATUS-WORKFLOW.md` |
| Initial backlog | Phase 0 | `backlog/INITIAL-BACKLOG.md` |
| Technique Registry v1 | Phase 1 | `registry/TECHNIQUE-REGISTRY.md` |
| Source Register | Phase 2 | `sources/registers/` |
| Architecture + ADRs | Phase 3 | `docs/architecture/`, `docs/decisions/` |
| Data dictionary / schema spec | Phase 4 | `specs/data-model/` |
| Rule specification standard | Phase 5 | `rules/templates/` |

---

## 6. Detailed Step-by-Step Development Plan

### Phase 0: Lock the Project Scope and Working Rules

**Purpose:** Create one controlled project so AI agents do not build disconnected features or change rules without approval.

**What the AI/development work must do**

- Create one repository and one project name for the astrology backend.
- Create folders for requirements, sources, rules, calculation specifications, tests, expert reviews and release notes.
- Add permanent AI instructions that require reading the project documents before every task.
- Define that final frontend work is out of scope until backend approval.
- Create status values: Not Researched, Source Ready, Spec Ready, Implemented, Auto-Tested, Expert-Checked, Approved and Frozen.

**Required outputs**

- Project charter
- Repository structure
- AI project instructions
- Status workflow
- Initial backlog

**Approval gate:** No calculation work begins until the repository and project instructions exist.

**Important note:** Use one central instruction file (`AGENTS.md`) to keep every AI task consistent.

### Phase 1: Create the Complete Technique Registry

**Purpose:** Make it impossible to forget a technique or mark an incomplete technique as finished.

**What the AI/development work must do**

- Enter all 96 approved techniques from this document.
- Break broad techniques into smaller child items where required. Example: Shadbala contains six strength calculations.
- Assign a permanent technique ID and parent engine to every item.
- Record whether the item is calculation, classification, timing, interpretation, manual input, lookup or orchestration.
- Record dependencies. Example: Kakshya scoring depends on correct Ashtakavarga and transit calculations.
- Record safety level and whether final expert approval is compulsory.

**Required outputs**

- Technique Registry v1
- Dependency map
- Coverage dashboard definition

**Approval gate:** The registry contains every approved technique and no duplicate or ambiguous entries.

> **Blocker:** Section 8 inventory table was not fully pasted into this controlling copy. Phase 1 cannot close until the complete 96-item list is supplied and entered.

### Phase 2: Build the Astrology Source Library

Prevent the AI from inventing or mixing astrology rules. Choose primary/secondary sources, separate classical text vs modern interpretation vs product rules, record variants, require astrologer approval, and flag non-algorithmic traditions.

### Phase 3: Approve the System Architecture and Technology Decisions

Decide calculation runtime and Swiss Ephemeris integration, API/database/test/deploy approach, kernel vs engine separation, environments, Swiss Ephemeris licensing before public activation, plus backup/secrets/privacy/security/audit requirements.

### Phase 4: Define the Canonical Data Model and Database Plan

Define birth/location/timezone/uncertainty, chart configuration, planetary/cusp/nakshatra/varga/dasha/transit/panchanga objects, rule/source/version/evidence/result/approval records, calculation snapshots, privacy boundaries, retention/deletion/backup/audit.

### Phase 5: Create the Rule Specification Standard

Mandatory rule fields, variants, negative/cancellation representation, activation rules, evidence output, versioning and deprecation. Complete before large-scale yoga encoding.

### Phase 6: Build the Astronomical Calculation Kernel

Date/time/UTC/timezone/DST/Julian day; planetary positions/speeds/retrograde/nodes; sidereal/ayanamsas; houses/cusps; angles; sunrise/sunset; library version recording; structured errors; golden tests.

### Phase 7: Build Chart Construction and Derived Calculations

Rasi vs Bhava Chalit; nakshatra/pada/star-sub-sub lords; house mappings; Vargas D1–D60 (D150 gated); combustion/retro/planetary war; aspects; dignity/ownership/dispositors; relationship graph; boundary tests.

### Phase 8: Build Strength and Classification Foundations

Benefic/malefic classifications; dignity and cancellation; Shadbala/Bhava Bala components; Vimshopaka; Argala; karakas; store components and thresholds as configuration.

### Phase 9: Build the Dasha and Period Timing Platform

Vimshottari full levels; conditional dashas; independent Jaimini rashi dashas; Yogini/Kalachakra/annual variants; common timing interface; continuity/boundary tests.

### Phase 10: Build the Parashara Engine

Independent, source-traceable yogas/doshas/activation; natal potential vs current manifestation; rule-level tests including cancellation/activation examples.

### Phase 11: Build the KP Engine

KP New Ayanamsa + Placidus; star/sub/sub-sub chains; significators; Ruling Planets; Horary 1–249; no reuse of Lahiri values when KP config differs.

### Phase 12: Build Ashtakavarga and Transit Strength Engines

BAV/SAV/Prastara; Shodhana; Sodhya Pinda; Kakshya; store bindu contributors.

### Phase 13: Build Nakshatra Nadi as a First-Class Engine

Planet-in-star chains; supporting/blocking/mixed chains; depth/stop conditions; evidence paths; approved rule corpus required.

### Phase 14: Build Bhrigu Nandi Nadi and Other Codable Nadi Modules

Separate modules; accuracy gates; exclude palm-leaf manuscript claims; label each tradition.

### Phase 15: Build the Jaimini Engine

Chara Karakas, Karakamsa/Swamsa, Arudha, rashi drishti/argala, rashi dashas. **Do not label this engine “Gemini.”**

### Phase 16: Build Daily, Panchanga and Hourly Timing Engines

Tithi/Vara/Nakshatra/Yoga/Karana; Rahu Kala etc.; Tara/Chandra Bala; Hora/Chaughadiya; Panchapakshi; location-aware sunrise boundaries.

### Phase 17: Build Annual, Return, Chakra and Progression Frameworks

Tajika/Varshaphal, Tithi Pravesh, Sudarshana, chakras, progressions; document annual location rule.

### Phase 18: Build Prashna and Horary Systems

KP Horary, Prashna Marga, Tamil/Aroodha, Ashtamangala manual input, audit logs; no natal assumption reuse where tradition differs.

### Phase 19: Build Parallel Schools and Specialised Applications

Lal Kitab, Systems Approach, Sripati/Bhava Chalit, numerology, muhurta, compatibility, medical (restricted), mundane/financial (research), vastu bridge, rectification, longevity (restricted research).

### Phase 20: Build the Evidence, Scoring and Conflict-Orchestration Layer

Shared domains, structured evidence, activation requirements, confidence, conflict groups, prediction candidates, safety gates.

### Phase 21: Build Comprehensive Automated Testing and Benchmarking

Unit/boundary/integration/golden/cross-software/historical/regression/performance/data-quality tests. Never change expected values merely to make failing code pass.

### Phase 22: Build the Internal Verification Console

Simple inspection UI for inputs, raw calc, charts, engines, evidence, comparison, export, expert approval controls. No consumer polish.

### Phase 23: Run Expert Validation, Reconciliation and Backend Freeze

Review panel by tradition; resolve discrepancies; freeze versions; known limitations. Freeze condition is tested + traceable + approved — not “96 techniques implemented.”

### Phase 24: Prepare the Backend for the Later Customer Frontend

Stable APIs, auth/rate limits/privacy, monitoring, narrative-output contract for later LLM layer, API docs. Only after this gate does customer frontend planning begin.

---

## 7. Recommended Implementation Waves

> **Gap note (paste incomplete):** Wave table not supplied. Until expanded, use dependency order below as provisional waves.

| Wave | Content | Depends on |
|---|---|---|
| W0 | Phases 0–5 (docs, registry, sources, architecture, data model, rule standard) | — |
| W1 | Phases 6–8 (kernel, chart, strength/classification) | W0 |
| W2 | Phase 9 (dasha platform) | W1 |
| W3 | Phases 10–12 (Parashara, KP, Ashtakavarga) | W1–W2 |
| W4 | Phases 13–15 (Nadi modules, Jaimini) | W1–W2 |
| W5 | Phases 16–18 (daily/panchanga, annual/chakra, prashna) | W1–W2 |
| W6 | Phase 19 (specialist schools) | W1–W3 as relevant |
| W7 | Phases 20–24 (orchestration, tests, console, freeze, API) | Prior waves |

A later wave may be researched while an earlier wave is built, but cannot be approved before its dependencies are stable.

---

## 8. Master Technique Coverage Register (96 Items)

> **CRITICAL GAP:** The 96-item inventory table was not included in the source paste. Phase 1 (Technique Registry) is blocked until the complete approved inventory is provided.

Placeholder tracking file: `registry/TECHNIQUE-REGISTRY.md`

Each broad row must later be expanded into child calculations and rules. Status is maintained in the live registry, not only in this document.

---

## 9. Required Fields for Every Technique

> **Gap note (paste incomplete):** Use the following provisional field set until Section 9 is formally expanded and approved.

| Field | Description |
|---|---|
| `technique_id` | Permanent unique ID |
| `name` | Human-readable name |
| `parent_engine` | School/platform ownership |
| `parent_technique_id` | Optional parent for child decomposition |
| `kind` | calculation / classification / timing / interpretation / manual_input / lookup / orchestration |
| `dependencies` | Technique IDs required first |
| `safety_level` | normal / restricted / research_only / prohibited_user_facing |
| `expert_approval_required` | boolean |
| `status` | See status workflow |
| `primary_sources` | Source register references |
| `variants` | Documented disagreements |
| `test_refs` | Linked automated/expert tests |
| `notes` | Scope decisions and limitations |

---

## 10. Database Plan in Simple Language

The database is the memory of the backend. It should store both stable knowledge and every generated calculation, so a result can be reproduced after rules change.

- **Reference data:** Planets, signs, nakshatras, lords, dignities, standard mappings, locations and time-zone references.
- **Source knowledge:** Books, chapters, quotations/notes, variants, reviewer decisions and usage permissions.
- **Technique and rule library:** Techniques, child rules, conditions, exceptions, outputs, versions and status.
- **Chart input:** Birth/question/event data, uncertainty, location and privacy status.
- **Calculation snapshots:** Planetary positions, cusps, vargas, panchanga, dashas and exact configuration/version.
- **Engine results:** Matched rules, failed conditions, scores, evidence and conflicts.
- **Verification:** Test cases, expected values, actual values, pass/fail and comparison reports.
- **Expert review:** Reviewer comments, approvals, rejection reasons and resolution history.
- **Audit and operations:** Who changed what, when it changed, errors, performance and release manifests.

**Database rule:** Never overwrite an approved historical rule or calculation snapshot. Create a new version so old predictions remain reproducible.

---

## 11. Validation and Testing Plan

> **Gap note (paste incomplete):** Expand detailed matrices in Phase 21. Current minimum:

- Unit tests for every calculation/rule unit.
- Boundary tests at degree/time/sign/nakshatra/cusp/sublord/dasha/sunrise edges.
- Integration tests for chart-to-engine flows.
- Golden chart library with locked expected outputs.
- Regression after every shared change.
- Expert review for interpretive rules.
- Never alter expected values only to silence a failing implementation.

---

## 12. Internal Testing UI: What It Must Show

Birth/event/question input and exact configuration used; raw UTC/JD/location/TZ; planetary longitudes/speeds/retrograde/ephemeris version; Ascendant/houses/cusps/Rasi/Bhava Chalit/Vargas; nakshatra/pada/star/sub/sub-sub; dashas with timestamps; Ashtakavarga components; panchanga/hourly windows; engine selector; matched/failed rules with sources; KP/Nadi evidence chains; side-by-side comparison; test summary and expert approval controls; exportable verification report.

**Do not build now:** consumer dashboard, prediction cards, subscriptions, gamification, notifications, final remedies UI or marketing content.

---

## 13. How to Use ChatGPT/Codex Without Creating a Confused Codebase

- One repository only.
- Keep master requirements, Technique Registry and architecture decisions inside the repository.
- One bounded task at a time.
- Each task begins by reading approved project documents and existing code.
- Spec → implement → test → report.
- Explicit in-scope / out-of-scope, acceptance criteria and required tests.
- Do not accept “completed” without test results and changed-files summary.
- Checkpoint after approval before next task.
- Separate implementation and review tasks.
- No silent method replacements or invented rules (`Source Needed` instead).
- Full regression after kernel/data-model/shared-rule changes.
- Keep customer-language generation disabled until structured evidence is validated.

**Best pattern:** Read → Explain current state → Propose small change → Update specification → Implement → Add tests → Run tests → Show evidence → Wait for human approval.

---

## 14. AI Prompt Sequence for the Entire Programme

> **Gap note (paste incomplete):** Full prompt pack not supplied. Use `docs/prompts/` starting with P00 and P02.

Order rule: do not paste all prompts at once. Create each prompt only after the previous task passes its approval gate.

---

## 15. Standard Acceptance Checklist for Every AI Task

- [ ] The task references the correct requirement and Technique Registry IDs.
- [ ] The AI has not changed unrelated modules.
- [ ] The selected astrology source and variant are documented.
- [ ] Inputs, outputs, units and error states are defined.
- [ ] Positive, negative and boundary tests were added.
- [ ] All new and existing tests pass.
- [ ] The result is traceable to calculation and rule versions.
- [ ] The AI provided a changed-files summary and known limitations.
- [ ] No final user-facing narrative or UI was added unless explicitly requested.
- [ ] Human or expert review is recorded before the status becomes Approved.

---

## 16. Definition of “Backend Complete”

- [ ] All 96 top-level techniques exist in the registry and have approved scope decisions.
- [ ] Every implemented technique has an approved source or explicit product rule.
- [ ] Every broad technique has been decomposed into testable child calculations and rules.
- [ ] All objective calculation modules pass golden and boundary tests.
- [ ] Each astrology school can run independently.
- [ ] Conflicting schools are not silently blended.
- [ ] Every result contains rule evidence, source, configuration and version.
- [ ] Birth-time and source uncertainty are represented in the output.
- [ ] Manual/non-algorithmic systems are correctly gated and labelled.
- [ ] Restricted medical, financial and longevity outputs follow safety and legal review requirements.
- [ ] The internal verification console can inspect every major calculation and rule chain.
- [ ] Critical expert discrepancies are resolved or recorded as known limitations.
- [ ] Full regression tests pass on the frozen release candidate.
- [ ] The backend APIs are stable enough that frontend work will not require rewriting astrology logic.

---

## 17. Realistic Programme Size, Team and Timeline

This is not a normal small app backend. Implementing and validating all 96 top-level techniques is a large knowledge-engineering programme. AI can speed up documentation, implementation and testing, but it cannot remove the need for architecture review, source decisions and astrologer validation.

### Minimum roles

- **Product owner:** scope, priorities, approvals and final product decisions.
- **Technical architect/lead developer:** architecture, database, security, licensing, AI-generated changes and deployment.
- **Astrology domain reviewers:** at least one qualified reviewer per major tradition.
- **Quality/test owner:** golden charts, regression, discrepancies and release gates.
- **Privacy/security/legal reviewer:** birth-data handling, licensing, public claims and restricted modules.
- **AI agents:** bounded research, coding, testing, review and documentation under project rules.

> **Gap note:** Numeric calendar estimates from the source paste were incomplete. Prefer technical sequencing by phase/wave over calendar forecasts.

Do not wait until all engines are finished to begin testing. Testing and expert review must run continuously after every engine batch. The final customer frontend can wait; verification cannot.

---

## 18. Main Risks and How This Plan Prevents Them

> **Gap note (paste incomplete):** Provisional risk register:

| Risk | Prevention in this plan |
|---|---|
| AI invents astrology rules | Source library + Source Needed stop condition |
| Schools silently blended | Independent engines + conflict orchestration |
| Wrong ephemeris/kernel | Golden tests before interpretive engines |
| Silent rule drift | Versioned rules + reproducible snapshots |
| “Complete” without tests | Status workflow requires Auto-Tested / Expert-Checked |
| Unsafe claims | Safety levels + restricted modules |
| Premature frontend | Explicit out-of-scope until Phase 24 gate |
| Swiss Ephemeris license breach | License decision required before public activation |
| Missing technique inventory | Phase 1 blocked until 96-item list is supplied |

---

## 19. The Exact First Action

Do not ask AI to build the backend calculation engines yet. The first implementation task is **P00**: create the project charter, permanent AI instructions, repository structure and controlled status workflow. The second is **P02**: create the live Technique Registry and enter all 96 techniques.

1. Save this requirements document inside the project repository as the controlling plan.
2. Create P00 as a detailed prompt and run only that task.
3. Review the created folders and project instructions.
4. Create P02 and build the Technique Registry.
5. Confirm all 96 rows and begin decomposition by layer.
6. Only after Phases 0–5 are approved should calculation implementation start.

---

## 20. External Implementation Notes

- **Swiss Ephemeris:** Dual licensing under AGPL or a professional license. License choice must be resolved before distribution or public activation.
- **AI workflow:** Permanent repository instructions and bounded tasks rather than one huge build prompt.
- **Database auditing:** Preserve historical rule and result versions rather than overwriting approved data.
- **Sources consulted:** Swiss Ephemeris Programmer Documentation; Swiss Ephemeris General and Licensing Information; OpenAI Codex / project instructions with AGENTS.md; PostgreSQL official documentation.

---

## 21. Product and Validation Disclaimer

This document is an engineering and product-planning specification for implementing traditional astrology systems. The 96-item technique scope comes from the supplied inventory and must be validated against chosen source texts and qualified practitioners. Astrology interpretations are not established scientific predictions. Product copy must avoid presenting medical, legal, financial, safety or longevity conclusions as certain facts or professional advice.

This interpretation is for entertainment purposes only.

# BHAVA360 Build Plan Using VedAstro as Reference

**Version:** 0.1  
**Date:** 2 August 2026  
**Status:** Draft for product/architecture review  
**Related:** `BHAVA360-Backend-Requirements-v1.0.md`, `PROJECT-CHARTER.md`, VedAstro (`https://github.com/VedAstro/VedAstro`)

## 1. One-sentence strategy

Use **VedAstro as a calculation reference and optional bootstrap kernel**, but build **Bhava360 as our own controlled backend** with technique registry, source tracing, independent school engines, evidence, tests and an internal verification console — then build the customer app only after backend freeze.

## 2. What VedAstro gives us

VedAstro is a mature open-source Vedic astrology stack (MIT, mainly C# / .NET, Swiss Ephemeris based), with:

| Asset | Useful for Bhava360? |
|---|---|
| `VedAstro.Library` (NuGet) / Python `VedAstro` | Fast bootstrap for longitudes, houses, vargas, shadbala, dasha, ashtakavarga-style calcs |
| REST API + Docker image | Spike tests, golden-chart comparison, local reference server |
| Open calculation source under `Library/Logic/Calculate/` | Learn formulas; compare outputs; do **not** copy blindly into production rules |
| Website features (horoscope, match, horary, panchang, life predictor, AI chat) | Product inspiration only — not our architecture |
| MCP / AI chat layers | Later explanation layer only; never the calculation authority |
| HuggingFace datasets | Optional research / back-test material |

### What VedAstro is **not**

- Not a multi-school evidence/orchestration system (Parashara / KP / Jaimini / Nadi kept isolated with conflict policy)
- Not source-versioned rule governance with expert freeze gates
- Not our product UX, branding, subscriptions or safety policy
- Not a substitute for the 96-technique registry and approved sources
- Their “gonzo” development style conflicts with Bhava360’s gated programme — we do **not** copy that process

## 3. Build posture (locked)

```text
VedAstro / Swiss Ephemeris  →  raw astronomy + derived chart facts
Bhava360 engines            →  school rules, timing, evidence, conflicts
Internal console            →  verify truth
Customer app (later)        →  consume stable APIs only
LLM (later)                 →  explain approved evidence only
```

**Rules:**

1. Deterministic engines decide; LLM never invents positions or verdicts.
2. Schools stay independent.
3. Every result is traceable (technique ID, rule ID, source, config, engine version).
4. No customer frontend until backend freeze (Phase 24 gate).
5. Jaimini ≠ Gemini.

## 4. Three technical options

| Option | Approach | When to choose |
|---|---|---|
| **A — Reference only** | Call Swiss Ephemeris ourselves; use VedAstro outputs only as comparison oracles in tests | Best long-term control, license clarity, school purity |
| **B — Bootstrap wrapper** | Temporarily wrap VedAstro.Library / API for kernel + chart construction; replace module-by-module | Fastest path to verification console |
| **C — Hybrid (recommended)** | Phase 0–5 docs first; spike A vs B; adopt **direct Swiss Ephemeris kernel** as target, use VedAstro as **golden comparator** and formula reference during Phases 6–8 | Balance speed and control |

**Recommended default: Option C.**

Swiss Ephemeris dual license (AGPL vs commercial) must be decided in Phase 3 before any public API/service.

## 5. End product shape (what we are building)

### Now (backend programme)

1. Calculation kernel (astronomy, timezone, ayanamsa, houses)
2. Chart construction (rasi, bhava, nakshatra, vargas, dignities)
3. Strength / classification foundations
4. Dasha / transit / daily timing platforms
5. Independent engines: Parashara, KP, Jaimini, Nadi (codable), Ashtakavarga, Prashna, Tajika, Lal Kitab, etc.
6. Evidence + conflict orchestration
7. Automated golden/boundary tests
8. Internal verification console (not consumer UI)

### Later (customer Vedic astrology app)

Only after backend freeze:

- Onboarding + birth data capture (privacy-first)
- Chart views and school-specific reports
- Daily/hourly guidance from approved timing engines
- Optional LLM narrative bound to evidence IDs
- Auth, billing, notifications — outside astrology logic

## 6. Dependency-ordered delivery waves

### Wave 0 — Control plane (current)

**Goal:** One repo, one process, no random coding.

- [x] Charter, `AGENTS.md`, folders, status workflow
- [ ] Supply complete **96-technique inventory**
- [ ] Technique Registry v1 + dependency map (P02)
- [ ] Source Register process + first approved sources
- [ ] Architecture ADR: runtime language, SE license, VedAstro usage decision (A/B/C)
- [ ] Canonical data model + privacy classification
- [ ] Rule specification standard + 3 sample rules

**Exit gate:** Phases 0–5 approved. No interpretive engine coding before this.

### Wave 1 — Kernel + chart (use VedAstro as comparator)

**Goal:** Trustworthy positions and chart structures.

1. Timezone / DST / Julian day / location validation
2. Swiss Ephemeris integration (or temporary VedAstro wrapper if ADR allows)
3. Sidereal longitudes + approved ayanamsas
4. Houses / cusps / ascendant / MC
5. Nakshatra, pada, star lord; KP sub/sub-sub as config-driven add-on
6. Vargas D1–D60 (D150 gated by birth-time accuracy)
7. Golden chart library: compare Bhava360 vs VedAstro vs one licensed desktop reference where available

**Exit gate:** Tolerances agreed; boundary tests pass; config/version stamped on every snapshot.

### Wave 2 — Strength + timing platform

1. Dignity / benefic-malefic classifications (configurable thresholds)
2. Shadbala / Bhava Bala component outputs (compare with VedAstro where overlapping)
3. Vimshottari full depth; framework for other dashas
4. Transit and daily panchanga / hora windows (location-aware)

**Exit gate:** Continuity of dasha timelines; component totals reconstructible.

### Wave 3 — First school engines (thin vertical slice)

Implement **one thin path end-to-end** before breadth:

1. Parashara: selected yogas/doshas with formation, cancellation, activation
2. KP: separate ayanamsa/house config + significator chain + one domain verdict
3. Ashtakavarga bindu reconstruction + kakshya scorer
4. Evidence objects for every match/fail

**Exit gate:** Internal console can run one chart through these engines and show rule IDs/sources.

### Wave 4 — Expand inventory by dependency

Order (do not parallel-approve):

1. Nakshatra Nadi (approved corpus only)
2. Jaimini (never labelled Gemini)
3. Codable Nadi modules with accuracy gates
4. Annual / Tajika / chakra modules
5. Prashna / horary (manual inputs for Ashtamangala etc.)
6. Lal Kitab and other specialist modules as isolated packages

### Wave 5 — Orchestration, freeze, customer app

1. Conflict policy + scoring configuration
2. Full regression + expert review panel
3. Backend freeze + API v1 contract
4. **Then** customer frontend plan (screens consume APIs only)

## 7. How to use VedAstro day-to-day (practical)

### Allowed

- Read their `Calculate/*` logic to understand an algorithm candidate
- Run VedAstro API/Docker to produce **reference JSON** for golden tests
- Diff Bhava360 vs VedAstro for objective facts (longitude, sign, nakshatra, varga, dasha lord)
- Document disagreements as variants or bugs — never silently average them

### Not allowed

- Treating VedAstro prose/AI chat as an astrology **source**
- Copying prediction text into user-facing claims without our rule IDs
- Letting their combined “life predictor” replace our independent engines
- Skipping Source Register because “VedAstro already does it”
- Importing their whole website stack as Bhava360

### Suggested adapter boundary

```text
IAstronomyProvider  → Swiss Ephemeris (target) | VedAstroAdapter (optional bootstrap)
IChartBuilder       → Bhava360 only
ISchoolEngine       → ParasharaEngine | KPEngine | JaiminiEngine | ...
IEvidenceStore      → versioned snapshots + rule hits
```

VedAstro may implement `IAstronomyProvider` temporarily; it must not implement school engines.

## 8. Customer app plan (after backend freeze only)

When APIs are stable:

1. **App shell** — auth, profile, privacy/delete birth data
2. **Chart studio** — D1 + selected vargas, configurable ayanamsa/house system
3. **Timing** — dasha timeline + today’s windows
4. **Reports** — school selector (Parashara / KP / …), evidence drawer for power users
5. **Match / muhurta / prashna** — only for engines that passed freeze
6. **Explain** — LLM summarises linked evidence IDs; cannot add new claims

Until freeze, the only UI is the **internal verification console**.

## 9. Team and ownership (minimum)

| Role | Owns |
|---|---|
| Product owner | Scope, 96-inventory, wave priority, freeze |
| Tech lead | ADR, SE license, VedAstro usage boundary, security |
| Domain reviewers | Per-school source/variant approval |
| Quality owner | Golden charts, VedAstro comparison reports, regression |
| AI agents | Bounded tasks under `AGENTS.md` |

## 10. Immediate next actions (this week)

1. **Human:** paste/supply the full **96-technique table** into the registry process.
2. **P02:** build Technique Registry v1 + mark which items VedAstro can help validate.
3. **ADR-001:** decide Option A/B/C and primary runtime (.NET vs Python vs other).
4. **ADR-002:** Swiss Ephemeris license path before any public deployment plan.
5. **Spike (time-boxed):** run VedAstro Docker/API on 5 known charts; store outputs as candidate golden fixtures (not production truth until reviewed).
6. Continue Phases 2–5 docs; **no school-engine coding yet**.

## 11. Success definition

We have built the Vedic astrology app correctly when:

- Objective calculations match approved references within tolerance (VedAstro is one comparator, not the only authority)
- Each school engine is independently runnable and source-traced
- Conflicts are visible, not blended
- Internal console can prove why a result fired
- Customer app never recalculates astrology logic locally in a divergent way
- Restricted medical/financial/longevity claims remain gated

## 12. Disclaimer

This is an engineering plan for traditional astrology software. Astrology is not established scientific prediction. Product copy must not present medical, legal, financial, safety or longevity conclusions as certain professional advice.

This interpretation is for entertainment purposes only.

# Timing Platform — Vimshottari (P09 v0.4)

**Module:** `bhava360.timing.vimshottari`  
**Technique:** TEC-029 (partial — Vimshottari implemented; other dashas later)

## In scope

- Birth balance from Moon nakshatra (elapsed/remaining fraction)
- Maha timeline with continuous rotation (no gaps/overlaps)
- Nested Antar / Pratyantar / Sookshma / Prana expansion
- Child periods start from parent lord; durations `parent_years * lord_years / 120`
- Mean year length `365.2425` days (documented; configurable later if needed)
- Continuity assertions
- `ChartConstructor` includes Vimshottari tree by default (`depth=antar`, `years_ahead=120`)

## Out of scope

- Yogini / Kalachakra / conditional dashas / Jaimini rashi dashas
- Activation of yogas from dasha lords (orchestration later)

## Acceptance checks covered by tests

- Nakshatra lord mapping (Aswini→Ketu, Rohini→Moon)
- Full balance at nakshatra start; near-zero at end
- Maha continuity
- Antar spans match parent and sum to parent duration
- Tree depth through Pratyantar

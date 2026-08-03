# Numerology — mantra-shastra thin slice (P21a)

**Module:** `bhava360.engines.numerology`  
**Engine:** `Numerology` `0.1.0-mantra-shastra`  
**Status:** Candidate  
**Technique:** TEC-092

## Scope

Deterministic number profile from civil birth date (+ optional Latin name):

| Field | Rule |
|-------|------|
| Birth number | Day of month reduced to 1–9 |
| Destiny number | Day + month + year reduced to 1–9 |
| Name number | Chaldean letter values, reduced to 1–9 (optional; never fabricated) |
| Ruling planet | Candidate map 1–9 → Sun…Mars |

Alignment flags: `birth_destiny_aligned`, and when name present `name_birth_aligned` / `name_destiny_aligned`.

Stamp: `numerology_mantra_shastra_candidate_v1`

## Safety

Numeric profile for verification only — not medical, financial, legal, remedial, or longevity advice.

## Deferred

- Master/compound retention
- Life-aspect score packs
- Pythagorean alphabet
- Name-change / mantra remedies

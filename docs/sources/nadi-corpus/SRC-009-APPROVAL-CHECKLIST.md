# SRC-009 Nakshatra Nadi Corpus Approval Checklist

Interpretive Nakshatra Nadi chains (TEC-054/TEC-055) stay **blocked** until this checklist is completed and the machine gate is flipped under review.

## Allowed without corpus

- Planet-in-star / pada facts derived from the chart kernel (`planet_in_star` in the P13 scaffold)

## Blocked without corpus

- Supporting / blocking / mixed chain evaluation
- Event trigger packs
- Any Nadi verdict language

## Required evidence

- [ ] Named corpus / course edition with stable `corpus_id`
- [ ] Rule inventory mapped to TEC-054 / TEC-055
- [ ] Depth / stop-condition policy documented
- [ ] Domain reviewer Approved status in Source Register (`SRC-009`)
- [ ] Versioned rule pack artefact path recorded (no invented rules in code)
- [ ] Explicit exclusion of palm-leaf manuscript recreation claims (TEC-065)

## Unlock procedure

1. Complete this checklist and update `sources/registers/SOURCE-REGISTER.md` (`SRC-009` → Approved).
2. Flip `src/bhava360/engines/nadi/nakshatra_nadi_corpus_status.json` under review:
   - `corpus_status`: `"approved"`
   - `corpus_id`, `approval_status=Approved`, `approved_by`, `approved_at`
3. Load the versioned rule pack before enabling chain evaluation (engine still refuses empty packs).

## Gate code

- `bhava360.engines.nadi.assert_nadi_corpus_approved`
- Error: `CORPUS_GATE_BLOCKED`

# Ashtakavarga Thin Slice (P12a + P12b)

**Module:** `bhava360.engines.ashtakavarga`  
**Techniques:** TEC-048, TEC-049, TEC-051, TEC-052, TEC-053 (partial)

## In scope

### P12a
- Bhinnashtakavarga for Sun–Saturn with per-bindu contributor audit trail
- Sarvashtakavarga as sum of seven BAVs (classical total **337**)
- Reconstruction check: totals rebuild from contribution rows
- Kakshya labelling (8 × 3°45′) for natal planet degrees
- Natal sign scores (SAV/BAV of occupied sign + kakshya)

### P12b
- **Trikona Shodhana** (I Reduction) with Raman-style rules a–d
- **Ekadhipatya Shodhana** (II Reduction) driven by natal occupation of dual-lordship pairs
- **Mandala Shodhana** for SAV only (expunge multiples of 12; leave 12 on exact multiples)
- **Sodhya Pinda** = Rasi Pinda + Graha Pinda (gunakara tables stamped)
- Full before/after audit steps on every reduction

## Out of scope

- Prastara Ashtakavarga
- Full kakshya transit scorer / daily prediction claims
- Longevity/ayurdaya year conversion from Sodhya Pinda
- Rekha Sarvashtakavarga reductions (deferred)

## Variants

| Key | Value | Notes |
|---|---|---|
| `table_variant` | `standard_candidate_v1` | Raw BAV house tables |
| `shodhana_variant` | `raman_candidate_v1` | B.V. Raman computational sequence; Candidate |

Occupation for Ekadhipatya counts the seven BAV planets only (Rahu/Ketu excluded) in this Candidate rule.

## Source note

Bindu house tables and shodhana edge rules are Candidate pending Approved classical edition citation. VedAstro documentation may be used as comparator only.

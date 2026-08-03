# Ashtakavarga (P12a + P12b + P12c)

**Module:** `bhava360.engines.ashtakavarga`  
**Techniques:** TEC-048, TEC-049, TEC-050, TEC-051, TEC-052, TEC-053 (partial)  
**Engine version:** `0.3.0-prastara`

## In scope

### P12a
- Bhinnashtakavarga for Sun–Saturn with per-bindu contributor audit trail
- Sarvashtakavarga as sum of seven BAVs (classical total **337**)
- Reconstruction check: totals rebuild from contribution rows
- Kakshya labelling (8 × 3°45′) for natal planet degrees
- Natal sign scores (SAV/BAV of occupied sign + kakshya)

### P12b
- Trikona / Ekadhipatya Shodhana (+ SAV Mandala)
- Sodhya Pinda (Rasi + Graha gunakara)

### P12c
- **Prastara Ashtakavarga**: 8×12 binary grids per BAV in kakshya-lord order
- Column sums reconstruct BAV sign bindus
- Natal `kakshya_lord_bindu` flag from Prastara cell at occupied degree

## Out of scope

- Full day-by-day transit kakshya scorer / prediction claims
- Longevity/ayurdaya conversion from Sodhya Pinda
- Rekha Sarvashtakavarga reductions

## Variants

| Key | Value |
|---|---|
| `table_variant` | `standard_candidate_v1` |
| `shodhana_variant` / `prastara_variant` | `raman_candidate_v1` |

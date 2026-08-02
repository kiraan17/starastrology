# Shadbala partial pack (P27b–P31b)

**Module:** `bhava360.engines.shadbala`  
**Engine:** `Shadbala` `0.7.0-sphuta-drik`  
**Status:** Candidate  
**Technique:** TEC-023  
**Stamp:** `shadbala_sphuta_drik_candidate_v1`

## In scope (Virupa)

| Family | Included |
|--------|----------|
| Naisargika | Fixed 60×(7..1)/7 |
| Dig | Whole-sign dig-house distance |
| Sthana | Uchcha + Kendradi + Ojayugma(rasi+navamsa) + Saptavargaja + Drekkana |
| Kala | Natonnata + Paksha + Tribhaga + Abda/Masa/Vara/Hora + Ayana + Yuddha |
| Chesta | Sun=Ayana; Moon=Paksha; Mars–Saturn Saravali 8-fold speed bands |
| Drik | Sphuta continuous degree-Drishti + 1.25/0.75; classical table fallback |

### Drik (Sphuta)

Angle `a` = forward zodiacal distance from aspector to aspected.

- General Saravali piecewise table (0–60 virupa)
- General 150–180 uses `2*(a-150)` so opposition = 60 (Candidate table-print fix)
- Mars / Jupiter / Saturn special columns override general when present
- Benefic aspectors ×1.25 (add); malefic ×0.75 (subtract)
- Moon benefic in bright half; Mercury malefic if same-sign with Sun/Mars/Saturn
- If longitudes missing: whole-sign classical Graha table (7=60; 4/8=45 Mars60; 5/9=30 Jupiter60; 3/10=15 Saturn60)

## Out of scope

- Seeghra-kendra Chesta
- Abda/Masa Hora lord at exact sankranti
- Saptavargaja temporal / Adhi-mitra / Adhi-satru
- Full-pack minimum threshold verdicts

## Safety

Strength metrics for verification only — not predictive advice.

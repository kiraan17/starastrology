# Shadbala partial pack (P27b–P32a)

**Module:** `bhava360.engines.shadbala`  
**Engine:** `Shadbala` `0.8.0-abda-masa-hora`  
**Status:** Candidate  
**Technique:** TEC-023  
**Stamp:** `shadbala_abda_masa_hora_candidate_v1`

## In scope (Virupa)

| Family | Included |
|--------|----------|
| Naisargika | Fixed 60×(7..1)/7 |
| Dig | Whole-sign dig-house distance |
| Sthana | Uchcha + Kendradi + Ojayugma(rasi+navamsa) + Saptavargaja + Drekkana |
| Kala | Natonnata + Paksha + Tribhaga + Abda/Masa (Hora-at-sankranti) + Vara/Hora + Ayana + Yuddha |
| Chesta | Sun=Ayana; Moon=Paksha; Mars–Saturn Saravali 8-fold speed bands |
| Drik | Sphuta continuous degree-Drishti + 1.25/0.75; classical table fallback |

### Abda / Masa (Hora at sankranti)

- Sankranti instant ≈ birth − Δλ / mean sidereal solar motion (`0.98564733 °/day`)
- Abda: Hora lord at Mesha (0°) sankranti → 15 virupa
- Masa: Hora lord at current-rasi ingress sankranti → 30 virupa
- Birth-day sunrise/sunset clocks shifted onto sankranti civil date (Candidate)
- Vara-lord fallback if day window missing

### Drik (Sphuta)

Angle `a` = forward zodiacal distance from aspector to aspected.

- General Saravali piecewise table (0–60 virupa)
- General 150–180 uses `2*(a-150)` so opposition = 60 (Candidate table-print fix)
- Mars / Jupiter / Saturn special columns override general when present
- Benefic aspectors ×1.25 (add); malefic ×0.75 (subtract)
- If longitudes missing: whole-sign classical Graha table

## Out of scope

- Seeghra-kendra Chesta
- Exact ephemeris sunrise for the sankranti day
- Saptavargaja temporal / Adhi-mitra / Adhi-satru
- Full-pack minimum threshold verdicts

## Safety

Strength metrics for verification only — not predictive advice.

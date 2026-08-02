# Shadbala partial pack (P27b–P30b)

**Module:** `bhava360.engines.shadbala`  
**Engine:** `Shadbala` `0.5.0-chesta-motion`  
**Status:** Candidate  
**Technique:** TEC-023  
**Stamp:** `shadbala_chesta_motion_candidate_v1`

## In scope (Virupa)

| Family | Included |
|--------|----------|
| Naisargika | Fixed 60×(7..1)/7 |
| Dig | Whole-sign dig-house distance |
| Sthana | Uchcha + Kendradi + Ojayugma(rasi+navamsa) + Saptavargaja + Drekkana |
| Kala | Natonnata + Paksha + Tribhaga + Abda/Masa/Vara/Hora + Ayana + Yuddha |
| Chesta | Sun=Ayana; Moon=Paksha; Mars–Saturn Saravali 8-fold speed bands |
| Drik thin | Whole-sign graha aspect net, ±60 clamp |

### Chesta motion bands (Saravali)

| Motion | Virupa | Rule |
|--------|--------|------|
| Vakra | 60 | speed &lt; 0 |
| Anuvakra | 30 | retrograde + sign_degree &lt; 1° |
| Vikala | 15 | speed &lt; 10% of mean |
| Mandatara | 15 | 10–50% of mean |
| Manda | 30 | 50–100% of mean |
| Sama | 7.5 | 100–150% of mean |
| Chara | 45 | &gt; 150% of mean |
| Atichara | 30 | Chara + sign_degree ≥ 29° |

## Out of scope

- Seeghra-kendra Chesta (BPHS mean/true formula)
- Abda/Masa Hora lord at exact sankranti
- Saptavargaja temporal / Adhi-mitra / Adhi-satru
- Classical Drik strength tables
- Full-pack minimum threshold verdicts

## Safety

Strength metrics for verification only — not predictive advice.

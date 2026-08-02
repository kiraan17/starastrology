# Shadbala partial pack (P27b / P28a / P29b / P30a)

**Module:** `bhava360.engines.shadbala`  
**Engine:** `Shadbala` `0.4.0-kala-remainder`  
**Status:** Candidate  
**Technique:** TEC-023  
**Stamp:** `shadbala_kala_remainder_candidate_v1`

## In scope (Virupa)

| Family | Included |
|--------|----------|
| Naisargika | Fixed 60×(7..1)/7 |
| Dig | Whole-sign dig-house distance |
| Sthana | Uchcha + Kendradi + Ojayugma(rasi+navamsa) + Saptavargaja + Drekkana |
| Kala | Natonnata + Paksha + Tribhaga + Abda(15) + Masa(30) + Vara(45) + Hora(60) + Ayana + Yuddha |
| Chesta thin | Retrograde→60 else 15 for Mars–Saturn; Sun/Moon Ayana deferred (0) |
| Drik thin | Whole-sign graha aspect net, ±60 clamp |

### Kala notes (Candidate)

- **Tribhaga:** day Mercury/Sun/Saturn; night Moon/Venus/Mars; Jupiter always 60
- **Abda/Masa:** sankranti-weekday approximation (classical Hora-at-sankranti deferred)
- **Ayana:** length-based `30×(1±|sin(tropical_lon)|)` (Saravali)
- **Yuddha:** Mars–Saturn within 1°; redistribute pre-Ayana Kala difference

## Out of scope

- Abda/Masa Hora lord at exact sankranti instant
- Saptavargaja temporal / Adhi-mitra / Adhi-satru
- Chesta seeghra kendra + luminous Ayana Chesta
- Classical Drik strength tables
- Full-pack minimum threshold verdicts

## Safety

Strength metrics for verification only — not predictive advice.

# Shadbala partial pack (P27b–P32b)

**Module:** `bhava360.engines.shadbala`  
**Engine:** `Shadbala` `0.9.0-seeghra-chesta`  
**Status:** Candidate  
**Technique:** TEC-023  
**Stamp:** `shadbala_seeghra_chesta_candidate_v1`

## In scope (Virupa)

| Family | Included |
|--------|----------|
| Naisargika | Fixed 60×(7..1)/7 |
| Dig | Whole-sign dig-house distance |
| Sthana | Uchcha + Kendradi + Ojayugma(rasi+navamsa) + Saptavargaja + Drekkana |
| Kala | Natonnata + Paksha + Tribhaga + Abda/Masa (Hora-at-sankranti) + Vara/Hora + Ayana + Yuddha |
| Chesta | Sun=Ayana; Moon=Paksha; Mars–Saturn Seeghra-kendra (BPHS); Saravali fallback |
| Drik | Sphuta continuous degree-Drishti + 1.25/0.75; classical table fallback |

### Chesta (Seeghra kendra)

BPHS: `CK = Seeghrochcha − (Mean + True)/2`; if CK>180 use `360−CK`; Bala = CK/3 (0–60).

| Planet | Mean | Seeghrochcha |
|--------|------|--------------|
| Mars, Jupiter, Saturn | SE osculating mean LM (sidereal) | Mean Sun (Earth LM + 180°) |
| Mercury, Venus | Mean Sun | Heliocentric mean LM (Candidate table proxy) |
| Sun / Moon | — | Ayana / Paksha (unchanged) |

Saravali 8-fold speed bands remain as fallback when JD/means unavailable.

### Abda / Masa (Hora at sankranti)

- Sankranti instant ≈ birth − Δλ / mean sidereal solar motion
- Abda/Masa = planetary Hora lord at Mesha / current-rasi ingress

### Drik (Sphuta)

- Continuous degree-Drishti + 1.25/0.75; classical table fallback if longitudes missing

## Out of scope

- Mercury/Venus classical Seeghrochcha product tables
- Exact ephemeris sunrise for the sankranti day
- Saptavargaja temporal / Adhi-mitra / Adhi-satru
- Full-pack minimum threshold verdicts

## Safety

Strength metrics for verification only — not predictive advice.

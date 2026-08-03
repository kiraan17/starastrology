# Shadbala partial pack (P27b–P33a)

**Module:** `bhava360.engines.shadbala`  
**Engine:** `Shadbala` `0.10.0-adhi-mitra`  
**Status:** Candidate  
**Technique:** TEC-023  
**Stamp:** `shadbala_adhi_mitra_candidate_v1`

## In scope (Virupa)

| Family | Included |
|--------|----------|
| Naisargika | Fixed 60×(7..1)/7 |
| Dig | Whole-sign dig-house distance |
| Sthana | Uchcha + Kendradi + Ojayugma + Saptavargaja (Panchadha) + Drekkana |
| Kala | Natonnata + Paksha + Tribhaga + Abda/Masa (Hora-at-sankranti) + Vara/Hora + Ayana + Yuddha |
| Chesta | Sun=Ayana; Moon=Paksha; Mars–Saturn Seeghra-kendra; Saravali fallback |
| Drik | Sphuta continuous degree-Drishti + 1.25/0.75; classical table fallback |

### Saptavargaja (Panchadha)

Compound friendship = permanent × temporary (D1 houses 2/3/4/10/11/12 = temp friend).

| Basis | Virupa (BPHS Santhanam) |
|-------|-------------------------|
| Moolatrikona (D1 only) | 45 |
| Own | 30 |
| Adhi-mitra | 20 |
| Friend | 15 |
| Neutral | 10 |
| Enemy | 4 |
| Adhi-satru | 2 |

| Permanent | Temporary | Compound |
|-----------|-----------|----------|
| friend | friend | adhi_mitra |
| enemy | enemy | adhi_satru |
| friend | enemy | neutral |
| enemy | friend | neutral |
| neutral | friend | friend |
| neutral | enemy | enemy |

### Chesta / Abda-Masa / Drik

Unchanged from P32b / P32a / P31b (see prior release notes).

## Out of scope

- Mercury/Venus classical Seeghrochcha product tables
- Exact ephemeris sunrise for the sankranti day
- Full-pack minimum threshold verdicts
- Alternate Raman half-virupa table (22.5 / 7.5 / 3.75 / 1.875)

## Safety

Strength metrics for verification only — not predictive advice.

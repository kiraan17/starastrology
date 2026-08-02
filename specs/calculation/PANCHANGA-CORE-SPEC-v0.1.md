# Panchanga + Muhurta (P16a + P16b)

**Modules:** `bhava360.timing.panchanga`, `bhava360.timing.muhurta`, `run_panchanga_engine`  
**Techniques:** TEC-070, TEC-071, TEC-073  
**Engine version:** `0.2.0-muhurta`

## In scope

### P16a
- Tithi / Vara / Nakshatra / Yoga / Karana
- Vara from local sunrise weekday

### P16b
- Rahu Kala, Yamaganda, Gulika (daytime eighth tables by weekday)
- Abhijit (midday-centered, duration = daytime/15)
- Planetary Hora (12 day + 12 night)
- Chaughadiya (8 day + 8 night)
- Active flags at subject instant

## Out of scope

- Night Gulika tables
- Tara / Chandra Bala (TEC-072)
- Panchaka / Bhadra / Panchapakshi / activity windows (TEC-074..076)

## Variants

`sidereal_lahiri_candidate_v1` (limbs), `classical_segments_candidate_v1` (muhurta)

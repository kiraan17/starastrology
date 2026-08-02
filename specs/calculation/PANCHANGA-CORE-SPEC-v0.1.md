# Panchanga Core (P16a v0.1)

**Module:** `bhava360.timing.panchanga` / `run_panchanga_engine`  
**Technique:** TEC-070  
**Variant:** `sidereal_lahiri_candidate_v1`

## In scope

- Tithi (30) from Moon−Sun elongation
- Karana (60) from half-tithi elongation
- Yoga (27) from Sun+Moon sum (sidereal Candidate)
- Nakshatra + pada of Moon
- Vara from weekday of local **sunrise** instant
- Console `panchanga` engine checkbox

## Out of scope

- Rahu Kala / Yamaganda / Gulika / Abhijit (TEC-071)
- Tara/Chandra Bala (TEC-072)
- Hora / Chaughadiya (TEC-073)
- Panchaka / Bhadra / Panchapakshi (TEC-074..075)
- Activity good/mixed/avoid windows (TEC-076)
- End-time of each limb (next transition search)

## Notes

Elongation-based limbs are ayanamsa-invariant. Yoga uses sidereal sum and is stamped Candidate.

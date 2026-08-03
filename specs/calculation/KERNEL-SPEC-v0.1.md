# Calculation Kernel Specification (P07 v0.2)

**Status:** Implemented  
**Techniques:** TEC-001 (partial), TEC-003, TEC-005, TEC-006, TEC-007 (partial), TEC-008, TEC-009, TEC-010, TEC-013  
**Provider:** `SwissEphemerisProvider` via `pyswisseph`  
**Default mode:** Moshier + Lahiri + mean node + whole_sign houses

## In scope

### v0.1
- Fixed-offset local → UTC → Julian Day UT
- Sidereal planetary longitudes for Sun–Saturn, Rahu, Ketu
- Speed / retrograde flag
- Sign + VedAstro-spelling nakshatra/pada labels
- Immutable snapshot stamp with config + library versions
- Structured kernel errors

### v0.2 (P07b)
- Ascendant and Midheaven (sidereal)
- House cusps:
  - **whole_sign** — Vedic whole-sign from Asc sign (computed locally; not SE `W`)
  - **placidus** — Swiss Ephemeris Placidus (for KP path)
- Planet-to-house index for either system
- Sunrise / sunset (disc center) for subject local civil date
- Location required for houses/day windows (`INVALID_LOCATION` if missing)
- Snapshot optionally includes `houses` + `day_window` when coordinates present

## Out of scope (next)

- IANA timezone / DST history database
- Sripati / Bhava Chalit cusp variants
- Vargas / KP sublords
- School engines

## Tolerances

| Quantity | Tolerance |
|---|---|
| Sidereal planet longitude vs VedAstro SPIKE-01 | ≤ 0.01° |
| Sign / nakshatra label vs SPIKE-01 | exact |
| Placidus cusp1 vs Asc, cusp10 vs MC | ≤ 1e-6° internal consistency |

## Notes

- SE house system code `W` is **not** used for Vedic whole-sign; Bhava360 computes whole-sign cusps from Asc longitude explicitly.
- Sunrise/sunset are location-dependent; same UT date at different longitudes must differ.

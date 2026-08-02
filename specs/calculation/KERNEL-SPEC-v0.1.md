# Calculation Kernel Specification (P07 v0.1)

**Status:** Implemented scaffold  
**Techniques:** TEC-001 (partial), TEC-003, TEC-005 (mean/true config), TEC-006 (Lahiri/KP modes), TEC-010, TEC-013 (nakshatra/pada labels)  
**Provider:** `SwissEphemerisProvider` via `pyswisseph`  
**Default mode:** Moshier + Lahiri + mean node

## In scope (this release)

- Fixed-offset local → UTC → Julian Day UT
- Sidereal planetary longitudes for Sun–Saturn, Rahu, Ketu
- Speed / retrograde flag
- Sign + VedAstro-spelling nakshatra/pada labels for comparator tests
- Immutable snapshot stamp with config + library versions
- Structured kernel errors

## Out of scope (next kernel tasks)

- IANA timezone / DST history database
- House cusps / Asc / MC
- Vargas
- KP sublord chains
- School engines

## Tolerances (vs VedAstro SPIKE-01)

| Quantity | Tolerance |
|---|---|
| Sidereal longitude | ≤ 0.01° absolute difference |
| Sign name | exact |
| Nakshatra label (`Name - pada`) | exact against SPIKE-01 spellings |

## Error catalogue

| code | when |
|---|---|
| INVALID_DATETIME | bad local datetime / token |
| INVALID_TIMEZONE | offset out of range |
| INVALID_LOCATION | lat/lon out of range |
| UNSUPPORTED_PLANET | unknown planet |
| UNSUPPORTED_CONFIG | bad ephemeris/ayanamsa/node config |
| EPHEMERIS_UNAVAILABLE | reserved for missing SE files |
| CALCULATION_FAILED | SE backend failure |

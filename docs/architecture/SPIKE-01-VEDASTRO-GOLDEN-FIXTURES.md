# SPIKE-01 Report — VedAstro Golden Fixtures

**Date:** 2026-08-02  
**Status:** Complete (comparator fixtures only)  
**Script:** `scripts/spike_vedastro_golden_fixtures.py`  
**Output:** `tests/golden/vedastro-spike/`

## Goal

Prove we can pull objective VedAstro calculation outputs for fixed charts and store them as future Bhava360 kernel comparison fixtures.

## Result

| Chart ID | Location / time | Sun rasi (VedAstro) | Moon nakshatra | Errors |
|---|---|---|---|---|
| chennai_1990_0815_1200 | Chennai 12:00 15/08/1990 +05:30 | Cancer | Rohini - 3 | 0 |
| singapore_2024_0424_0000 | Singapore 00:00 24/04/2024 +08:00 | Aries | Chitta - 4 | 0 |
| london_2000_0101_1200 | London 12:00 01/01/2000 +00:00 | Sagittarius | Swathi - 4 | 0 |
| newyork_1976_0704_1430 | New York 14:30 04/07/1976 -04:00 | Gemini | Hasta - 3 | 0 |
| mumbai_1950_0126_1010 | Mumbai 10:10 26/01/1950 +05:30 | Capricorn | Aswini - 4 | 0 |

Fetched per planet: `PlanetNirayanaLongitude`, `PlanetRasiD1Sign`, `PlanetConstellation`, plus `AllPlanetData` for Sun.

## Limits discovered

- Many calculator names return `Calculator method not found` unless exact API Builder names/params are used.
- Locations with spaces must be URL-encoded.
- House/ayanamsa/dasha endpoints were not reliably discoverable in this spike; follow-up can use API Builder exports.
- Fixtures are **not** approved golden truth until quality review against Bhava360 kernel + second reference.

## Decision impact

Supports ADR-001 Option C: keep VedAstro as HTTP comparator now; do not bind production engines to VedAstro.

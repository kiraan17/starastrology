# Tajika Annual / Sahams / Aspects / Tithi Pravesh (P17a–P17c)

**Module:** `bhava360.engines.tajika`  
**Engine:** `TajikaAnnual` `0.3.0-sahams-aspects`  
**Status:** Candidate  
**Techniques:** TEC-077 (partial), TEC-078 (thin), TEC-079 (thin)

## Scope

### P17a
- Sidereal solar return (Varsha Pravesh) near `target_year` anniversary
- Muntha = natal Lagna sign + completed years (mod 12)
- Year-lord **candidate** = Muntha-sign lord (full Varshesh deferred)
- `annual.location_rule` stamped (VARIANT-002)

### P17b
- Tithi Pravesh: natal Moon−Sun elongation return nearest solar return (±20d)
- Stamp `tithi_pravesh_candidate_v1`

### P17c
- Sahams (5): Punya, Vidya, Yasya, Mitra, Rajya — Asc+A−B with day/night reverse
- Tajika degree aspects with Candidate orbs + applying flag
- Ithasala **candidate** = applying aspect within orb (full yoga suite deferred)
- Stamps: `tajika_saham_candidate_v1`, `tajika_aspects_candidate_v1`
- **SRC-012 edition citation still required** before Approved

## Deferred

- Full Varshesh multi-factor year lord
- Full Saham catalog
- Full Ithasala/Isarpha/Nakta/Kamboola suite
- Month/day charts
- Alternate Tithi Pravesh centering

## Provenance stamps

- `tajika_thin_candidate_v1`
- `tithi_pravesh_candidate_v1`
- `tajika_saham_candidate_v1`
- `tajika_aspects_candidate_v1`

# Tajika Annual / Varshaphala + Tithi Pravesh (P17a–P17b)

**Module:** `bhava360.engines.tajika`  
**Engine:** `TajikaAnnual` `0.2.0-tithi-pravesh`  
**Status:** Candidate  
**Techniques:** TEC-077 (partial), TEC-079 (thin)

## Scope

### P17a
- Sidereal solar return (Varsha Pravesh) near `target_year` anniversary
- Muntha = natal Lagna sign + completed years (mod 12)
- Year-lord **candidate** = Muntha-sign lord (full Varshesh deferred)
- `annual.location_rule` stamped (VARIANT-002): `birth_place` | `residence` | `event_location`

### P17b
- Tithi Pravesh: natal Moon−Sun elongation return nearest the solar-return JD (±20 days)
- Same `annual.location_rule` coordinates as Varsha chart
- Stamp `tithi_pravesh_candidate_v1`

## Deferred

- Full Varshesh multi-factor year lord
- Sahams / Tajika aspects (TEC-078)
- Month/day charts
- Alternate Tithi Pravesh centering (lunar-month-only variants)

## Provenance stamps

- `tajika_thin_candidate_v1`
- `tithi_pravesh_candidate_v1`

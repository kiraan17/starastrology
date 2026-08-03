# Panchaka and Bhadra (P26a)

**Module:** `bhava360.timing.panchaka` / `panchaka_engine`  
**Engine:** `PanchakaBhadra` `0.1.0-panchaka-bhadra`  
**Status:** Candidate  
**Technique:** TEC-074  
**Stamp:** `panchaka_bhadra_candidate_v1`

## Scope

| Output | Rule |
|--------|------|
| Moon Panchak | Sidereal Moon in `[300°, 360°)` (Dhanishta pada 3 → Revathi) |
| Panchaka Rahita | `(tithi + vara + nakshatra + lagna) % 9`; rem 1/2/4/6/8 → Mrityu/Agni/Raja/Chora/Roga |
| Bhadra | Vishti karana active |

Type labels are structural classifiers only.

## Safety

Timing classification for verification — not medical, longevity, or predictive advice.

## Deferred

- Sunrise-to-sunrise lagna-segment Rahita window sweep
- Timed Moon Panchak ingress/egress search
- Full classical activity nibandha mappings

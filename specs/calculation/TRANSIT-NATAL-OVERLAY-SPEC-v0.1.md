# Transit vs natal overlay (P25b)

**Module:** `bhava360.engines.transit`  
**Engine:** `Transit` `0.1.0-natal-overlay`  
**Status:** Candidate  
**Technique:** TEC-035

## Scope

| Output | Rule |
|--------|------|
| Placements | Transit planet sign + whole-sign house from natal Lagna and natal Moon |
| Sign diff | Natal vs transit sign per planet |
| Conjunctions | Transit longitude within orb of natal longitude (default 1°) |
| Aspects | Whole-sign graha aspects from transit → natal planets |

Stamp: `transit_natal_overlay_candidate_v1`

## Safety

Structural overlay for verification only — not gochara advice.

## Deferred

- Ephemeris sweep / next-hit search
- Ashtakavarga transit scoring
- Interpretive gochara packs
- Degree aspect orbs

# Panchapakshi day/night cycles (P26b / P27a)

**Module:** `bhava360.timing.panchapakshi` / `panchapakshi_engine`  
**Engine:** `Panchapakshi` `0.2.0-both-paksha`  
**Status:** Candidate  
**Technique:** TEC-075  
**Stamp:** `panchapakshi_pyjhora_major_candidate_v1`

## Scope

| Output | Rule |
|--------|------|
| Birth bird | PyJHora `pancha_pakshi_stars_birds_paksha` (5/6/5/5/6 by paksha) |
| Yama clock | 5 equal day + 5 equal night segments from local sunrise/sunset |
| Major activities | Both Shukla and Krishna — 70 weekday×paksha×bird schedules from PyJHora CSV majors |

Activity classes: Ruling/Eating → favorable; Walking → mixed; Sleeping/Dying → avoid.

## Provenance

Major tables derived from PyJHora V4.8.7 `pancha_pakshi_db.csv` (AGPL-3.0; Candidate). Sub-period rows not vendored.

## Safety

Timing classification for verification — not predictive advice.

## Deferred

- Sub-yama nested activities and duration weights
- Padu/Bharana companion birds
- Competitive bird-vs-bird verdicts
- Natal-bird + query-time schedule split

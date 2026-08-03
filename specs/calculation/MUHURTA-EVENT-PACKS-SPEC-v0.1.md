# Muhurta Event Rule Packs (P20b)

**Module:** `bhava360.timing.event_rules` / `muhurta_event_engine`  
**Engine:** `MuhurtaEvents` `0.1.0-event-pack`  
**Status:** Candidate  
**Techniques:** TEC-093, TEC-076 (thin)

## Scope

Instant classification for activities:

- `general`, `travel`, `education`, `business_start`, `meeting`

Uses existing Panchanga / Muhurta / Tara facts:

- Avoid pressure: Rahu Kala, Yamaganda, Gulika, Vishti, Vipat/Pratyak/Naidhana
- Support: Abhijit, Amrit/Shubh/Labh Chaughadiya, auspicious Tara, selected horas

Verdicts: `good` | `mixed` | `avoid`

## Safety

Timing classes only — not medical, financial, legal, or longevity advice.

## Deferred

- Full classical nibandha libraries
- Multi-day next-good-slot search
- Full electional chart construction

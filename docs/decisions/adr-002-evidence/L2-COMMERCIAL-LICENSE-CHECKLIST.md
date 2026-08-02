# ADR-002 Path L2 — Commercial SE License Checklist

Default product intent for commercial Bhava360 SaaS (per ADR-002).

## Required evidence

- [ ] Executed Swiss Ephemeris professional/commercial license (or Astrodienst equivalent grant)
- [ ] License scope covers public API / hosted calculation service
- [ ] Licensee legal entity matches deployment operator
- [ ] Renewal / termination calendar recorded
- [ ] Ephemeris file redistribution rights confirmed if shipping SE files
- [ ] Legal reviewer sign-off recorded (name + date)
- [ ] Evidence id assigned (example: `EVID-SE-L2-001`); store grant offline/securely — do not commit secrets

## Not sufficient alone

- Intent to purchase later
- Moshier-only private/dev usage
- Conditional ADR-002 private/dev approval

## Gate fields to set after completion

```json
{
  "public_activation": "allowed",
  "chosen_path": "L2_COMMERCIAL",
  "evidence_ids": ["EVID-SE-L2-001"],
  "approved_by": ["legal:<name>", "product:<name>"],
  "approved_at": "<ISO-8601>"
}
```

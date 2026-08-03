# ADR-002 Path L1 — AGPL Compliance Checklist

Use only if product owner chooses AGPL distribution for Swiss Ephemeris usage.

## Required evidence

- [ ] Written product decision to distribute under AGPL-compatible terms
- [ ] Inventory of SE-using components (`pyswisseph`, ephemeris files, wrappers)
- [ ] Source-offer / corresponding-source process documented for hosted service
- [ ] Network-use / AGPL obligations reviewed for SaaS deployment
- [ ] NOTICE / LICENSE texts present in distribution artefacts
- [ ] Legal reviewer sign-off recorded (name + date)
- [ ] Evidence id assigned (example: `EVID-SE-L1-001`) and linked artefacts stored privately if needed

## Not sufficient alone

- README disclaimer without source-offer process
- Private/dev usage approval from ADR-002 conditional acceptance

## Gate fields to set after completion

```json
{
  "public_activation": "allowed",
  "chosen_path": "L1_AGPL",
  "evidence_ids": ["EVID-SE-L1-001"],
  "approved_by": ["legal:<name>", "product:<name>"],
  "approved_at": "<ISO-8601>"
}
```

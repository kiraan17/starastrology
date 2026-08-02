# Variant Decision Log

Record disagreements here. Do not hide them in code defaults.

## Template

```text
VARIANT-ID:
Technique IDs:
Question:
Option A: (source + summary)
Option B: (source + summary)
Option C: (optional)
Decision: supported option / research_only / deferred
Decided by:
Date:
Engine config key:
Notes:
```

## Entries

### VARIANT-001 — Chara Karaka count

- **Technique IDs:** TEC-028
- **Question:** Use 7-karaka or 8-karaka scheme?
- **Option A:** Seven karakas
- **Option B:** Eight karakas
- **Decision:** deferred — both must be configurable; default unset until expert approval
- **Engine config key:** `jaimini.chara_karaka.scheme`
- **Notes:** Do not hardcode a silent default in production verdicts

### VARIANT-002 — Annual chart location

- **Technique IDs:** TEC-077, TEC-079
- **Question:** Cast annual return for birth place, current residence, or event location?
- **Options:** birth_place / residence / event_location
- **Decision:** deferred — store chosen rule on every annual snapshot
- **Engine config key:** `annual.location_rule`

### VARIANT-003 — Node type for natal charts

- **Technique IDs:** TEC-005
- **Question:** Mean Node vs True Node default?
- **Decision:** deferred — both supported in config; product default TBD
- **Engine config key:** `kernel.node_type`

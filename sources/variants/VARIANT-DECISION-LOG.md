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
- **Notes:** Do not hardcode a silent default in production verdicts. Verification console may pass an explicit `seven` or `eight` for operator convenience; every result stamps the chosen scheme.

### VARIANT-002 — Annual chart location

- **Technique IDs:** TEC-077, TEC-079
- **Question:** Cast annual return for birth place, current residence, or event location?
- **Options:** birth_place / residence / event_location
- **Decision:** deferred — store chosen rule on every annual snapshot (P17a stamps `annual.location_rule`; default `birth_place` for verification)
- **Engine config key:** `annual.location_rule`

### VARIANT-006 — Tajika Saham / aspect Candidate defaults

- **Technique IDs:** TEC-078
- **Question:** Which Saham formula table and Tajika orb set?
- **Decision:** supported Candidate defaults (`tajika_saham_candidate_v1`, `tajika_aspects_candidate_v1`) until SRC-012 edition Approved
- **Engine config keys:** `sahams.variant`, `aspects.variant`
- **Notes:** Five Sahams with day/night reverse; aspects 0/60/90/120/180° with Candidate orbs; Ithasala = applying-within-orb flag only

### VARIANT-003 — Node type for natal charts

- **Technique IDs:** TEC-005
- **Question:** Mean Node vs True Node default?
- **Decision:** deferred — both supported in config; product default TBD
- **Engine config key:** `kernel.node_type`

### VARIANT-004 — Ashtakavarga Shodhana edge rules

- **Technique IDs:** TEC-051, TEC-052
- **Question:** Which Trikona/Ekadhipatya edge rules and gunakara tables?
- **Option A:** B.V. Raman computational sequence (zero exemptions, equalise-to-smaller, Mandala leave-12)
- **Option B:** Alternate regional editions / software defaults
- **Decision:** supported option A as Candidate (`raman_candidate_v1`) until Approved classical edition citation
- **Engine config key:** `ashtakavarga.shodhana.variant`
- **Notes:** VedAstro commentary used as comparator only; Rahu/Ketu excluded from occupation set in this Candidate rule

### VARIANT-005 — DST ambiguous civil time

- **Technique IDs:** TEC-001
- **Question:** When local civil time falls in a DST overlap, which occurrence?
- **Option A:** earlier (fold=0)
- **Option B:** later (fold=1)
- **Option C:** raise / require explicit operator choice
- **Decision:** supported — all three via `dst_ambiguity_policy`; verification default `earlier`
- **Engine config key:** `kernel.dst_ambiguity_policy`
- **Notes:** Gap times always raise. Resolved stamp records ambiguity + fold.

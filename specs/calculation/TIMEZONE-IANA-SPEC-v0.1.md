# Kernel Timezone Spec — P07c (IANA / DST)

**Module:** `bhava360.kernel.timeutil`  
**Technique:** TEC-001  
**Kernel stamp:** `bhava360-kernel-0.6.0`

## In scope

- Fixed UTC offset resolution (legacy / SPIKE fixtures)
- IANA timezone ids via Python `zoneinfo` + `tzdata` (DST history aware)
- Structured handling of:
  - **DST gap** (spring forward): raise `INVALID_DATETIME`
  - **DST overlap** (fall back): policy `earlier` | `later` | `raise`
- Resolved-time stamp fields: source, id, effective offset, `is_dst`, ambiguity/fold
- Day-window local conversions use the same IANA tzinfo (not a frozen offset)

## Out of scope

- Geolocation → timezone inference
- Historical political timezone renaming beyond tzdb
- Manual civil-calendar reforms outside tzdb

## Config

| Field | Values | Notes |
|---|---|---|
| `timezone_id` | IANA id | Preferred when present |
| `timezone_offset_minutes` | int | Used when no IANA id; if both set must agree |
| `dst_ambiguity_policy` | earlier/later/raise | Default `earlier` for verification |

## Notes

- IANA resolution is authoritative for DST transitions recorded in the zone database.
- Fixed offsets remain supported for comparator fixtures that publish an explicit offset token.

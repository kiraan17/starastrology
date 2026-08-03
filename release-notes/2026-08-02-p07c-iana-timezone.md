# Release note — P07c IANA timezone / DST (2026-08-02)

## Summary

Kernel time resolution now accepts IANA timezone ids with DST gap/overlap handling and stamps effective offset, DST flag, and ambiguity metadata.

## Changes

- `SubjectInput.timezone_id` + `dst_ambiguity_policy`
- `ResolvedTime` extended stamp (`timezone_source`, `is_dst`, fold, etc.)
- Console IANA field + ambiguity policy
- Dependency: `tzdata`
- Kernel constructor stamp `bhava360-kernel-0.6.0`

## Technique

TEC-001 → Auto-Tested (partial → yes for IANA/DST path)

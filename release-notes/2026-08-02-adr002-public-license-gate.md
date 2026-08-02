# Release note — ADR-002 public license gate (2026-08-02)

## Summary

Adds a hard Swiss Ephemeris public-activation gate. Public API helpers refuse to enable until Path L1 (AGPL) or L2 (commercial) evidence is filed and the status JSON is flipped under review.

## Artefacts

- `bhava360.licensing` + `bhava360.api.public_activation`
- Evidence checklists under `docs/decisions/adr-002-evidence/`
- Status default: `blocked`
- Console `/health` reports `public_api_ready` + license gate
- Error code: `LICENSE_GATE_BLOCKED`

## Note

This does **not** purchase or invent a license. It prevents accidental public activation without evidence.

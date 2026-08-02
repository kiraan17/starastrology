# ADR-002 Public Activation Evidence

Public API / customer distribution remains **blocked** until Path **L1** or **L2** evidence is filed and the machine-readable gate status is flipped under review.

## Machine gate

- Code: `bhava360.licensing.assert_public_activation_allowed`
- Status file: `src/bhava360/licensing/adr002_public_status.json`
- Env var `BHAVA360_PUBLIC_API=1` does **not** bypass the gate

## Paths

| Path | Meaning | Checklist |
|---|---|---|
| L1 | AGPL compliance for SE + distribution | [L1-AGPL-COMPLIANCE-CHECKLIST.md](L1-AGPL-COMPLIANCE-CHECKLIST.md) |
| L2 | Commercial/professional Swiss Ephemeris license (default product intent) | [L2-COMMERCIAL-LICENSE-CHECKLIST.md](L2-COMMERCIAL-LICENSE-CHECKLIST.md) |

## Unlock procedure

1. Complete L1 or L2 checklist with linked artefacts (license grant, compliance notes, legal sign-off).
2. Update `adr002_public_status.json`:
   - `public_activation`: `"allowed"`
   - `chosen_path`: `"L1_AGPL"` or `"L2_COMMERCIAL"`
   - `evidence_ids`: non-empty list (e.g. `EVID-SE-L2-001`)
   - `approved_by`: include legal reviewer
   - `approved_at`: ISO timestamp
3. Open a reviewed PR; do not flip status in the same change that ships a public API without legal approval.
4. Confirm `assert_public_activation_allowed()` succeeds in CI.

## Current state

See status JSON — default is `blocked` for private/dev only.

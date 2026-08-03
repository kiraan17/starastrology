# Public API readiness v0.1 (P24a)

**Status:** Documentation + gate wiring only — public API **not** enabled.

## Current readiness

Call `bhava360.api.public_api_readiness()` or console `GET /health`.

Expected while gates are open:

| Field | Value |
|-------|--------|
| `ready` | `false` |
| `license_gate.public_api_allowed` | `false` until ADR-002 L1/L2 |
| `freeze_candidate.public_api_eligible` | `false` |
| `freeze_candidate.frozen` | `false` |
| `blocked_reasons` | non-empty |

## Intended future surface (contract stub)

These routes are **not implemented** for public traffic. Names are reserved for post-freeze work:

| Method | Path | Purpose | Gate |
|--------|------|---------|------|
| POST | `/v1/chart` | Construct chart snapshot | ADR-002 + freeze |
| POST | `/v1/engines/{school}` | Run one school engine | ADR-002 + freeze + school Approved/Frozen |
| POST | `/v1/orchestration` | Evidence/conflict package | ADR-002 + freeze |
| GET | `/v1/health` | Public readiness | may be public-safe subset |
| GET | `/v1/manifest` | Frozen manifest id/version | ADR-002 + freeze |

### Non-goals until freeze

- Auth, rate limits, tenancy (Phase 24 remaining work)
- LLM narrative endpoints
- Customer UI
- Restricted modules (medical/longevity/LK remedies) without legal review

### Narrative-output contract (later LLM)

LLM layers must consume **structured engine JSON only** and must not invent planetary positions, verdicts, or remedies. Activation requires Frozen/Approved engines + product safety policy (SRC-014).

## Unlock sequence (human)

1. Expert validation → Frozen manifest under release authority  
2. ADR-002 Path L1 or L2 evidence filed; status JSON flipped under review  
3. Implement `/v1/*` routers behind `enable_public_api_surface()`  
4. Customer frontend planning may begin only after this gate

## Related

- `docs/status/FREEZE-CANDIDATE-v0.1.md`
- `docs/decisions/adr-002-evidence/`
- `release/freeze-candidate-manifest-v0.1.json`

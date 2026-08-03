# Architecture Context Diagram (Draft)

**Phase:** 3  
**Status:** Draft — aligns with ADR-001/ADR-002 proposals  
**Out of scope here:** customer UX, billing, marketing

## Context

```text
                    ┌──────────────────────────┐
                    │ Internal Verification UI │
                    │ (console only)           │
                    └────────────┬─────────────┘
                                 │
                         Bhava360 API
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        ▼                        ▼                        ▼
┌───────────────┐      ┌─────────────────┐      ┌──────────────────┐
│ Chart Config  │      │ Subject Inputs  │      │ Expert Review /  │
│ + Variants    │      │ (birth/prashna) │      │ Test fixtures    │
└───────┬───────┘      └────────┬────────┘      └────────┬─────────┘
        │                       │                        │
        └───────────┬───────────┘                        │
                    ▼                                    │
          ┌───────────────────┐                          │
          │ Calculation Kernel│◄── Swiss Ephemeris       │
          │ IAstronomyProvider│    (license-gated)       │
          └─────────┬─────────┘                          │
                    │ snapshots                          │
                    ▼                                    │
          ┌───────────────────┐                          │
          │ Chart Construction│                          │
          └─────────┬─────────┘                          │
                    │                                    │
      ┌─────────────┼─────────────┬──────────────┐       │
      ▼             ▼             ▼              ▼       │
 Parashara         KP         Jaimini     Nadi/Other     │
 Engine          Engine       Engine       Engines       │
      │             │             │              │       │
      └─────────────┴─────────────┴──────────────┘       │
                    │ evidence                           │
                    ▼                                    │
          ┌───────────────────┐                          │
          │ Orchestration     │◄─────────────────────────┘
          │ conflict + score  │
          └─────────┬─────────┘
                    │
                    ▼
          Versioned DB (rules, snapshots, evidence, reviews)

Comparator only (not in production decision path):
          VedAstro API/Library ──► golden tests / SPIKE fixtures
```

## Trust boundary

| Component | May decide astrology verdicts? |
|---|---|
| Swiss Ephemeris / kernel | Positions only |
| School engines | Yes, within school |
| Orchestration | Ranks/conflicts structured evidence only |
| VedAstro | No — comparator |
| LLM | No — explain approved evidence later |

## Deployment note

Public activation requires ADR-002 license path. Customer frontend waits for Phase 24 API freeze.

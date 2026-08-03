# Repository Structure

```
.
├── AGENTS.md                          # Permanent AI instructions
├── README.md
├── backlog/                           # Programme backlog
├── console/                           # Internal verification console (later; empty for now)
├── docs/
│   ├── architecture/                  # Phase 3 diagrams
│   ├── decisions/                     # ADRs / license decisions
│   ├── prompts/                       # Bounded AI task prompts (P00, P02, …)
│   ├── requirements/                  # Controlling plan + charter
│   └── status/                        # Status workflow
├── expert-reviews/                    # Expert sign-off records (later)
├── registry/                          # Live Technique Registry
├── release-notes/                     # Freeze / release manifests (later)
├── rules/
│   ├── libraries/                     # Rule corpora by school (later)
│   └── templates/                     # Rule specification standard (Phase 5)
├── scripts/                           # Tooling (structure checks, etc.)
├── sources/
│   ├── notes/                         # Digitised rule notes
│   ├── registers/                     # Source Register
│   └── variants/                      # Variant decision log
├── specs/
│   ├── calculation/                   # Kernel specs (Phase 6+)
│   ├── data-model/                    # Phase 4 dictionary/schema
│   └── engines/                       # Per-engine specs
├── src/                               # Application code (not started in Phase 0)
└── tests/
    ├── boundary/
    ├── golden/
    ├── integration/
    └── unit/
```

## Phase 0 rule

`src/` and `console/` remain empty placeholders until Phases 0–5 are approved and a later phase explicitly authorises implementation.

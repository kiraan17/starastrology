# Birth-time rectification toolkit scaffold (P22b)

**Module:** `bhava360.engines.rectification`  
**Engine:** `Rectification` `0.1.0-scan-scaffold`  
**Status:** Candidate  
**Technique:** TEC-095  
**Safety:** restricted

## Scope

Time-window sensitivity toolkit around a stated civil birth time:

| Output | Rule |
|--------|------|
| Sample grid | Inclusive ±`window_minutes` at `step_minutes` (step auto-widens if > max samples) |
| Fingerprints | Lagna sign/nak/pada, Moon nak/pada, Vimshottari balance lord, D9/D60 lagna, Kunda sign |
| Kunda | `lagna_longitude × 81` (mod 360) — structural marker |
| Transitions | Field flips between consecutive samples |
| Manual events | Passthrough anchors only — **not scored** |

Defaults: window 15m (or `birth_time_uncertainty_minutes` when set), step 5m, max 25 samples.

Stamp: `rectification_scan_candidate_v1`

## Safety

Does **not** assert a true birth time or emit a winner. Restricted verification toolkit only.

## Deferred

- Pranapada / Tatkalika classical checks
- Event-matching scoring packs
- Automatic ranked selection

# Parashara Engine Thin Slice (P10 v0.1)

**Module:** `bhava360.engines.parashara`  
**Techniques:** TEC-037 (partial), TEC-041 (activation stub)

## In scope

- Structured `RuleEvidence` outcomes: matched / failed / cancelled / skipped / inconclusive
- RULE-PARASHARA-001 Gajakesari (provisional mutual whole-sign kendra + combust cancel)
- RULE-PARASHARA-002 Budha-Aditya (provisional same-sign conjunction)
- Period activation against Vimshottari maha/antar lords (natal potential vs active)
- Positive / negative / cancellation / live-chart activation field tests

## Explicit limitations

- Classical source edition for yogas is still **Candidate** (`SRC-004`); rules are provisional product definitions
- No user-facing narrative claims
- No full yoga catalogue yet
- Cancellation set is intentionally minimal and labelled provisional

## Usage

```python
chart = ChartConstructor().build(subject).to_dict()
result = run_parashara_engine(chart)
```

# KP Engine Thin Slice (P11 v0.1)

**Module:** `bhava360.engines.kp`  
**Techniques:** TEC-014 (partial), TEC-042, TEC-043 (sketch)

## In scope

- RULE-KP-001 config isolation (KP ayanamsa + Placidus required)
- Star lord / sub lord / sub-sub lord chains via Vimshottari proportions
- Cuspal lord chains for 12 Placidus cusps
- Basic significator sketch: occupants, owner, star lord, sub lord
- Hard fail on Lahiri/whole-sign silent reuse

## Out of scope

- Domain verdicts (fruitful/barren packs)
- Ruling Planets module
- KP Horary 1–249
- Full significator hierarchy weighting / verdict engine

## Usage

```python
from bhava360.engines.kp import run_kp_engine
result = run_kp_engine(subject)  # defaults to KP ayanamsa + Placidus
```

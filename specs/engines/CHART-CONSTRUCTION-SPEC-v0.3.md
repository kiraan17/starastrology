# Chart Construction Specification (P08 v0.3)

**Status:** Implemented scaffold  
**Module:** `bhava360.chart`  
**Depends on:** Kernel P07a/P07b

## In scope

- Divisional charts: D1, D2, D3, D7, D9, D10, D12, D16, D20, D24, D27, D30, D40, D45, D60
- D150 available only behind birth-time accuracy gate (`birth_time_uncertainty_minutes <= 1` by default)
- Dignity classification: exalted / debilitated / own / moolatrikona / neutral (+ combustion candidate orb)
- Sign lord mapping
- Rasi (whole-sign) vs Bhava Chalit (default Placidus cuspal) house comparison per planet
- `ChartConstructor.build()` assembled chart document with version stamp `bhava360-kernel-0.3.0`

## Explicit limitations / Source Needed

- D30 unequal classical trimsamsa lords are approximated (equal-part scaffold) until Approved source edition is cited
- Some higher-varga start-sign conventions vary by author — recorded as configurable later; current defaults documented in code
- No yoga/school interpretation
- No KP sublord chains yet

## Techniques touched

| ID | Status |
|---|---|
| TEC-011 | Auto-Tested (via constructor D1) |
| TEC-012 | Auto-Tested (Rasi vs Bhava map) |
| TEC-015 | Auto-Tested (D1–D60 pack; D30 approx noted) |
| TEC-016 | Auto-Tested gate (D150) |
| TEC-017 | Partial (combustion candidate only) |
| TEC-020 | Partial (sign lord + dignity states) |
| TEC-022 | Auto-Tested (exalt/debil/own/moolatrikona) |

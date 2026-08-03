# Sample Rule: Sidereal longitude available for planet

```yaml
rule_id: RULE-KERNEL-001
technique_id: TEC-003
school: Kernel
name: Planet sidereal longitude computed
source_ids: [SRC-001]
variant_id: null
version: "0.1.0"
status: Spec Ready
safety_level: normal

inputs:
  - name: planet
    type: PlanetName
  - name: utc_datetime
    type: datetime
  - name: ephemeris_mode
    type: string

preconditions:
  - ephemeris files available for date range
  - planet in supported set

conditions:
  - id: C1
    assert: longitude_sidereal_deg is finite
    assert: 0 <= longitude_sidereal_deg < 360

exceptions:
  - id: E1
    when: date out of ephemeris range
    outcome: skipped
    error_code: EPHEMERIS_UNAVAILABLE

modifiers: []

activation:
  type: always_when_preconditions_met

output:
  type: PlanetPosition partial
  fields: [longitude_sidereal_deg, speed_longitude, is_retrograde]

test_cases:
  - id: T-POS-001
    kind: positive
    chart_ref: tests/golden/vedastro-spike/chennai_1990_0815_1200.json
    expect: Sun longitude finite
  - id: T-NEG-001
    kind: negative
    input: unsupported planet name
    expect: structured validation error

change_note: Initial sample for Phase 5 template validation.
```

Notes: Comparator vs VedAstro is a **test** concern, not part of this rule’s source authority.

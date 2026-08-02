# Sample Rule: KP chart config isolation

```yaml
rule_id: RULE-KP-001
technique_id: TEC-042
school: KP
name: KP configuration must not reuse Lahiri/Parashara defaults silently
source_ids: [SRC-006, SRC-015]
variant_id: null
version: "0.1.0"
status: Spec Ready
safety_level: normal

inputs:
  - chart config

preconditions:
  - engine == KP

conditions:
  - id: C1
    assert: config.ayanamsa is an approved KP ayanamsa
  - id: C2
    assert: config.house_system == placidus  # unless an approved KP variant says otherwise

exceptions:
  - id: E1
    when: caller passes Lahiri + whole_sign without explicit KP override flag
    outcome: failed
    error_code: KP_CONFIG_MISMATCH

modifiers: []

activation:
  type: always_for_kp_runs

output:
  type: ConfigValidationResult

test_cases:
  - id: T-POS-KPCFG-001
    kind: positive
    expect: KP ayanamsa + Placidus accepted
  - id: T-NEG-KPCFG-001
    kind: negative
    expect: Lahiri whole-sign rejected for KP engine path

change_note: Encodes non-negotiable school isolation for KP.
```

# RULE-PARASHARA-002 Budha-Aditya Yoga (provisional)

```yaml
rule_id: RULE-PARASHARA-002
technique_id: TEC-037
school: Parashara
name: Budha-Aditya Yoga natal formation
source_ids: [SRC-004, SRC-014]
version: "0.1.0-provisional"
status: Implemented
safety_level: normal

conditions:
  - id: C1_same_sign_conjunction
    assert: Sun and Mercury occupy the same whole sign

exceptions:
  - id: X1_mercury_retrograde_note
    when: Mercury retrograde
    outcome: noted modifier only (not cancellation)

activation:
  type: natal_potential_until_period_activation
  required_lords: [Sun, Mercury]
```

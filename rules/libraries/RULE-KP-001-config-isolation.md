# RULE-KP-001 KP configuration isolation

```yaml
rule_id: RULE-KP-001
technique_id: TEC-042
school: KP
name: KP configuration must not reuse Lahiri/Parashara defaults silently
source_ids: [SRC-006, SRC-015]
version: "0.1.0"
status: Implemented
safety_level: normal

conditions:
  - id: C1_kp_ayanamsa
    assert: config.ayanamsa == kp
  - id: C2_placidus_houses
    assert: config.house_system == placidus

exceptions:
  - id: E1_override_flag
    when: kp_allow_nonstandard_config == true
    outcome: matched with warning note

output:
  type: RuleEvidence
  error_code_on_fail: KP_CONFIG_MISMATCH
```

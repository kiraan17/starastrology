# RULE-PARASHARA-001 Gajakesari Yoga (provisional implementation)

```yaml
rule_id: RULE-PARASHARA-001
technique_id: TEC-037
school: Parashara
name: Gajakesari Yoga natal formation
source_ids: [SRC-004, SRC-014]
variant_id: null
version: "0.2.0-provisional"
status: Implemented
safety_level: normal

inputs:
  - Moon whole-sign house from Asc
  - Jupiter whole-sign house from Asc
  - Sun longitude (for combust cancellation)

preconditions:
  - Constructed chart with whole_sign angles and planet longitudes

conditions:
  - id: C1_mutual_kendra
    assert: Moon and Jupiter are in mutual whole-sign kendras (relative houses 1/4/7/10)

exceptions:
  - id: X1_jupiter_combust_provisional
    when: Jupiter is within combustion orb of Sun
    outcome: cancelled

activation:
  type: natal_potential_until_period_activation
  required_lords: [Moon, Jupiter]
  note: Active only when a required lord is current Vimshottari maha or antar lord.

output:
  type: RuleEvidence

test_cases:
  - id: T-POS-Gaja-001
    kind: positive
  - id: T-NEG-Gaja-001
    kind: negative
  - id: T-CANCEL-Gaja-001
    kind: cancellation
  - id: T-ACT-Gaja-001
    kind: activation

change_note: >
  Provisional product definition implemented for thin-slice engine validation.
  Replace with Approved BPHS edition citation before Expert-Checked/Approved.
```

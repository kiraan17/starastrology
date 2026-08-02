# Sample Rule: Gajakesari Yoga natal formation (illustrative)

```yaml
rule_id: RULE-PARASHARA-001
technique_id: TEC-037
school: Parashara
name: Gajakesari Yoga natal formation (draft)
source_ids: [SRC-004]  # Candidate — not Approved yet
variant_id: null
version: "0.1.0-draft"
status: Not Researched  # cannot rise without Approved source + expert examples
safety_level: normal

inputs:
  - Jupiter sign/house
  - Moon sign/house
  - aspect/association definition set (must be cited)

preconditions:
  - D1 chart snapshot present
  - Parashara aspect definition variant selected

conditions:
  - id: C1
    assert: "Jupiter and Moon in kendra mutual relationship per selected definition"
    # Exact kendra-from-each-other / Moon-kendra-from-Jupiter wording must be fixed by source

exceptions:
  - id: X1
    name: cancellation_placeholder
    assert: "Source-defined cancellation conditions"
    outcome: cancelled

modifiers:
  - id: M1
    when: participating planets weak by selected strength method
    effect: reduce_confidence

activation:
  type: natal_potential_only
  note: >
    Remains natal context until timing engine activates participating
    planets/houses (see controlling plan Phase 10 note). Do not emit
    current-life event claims from formation alone.

output:
  type: YogaEvidence
  fields: [formed, cancelled, participants, houses, evidence_condition_ids]

test_cases:
  - id: T-POS-Gaja-001
    kind: positive
    status: Source Needed
  - id: T-NEG-Gaja-001
    kind: negative
    status: Source Needed
  - id: T-CANCEL-Gaja-001
    kind: cancellation
    status: Source Needed
  - id: T-ACT-Gaja-001
    kind: activation
    status: Source Needed

change_note: >
  Illustrative sample demonstrating template fields and activation split.
  Implementation is blocked until SRC-004 edition is Approved and
  conditions are cited to chapter/verse/page.
```

**Stop condition engaged:** Source Needed for precise formation/cancellation text.

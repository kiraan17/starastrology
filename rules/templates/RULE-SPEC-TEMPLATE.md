# Rule Specification Template

**Phase:** 5  
**Status:** Draft standard — required before large yoga/rule encoding

## Mandatory fields

Every rule file or DB record must include:

| Field | Description |
|---|---|
| `rule_id` | Permanent ID (`RULE-SCHOOL-###`) |
| `technique_id` | Registry ID |
| `school` | Parashara / KP / Jaimini / … |
| `name` | Human-readable |
| `source_ids` | Approved SRC references |
| `variant_id` | Optional VARIANT reference |
| `inputs` | Required snapshot fields / derived values |
| `preconditions` | Chart/config requirements |
| `conditions` | Positive match logic |
| `exceptions` | Negative / cancellation logic |
| `modifiers` | Strength or confidence adjustments |
| `activation` | Natal potential vs timing activation requirements |
| `output` | Structured verdict object (not prose) |
| `confidence_notes` | Birth-time or source uncertainty effects |
| `safety_level` | normal / restricted / research_only / prohibited_user_facing |
| `status` | workflow status |
| `version` | Rule version |
| `test_cases` | At least one positive, one negative; boundary where relevant |
| `change_note` | Required on every new version |

## Representation rules

1. Prefer declarative conditions over narrative paragraphs.
2. Cancellation is explicit — never implied by omitting a branch.
3. Activation is separate from formation (e.g. yoga may exist natally but be inactive).
4. Evidence output must list matched condition IDs and key input values.
5. Deprecation: old versions remain readable; new version gets a new `version` and change note.

## Review checklist

- [ ] Sources approved or product_rule explicit
- [ ] Inputs/outputs/units defined
- [ ] Positive, negative, cancellation, activation examples
- [ ] Safety level set
- [ ] No school leakage (KP rule doesn’t assume Lahiri defaults, etc.)
- [ ] Tests named and linked

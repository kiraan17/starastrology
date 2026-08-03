# Rule Versioning Policy

1. Any behavioural change creates a **new rule version**; never edit Approved/Frozen versions in place.
2. Calculation snapshots and engine results store `rule_id` + `rule_version`.
3. Historical predictions remain reproducible against the stored versions.
4. Changing a default variant config is a product change note and may require re-approval of affected techniques.
5. Expected golden-test updates require documented expert/quality decision — never only to silence failures.

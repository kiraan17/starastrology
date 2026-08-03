# Privacy Classification Summary

See full field-level classes in [`DATA-DICTIONARY.md`](DATA-DICTIONARY.md).

| class | Summary |
|---|---|
| P0_public | Reference lists, technique IDs |
| P1_config | Calculation config and versions |
| P2_event | Non-identifying event/question metadata |
| P3_birth | Birth/location/time — protect and deletable |
| P4_identity | Accounts and reviewer identities |
| P5_restricted_output | Medical/financial/longevity research outputs |

**Draft policy statements**

1. Do not put P3 birth payloads in client-side analytics by default.
2. Snapshots linked to P3 data inherit birth privacy until anonymized.
3. Restricted outputs (P5) are off by default in customer APIs.
4. Deletion requests must define whether snapshots are hard-deleted or irreversibly anonymized (ops handbook later).

# Jaimini Thin Slice (P15 v0.1)

**Module:** `bhava360.engines.jaimini`  
**Techniques:** TEC-028, TEC-066, TEC-067, TEC-068  
**Engine label:** **Jaimini** only — never Gemini

## In scope

- Chara Karakas with explicit **seven** or **eight** scheme (`VARIANT-001` / `jaimini.chara_karaka.scheme`)
- Arudha padas A1–A12 (whole-sign) with common exception (pada in house or 7th → 10th from calculated pada)
- Karakamsa = Atmakaraka in D9; Swamsa = Ascendant in D9
- Argala / Virodha Argala sign sketch from Arudha Lagna (2/4/11 vs 12/10/3)

## Out of scope

- Jaimini rashi dashas (TEC-033)
- Event interpretation pack (TEC-069)
- Secondary argala / intervention scoring
- Blending with Parashara/KP verdicts

## Config

| Key | Values | Notes |
|---|---|---|
| `jaimini.chara_karaka.scheme` | `seven` \| `eight` | Required stamp; console defaults to `seven` for verification only |

## Source note

Rules are Candidate pending Approved classical edition / expert confirmation (`SRC-007`).

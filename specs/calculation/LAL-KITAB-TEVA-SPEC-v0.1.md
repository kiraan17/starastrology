# Lal Kitab Teva scaffold (P22a)

**Module:** `bhava360.engines.lal_kitab`  
**Engine:** `LalKitab` `0.1.0-teva-scaffold`  
**Status:** Candidate  
**Technique:** TEC-090  
**Safety:** restricted

## Scope

| Output | Rule |
|--------|------|
| Teva house | Fixed Aries=1 … Pisces=12 from sidereal sign (not lagna) |
| Pakka Ghar | Sun1 Moon4 Mars3 Mercury7 Jupiter2 Venus7 Saturn10 Rahu12 Ketu6 |
| Aspects | Mars 4/7/8; Saturn 3/7/10; Jupiter/Rahu/Ketu 5/7/9; luminaries+Merc+Venus 7 |
| Yuti | Co-residents in same Teva house |
| Axis yuti | Occupied complementary pairs 1–7 … 6–12 |
| Varshphal | `((natal_house - 1) + age) % 12 + 1` when age/target_year given |

Stamp: `lal_kitab_teva_candidate_v1`

## Contradictions

Parashara rasi houses count from lagna; Lal Kitab Teva does not. Diffs are listed per planet — do not blend.

## Deferred / blocked

Debts (rin), remedies/upay, sleeping house rules, farzi planets, interpretive yuti verdicts.

## Safety

No remedies or debt verdicts in this thin slice. Not medical/financial/longevity advice.

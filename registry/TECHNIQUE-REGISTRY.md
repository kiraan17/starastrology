# Technique Registry v0.2 (Provisional)

**Status:** Provisional — reconstructed from BHAVA360 phase inventory because the official 96-row table was missing from the source paste.  
**Owner phase:** Phase 1 (P02)  
**Authority:** Product owner must confirm, rename, merge or split rows before this becomes Registry v1.  
**VedAstro column:** whether SPIKE/comparator overlap is expected (not a source approval).

## Field legend

| Field | Values |
|---|---|
| `kind` | calculation / classification / timing / interpretation / manual_input / lookup / orchestration |
| `status` | Not Researched (all rows until sources exist) |
| `safety_level` | normal / restricted / research_only / prohibited_user_facing |
| `vedastro_overlap` | yes / partial / no |

## Top-level techniques (provisional count: 96)

| technique_id | name | parent_engine | kind | safety_level | expert_approval_required | vedastro_overlap | status | notes |
|---|---|---|---|---|---|---|---|---|
| TEC-001 | Local datetime, timezone, DST, Julian day | Kernel | calculation | normal | yes | yes | Auto-Tested | P07c IANA+DST via zoneinfo/tzdata; fixed offset retained |
| TEC-002 | Geolocation and coordinate validation | Kernel | calculation | normal | no | yes | Not Researched | |
| TEC-003 | Planetary longitudes, speed, retrograde | Kernel | calculation | normal | yes | yes | Auto-Tested | P07a Moshier/Lahiri; SPIKE-01 golden |
| TEC-004 | Lunar position and phases support data | Kernel | calculation | normal | yes | yes | Not Researched | |
| TEC-005 | Rahu/Ketu node modes | Kernel | calculation | normal | yes | yes | Not Researched | mean/true config |
| TEC-006 | Sidereal conversion and ayanamsa set | Kernel | calculation | normal | yes | yes | Not Researched | Lahiri/KP/etc |
| TEC-007 | House cusps and house-system pack | Kernel | calculation | normal | yes | partial | Auto-Tested | whole_sign + placidus in P07b; Sripati deferred |
| TEC-008 | Ascendant, MC and related angles | Kernel | calculation | normal | yes | partial | Auto-Tested | P07b |
| TEC-009 | Sunrise, sunset, local day boundary | Kernel | calculation | normal | yes | partial | Auto-Tested | P07b disc-center; local civil date |
| TEC-010 | Ephemeris run stamp (lib/files/mode/version) | Kernel | calculation | normal | no | no | Auto-Tested | Snapshot/library stamp present; public activation gated by ADR-002 |
| TEC-011 | Rasi (D1) chart construction | Chart | calculation | normal | yes | yes | Auto-Tested | P08a |
| TEC-012 | Bhava Chalit mapping | Chart | calculation | normal | yes | partial | Auto-Tested | Rasi vs Placidus cuspal compare |
| TEC-013 | Nakshatra, pada, star lord | Chart | calculation | normal | yes | yes | Not Researched | |
| TEC-014 | KP sublord and sub-sub lord | KP | calculation | normal | yes | partial | Auto-Tested | P11a star/sub/sub-sub chains |
| TEC-015 | Divisional charts D1–D60 pack | Chart | calculation | normal | yes | yes | Auto-Tested | D30 approx noted; Source Needed for classical trimsamsa |
| TEC-016 | Nadiamsa D150 with birth-time accuracy gate | Nadi | calculation | restricted | yes | no | Auto-Tested | Gate implemented |
| TEC-017 | Combustion, retro, planetary war states | Chart | classification | normal | yes | partial | Implemented | Combustion candidate + retro from kernel; war TBD |
| TEC-018 | Graha aspects | Chart | calculation | normal | yes | yes | Auto-Tested | P08b whole-sign + special aspects |
| TEC-019 | Rashi aspects | Jaimini | calculation | normal | yes | partial | Auto-Tested | P08b Jaimini rashi drishti (not Gemini) |
| TEC-020 | Dignity, ownership, dispositor graph | Chart | classification | normal | yes | yes | Auto-Tested | P08b dispositor chains + graph edges |
| TEC-021 | Natural/temporal/functional benefic-malefic | Classification | classification | normal | yes | partial | Not Researched | Threshold config |
| TEC-022 | Exaltation, debilitation, own, moolatrikona, cancellation | Classification | classification | normal | yes | yes | Auto-Tested | Cancellation rules TBD |
| TEC-023 | Shadbala (component pack) | Strength | calculation | normal | yes | yes | Not Researched | Split to 6 children later |
| TEC-024 | Bhava Bala | Strength | calculation | normal | yes | partial | Not Researched | |
| TEC-025 | Vimshopaka Bala | Strength | calculation | normal | yes | partial | Not Researched | |
| TEC-026 | Argala and Virodha Argala | Strength | calculation | normal | yes | partial | Not Researched | |
| TEC-027 | Natural karakas | Classification | classification | normal | yes | partial | Not Researched | |
| TEC-028 | Chara Karakas (7/8 config) | Jaimini | classification | normal | yes | yes | Auto-Tested | P15 VARIANT-001 seven|eight; never Gemini |
| TEC-029 | Vimshottari dasha full depth | Timing | timing | normal | yes | yes | Auto-Tested | P09a Maha→Prana capable; mean year 365.2425d |
| TEC-030 | Conditional dasha eligibility pack | Timing | timing | normal | yes | partial | Not Researched | |
| TEC-031 | Yogini dasha | Timing | timing | normal | yes | partial | Not Researched | |
| TEC-032 | Kalachakra dasha | Timing | timing | normal | yes | no | Not Researched | |
| TEC-033 | Jaimini rashi dasha pack | Jaimini | timing | normal | yes | partial | Not Researched | Chara/Sthira/Navamsa… |
| TEC-034 | Annual dasha variants (Mudda/Patyayini/etc) | Annual | timing | normal | yes | partial | Not Researched | |
| TEC-035 | Transit engine vs natal reference | Timing | timing | normal | yes | partial | Not Researched | |
| TEC-036 | Parashara functional analysis core | Parashara | interpretation | normal | yes | partial | Not Researched | |
| TEC-037 | Parashara yoga detection pack | Parashara | interpretation | normal | yes | partial | Implemented | P10a thin slice (2 provisional yogas); Source Needed for full catalogue |
| TEC-038 | Parashara dosha and exception pack | Parashara | interpretation | normal | yes | partial | Not Researched | |
| TEC-039 | Bhavat Bhavam | Parashara | interpretation | normal | yes | no | Not Researched | |
| TEC-040 | Varga confirmation rules | Parashara | interpretation | normal | yes | no | Not Researched | |
| TEC-041 | Dasha/transit activation model | Orchestration | orchestration | normal | yes | no | Implemented | P10a maha/antar activation stub |
| TEC-042 | KP configuration (New Ayanamsa + Placidus) | KP | calculation | normal | yes | partial | Auto-Tested | P11a RULE-KP-001 enforced |
| TEC-043 | KP significator hierarchy | KP | interpretation | normal | yes | partial | Implemented | P11a sketch only (occupants/owner/star/sub) |
| TEC-044 | Cuspal sublord verdict engine | KP | interpretation | normal | yes | partial | Not Researched | |
| TEC-045 | Ruling Planets | KP | timing | normal | yes | partial | Not Researched | |
| TEC-046 | KP Horary 1–249 | KP | interpretation | normal | yes | partial | Not Researched | |
| TEC-047 | KP domain house-combination pack | KP | interpretation | normal | yes | no | Not Researched | Config versioned |
| TEC-048 | Bhinnashtakavarga | Ashtakavarga | calculation | normal | yes | yes | Auto-Tested | P12a contributor audit trail |
| TEC-049 | Sarvashtakavarga | Ashtakavarga | calculation | normal | yes | yes | Auto-Tested | P12a sum of seven BAVs (=337) |
| TEC-050 | Prastara Ashtakavarga | Ashtakavarga | calculation | normal | yes | yes | Auto-Tested | P12c 8×12 grids; reconstructs BAV totals |
| TEC-051 | Trikona and Ekadhipatya Shodhana | Ashtakavarga | calculation | normal | yes | yes | Auto-Tested | P12b raman_candidate_v1; SAV Mandala included |
| TEC-052 | Sodhya Pinda | Ashtakavarga | calculation | normal | yes | yes | Auto-Tested | P12b Rasi+Graha gunakara; longevity conversion deferred |
| TEC-053 | Kakshya scoring and transit contribution | Ashtakavarga | timing | normal | yes | no | Implemented | P12a kakshya labels + natal sign scores; full transit scorer TBD |
| TEC-054 | Nakshatra Nadi chain engine | NakshatraNadi | interpretation | normal | yes | no | Implemented | P13 scaffold; CORPUS_GATE_BLOCKED until SRC-009 Approved |
| TEC-055 | Nakshatra Nadi event triggers | NakshatraNadi | interpretation | normal | yes | no | Implemented | P13 scaffold gated with TEC-054 |
| TEC-056 | Bhrigu Nandi Nadi | BhriguNandiNadi | interpretation | normal | yes | no | Not Researched | Separate module |
| TEC-057 | Jupiter progression rules (approved set) | BhriguNandiNadi | timing | normal | yes | no | Not Researched | |
| TEC-058 | Chandra Kala Nadi / Deva Keralam corpus | ChandraKalaNadi | interpretation | normal | yes | no | Not Researched | |
| TEC-059 | Dhruva Nadi (if source exists) | NadiOther | interpretation | normal | yes | no | Not Researched | Source gate |
| TEC-060 | Sthira Nadi (if source exists) | NadiOther | interpretation | normal | yes | no | Not Researched | Source gate |
| TEC-061 | Satya Nadi (if source exists) | NadiOther | interpretation | normal | yes | no | Not Researched | Source gate |
| TEC-062 | Meena Nadi (if source exists) | NadiOther | interpretation | normal | yes | no | Not Researched | Source gate |
| TEC-063 | Saptarishi Nadi (if source exists) | NadiOther | interpretation | normal | yes | no | Not Researched | Source gate |
| TEC-064 | Bhrigu Samhita-style pattern library | NadiOther | lookup | research_only | yes | no | Not Researched | Explicit reconstruction only |
| TEC-065 | Palm-leaf manuscript Nadi | NadiOther | manual_input | prohibited_user_facing | yes | no | Not Researched | Not algorithmic claim |
| TEC-066 | Karakamsa and Swamsa | Jaimini | calculation | normal | yes | yes | Auto-Tested | P15 AK D9 + Asc D9 |
| TEC-067 | Arudha Lagna A1–A12 | Jaimini | calculation | normal | yes | yes | Auto-Tested | P15 whole-sign + exception |
| TEC-068 | Jaimini argala | Jaimini | calculation | normal | yes | partial | Auto-Tested | P15 sign sketch from AL; intervention TBD |
| TEC-069 | Jaimini event interpretation pack | Jaimini | interpretation | normal | yes | no | Not Researched | Never label Gemini |
| TEC-070 | Panchanga core (Tithi/Vara/Nakshatra/Yoga/Karana) | Panchanga | timing | normal | yes | yes | Not Researched | |
| TEC-071 | Rahu Kala, Yamaganda, Gulika, Abhijit | Panchanga | timing | normal | yes | partial | Not Researched | |
| TEC-072 | Tara Bala and Chandra Bala | Panchanga | timing | normal | yes | partial | Not Researched | |
| TEC-073 | Hora and Chaughadiya | Panchanga | timing | normal | yes | partial | Not Researched | |
| TEC-074 | Panchaka and Bhadra | Panchanga | timing | normal | yes | partial | Not Researched | |
| TEC-075 | Panchapakshi day/night cycles | Panchanga | timing | normal | yes | yes | Not Researched | VedAstro has module |
| TEC-076 | Activity good/mixed/avoid windows | Panchanga | timing | normal | yes | no | Not Researched | No major life claims |
| TEC-077 | Tajika Varshaphal / Muntha / year lord / Sahams | Tajika | calculation | normal | yes | partial | Not Researched | Annual location rule TBD |
| TEC-078 | Tajika aspects and yogas | Tajika | interpretation | normal | yes | no | Not Researched | |
| TEC-079 | Tithi Pravesh | Annual | timing | normal | yes | no | Not Researched | |
| TEC-080 | Sudarshana Chakra | Chakra | calculation | normal | yes | no | Not Researched | |
| TEC-081 | Bhrigu Bindu and transit triggers | Progression | timing | normal | yes | no | Not Researched | |
| TEC-082 | Sarvatobhadra Chakra and Vedha | Chakra | calculation | normal | yes | no | Not Researched | |
| TEC-083 | Tara Chakra and Kota Chakra | Chakra | calculation | normal | yes | no | Not Researched | |
| TEC-084 | Chandra Kriya, Avastha, Vela | Classification | classification | normal | yes | no | Not Researched | |
| TEC-085 | Gandanta and related conditions | Classification | classification | normal | yes | partial | Not Researched | |
| TEC-086 | Prashna Marga calculations and sphutas | Prashna | interpretation | normal | yes | partial | Not Researched | |
| TEC-087 | Tamil Prashna / Aroodha Lagna Prashna | Prashna | interpretation | normal | yes | no | Not Researched | |
| TEC-088 | Ashtamangala Prashna | Prashna | manual_input | normal | yes | no | Not Researched | Manual shell counts |
| TEC-089 | Krishna Mishra / Shatpanchashika | Prashna | interpretation | normal | yes | no | Not Researched | |
| TEC-090 | Lal Kitab teva/aspect/debt/remedy module | LalKitab | interpretation | restricted | yes | no | Not Researched | Keep contradictions visible |
| TEC-091 | Systems Approach configuration | SystemsApproach | interpretation | normal | yes | no | Not Researched | |
| TEC-092 | Numerology (mantra-shastra style) | Numerology | calculation | normal | yes | yes | Not Researched | VedAstro overlap |
| TEC-093 | Muhurta event rule packs | Muhurta | timing | normal | yes | yes | Not Researched | |
| TEC-094 | Compatibility / Kuta systems | Compatibility | interpretation | normal | yes | yes | Not Researched | |
| TEC-095 | Birth-time rectification toolkit | Rectification | orchestration | restricted | yes | partial | Not Researched | |
| TEC-096 | Evidence, scoring and conflict orchestration | Orchestration | orchestration | normal | yes | no | Not Researched | Product weights |

## Deferred specialist rows (not in the provisional 96; track separately)

These appear in the controlling plan but are held outside the provisional top-96 to avoid silently inventing the missing official inventory ordering:

| track_id | name | safety_level | notes |
|---|---|---|---|
| DEF-001 | Medical astrology mappings | restricted | Legal/safety review |
| DEF-002 | Mundane astrology research module | research_only | |
| DEF-003 | Financial astrology research module | research_only | |
| DEF-004 | Longevity methods | prohibited_user_facing | Research only until legal review |
| DEF-005 | Vastu correlation bridge | research_only | Separate Vastu product |
| DEF-006 | Sripati / alternate Bhava Chalit variants | normal | May merge under TEC-007/012 |

## Dependency map (draft)

```text
TEC-001..010 (Kernel)
  └─ TEC-011..020 (Chart)
      ├─ TEC-021..028 (Strength/Classification)
      ├─ TEC-029..035 (Timing platform)
      │     └─ TEC-041, TEC-053, TEC-076, TEC-095
      ├─ TEC-036..040 (Parashara)
      ├─ TEC-042..047 (KP)  [also needs TEC-014]
      ├─ TEC-048..053 (Ashtakavarga)
      ├─ TEC-054..065 (Nadi family)
      ├─ TEC-019,028,033,066..069 (Jaimini)
      ├─ TEC-070..076 (Panchanga/daily)
      ├─ TEC-077..085 (Annual/chakra/progressions)
      ├─ TEC-086..089 (Prashna) + TEC-046
      └─ TEC-090..094 (Specialist)
TEC-096 consumes evidence from all engines; never replaces them.
```

## Coverage dashboard definition

| Metric | Target |
|---|---|
| Top-level techniques | 96 confirmed by product owner |
| Rows with unique `technique_id` | 100% |
| Rows still `Not Researched` | expected until Phase 2 |
| Rows with `vedastro_overlap=yes/partial` | use in comparator tests first |

## Unblock checklist for Registry v1

- [ ] Product owner confirms or replaces this provisional 96-row list
- [ ] Official names/order from the missing Section 8 paste reconciled
- [ ] Broad rows flagged for child decomposition (esp. TEC-015, TEC-023, TEC-037, TEC-047)
- [ ] No calculation coding treated as complete based on this provisional list alone

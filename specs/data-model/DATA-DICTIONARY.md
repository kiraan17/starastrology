# Canonical Data Dictionary (Draft v0.1)

**Phase:** 4  
**Status:** Draft — approve before creating production DB schemas  
**Principle:** Store raw calculations and evidence, not only final sentences.

## 1. Privacy classification

| class | Examples | Rules |
|---|---|---|
| `P0_public` | planet names, sign names, technique IDs | Free to log |
| `P1_config` | ayanamsa mode, house system, engine versions | OK in logs; no person link required |
| `P2_event` | question text category, event timestamps without identity | Minimize retention |
| `P3_birth` | birth date/time, place, coordinates, timezone | Encrypt at rest; access-controlled; deletable |
| `P4_identity` | user account, email, reviewer identity | Auth boundaries; separate from anonymous calc where possible |
| `P5_restricted_output` | medical/financial/longevity research outputs | Research-only stores; no customer default exposure |

Birth data deletion must remove or anonymize linked snapshots per retention policy (TBD in ops handbook).

## 2. Core entities

### 2.1 Subject / input

| field | type | unit/allowed | privacy | notes |
|---|---|---|---|---|
| `input_id` | UUID | — | P1 | |
| `input_kind` | enum | birth / question / event / transit_ref | P1 | |
| `local_datetime` | datetime | civil local | P3 | As stated by user |
| `timezone_id` | string | IANA TZ | P3 | |
| `utc_datetime` | datetime | UTC | P3 | Derived |
| `julian_day` | float | JD UT | P3 | Derived |
| `latitude` | float | degrees | P3 | |
| `longitude` | float | degrees | P3 | |
| `location_label` | string | — | P3 | |
| `birth_time_uncertainty_minutes` | float\|null | minutes | P3 | Gates D150 etc. |
| `manual_inputs` | object\|null | ritual counts, etc. | P3/P2 | Never fabricated |

### 2.2 Chart configuration

| field | type | allowed | privacy | notes |
|---|---|---|---|---|
| `config_id` | UUID | — | P1 | |
| `ayanamsa` | enum | lahiri / kp / ... | P1 | Extensible |
| `house_system` | enum | whole_sign / placidus / sripati / ... | P1 | |
| `node_type` | enum | mean / true | P1 | |
| `ephemeris_mode` | string | SE mode id | P1 | |
| `ephemeris_files_version` | string | — | P1 | |
| `calc_library_version` | string | — | P1 | |
| `engine_versions` | map | engine→version | P1 | |
| `variant_config` | map | variant keys | P1 | From variant log |

### 2.3 Calculation snapshot

| field | type | privacy | notes |
|---|---|---|---|
| `snapshot_id` | UUID | P1 | Immutable once written |
| `input_id` | UUID | P3 link | |
| `config_id` | UUID | P1 | |
| `planets[]` | PlanetPosition | P3 | longitude, speed, retro, etc. |
| `cusps[]` | CuspPosition | P3 | |
| `angles` | object | P3 | Asc/MC… |
| `nakshatras[]` | object | P3 | |
| `vargas` | object | P3 | keyed by division |
| `panchanga` | object\|null | P3 | |
| `dashas` | object\|null | P3 | |
| `created_at` | datetime | P1 | |

**Immutability:** never overwrite; new calc → new snapshot.

### 2.4 PlanetPosition

| field | type | unit |
|---|---|---|
| `planet` | enum | Sun…Ketu |
| `longitude_sidereal_deg` | float | 0–360 |
| `longitude_tropical_deg` | float\|null | 0–360 |
| `latitude_deg` | float | |
| `speed_longitude` | float | deg/day |
| `is_retrograde` | bool | |
| `sign` | enum | Aries…Pisces |
| `sign_degree` | float | 0–30 |

### 2.5 Rule / technique metadata

| field | type | notes |
|---|---|---|
| `technique_id` | string | TEC-### |
| `rule_id` | string | RULE-### |
| `rule_version` | string | semver or monotonic |
| `school` | string | |
| `source_ids[]` | string | SRC-### |
| `variant_id` | string\|null | VARIANT-### |
| `status` | status enum | workflow |

### 2.6 Evidence / engine result

| field | type | notes |
|---|---|---|
| `result_id` | UUID | |
| `snapshot_id` | UUID | |
| `engine` | string | Parashara/KP/… |
| `technique_id` | string | |
| `rule_id` | string | |
| `rule_version` | string | |
| `outcome` | enum | matched / failed / cancelled / skipped / inconclusive |
| `conditions_evaluated[]` | object | input values + boolean |
| `modifiers[]` | object | strength adjustments |
| `confidence` | object | quality, agreement, birth-time accuracy |
| `safety_level` | enum | |
| `notes` | string | machine-readable preferred |

### 2.7 Prediction candidate (orchestration)

| field | type | notes |
|---|---|---|
| `candidate_id` | UUID | |
| `domain` | string | career/marriage/… |
| `window_start` / `window_end` | datetime\|null | |
| `support_result_ids[]` | UUID | |
| `oppose_result_ids[]` | UUID | |
| `mixed_result_ids[]` | UUID | |
| `score` | object | config-weighted, not universal truth |
| `claim_restriction` | enum | none/disclaimer/blocked |

### 2.8 Verification & review

| field | type | notes |
|---|---|---|
| `test_case_id` | string | |
| `expected` / `actual` | json | |
| `pass` | bool | |
| `review_id` | UUID | |
| `reviewer_id` | string | P4 |
| `decision` | enum | approve/reject/comment |
| `comment` | text | |

## 3. Entity relationship (logical)

```text
SubjectInput 1──* CalculationSnapshot
ChartConfig  1──* CalculationSnapshot
CalculationSnapshot 1──* EngineResult(Evidence)
Technique/Rule(*version) 1──* EngineResult
EngineResult *──* PredictionCandidate
Source *──* Rule
VariantDecision *──* Rule/Config
TestCase/Review *──* Snapshot/Result
```

## 4. Schema implementation note

Do **not** create SQL migrations until this dictionary is approved. Prefer JSON-serializable snapshot documents plus relational indexes for IDs/status/audit.

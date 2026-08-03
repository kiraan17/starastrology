# Source Register Process

**Phase:** 2  
**Status:** Draft process — ready to receive expert-approved entries  
**Rule:** An LLM is never an astrology source. VedAstro is a comparator, not a classical source.

## Purpose

Prevent invented or mixed astrology rules by binding every interpretive technique to approved material.

## Source classes

| class | Meaning | May implement interpretive rules? |
|---|---|---|
| `classical_text` | Named traditional text / commentary | Yes, after expert variant decision |
| `modern_author` | Named modern author/course | Yes, if explicitly selected |
| `product_rule` | Bhava360 business/safety rule | Yes, as product decision |
| `ephemeris_algorithm` | Swiss Ephemeris / kernel algorithm docs | Calculation only |
| `comparator_software` | VedAstro, desktop software, etc. | **No** — comparison/tests only |
| `llm_generated` | Model output | **Never** as authority |

## Mandatory fields for every source entry

| Field | Description |
|---|---|
| `source_id` | Permanent ID, e.g. `SRC-001` |
| `title` | Book/course/doc title |
| `author_or_body` | Author, school, or organization |
| `class` | One of the classes above |
| `tradition_tags` | Parashara, KP, Jaimini, Nadi, … |
| `edition_or_url` | Edition, translator, URL, ISBN if known |
| `citation_grain` | chapter / verse / page / lesson granularity available |
| `permission_notes` | copyright / quotation limits |
| `reviewer` | Domain reviewer name/role |
| `approval_status` | Candidate / Approved / Rejected / Deferred |
| `linked_techniques` | Technique IDs |
| `notes` | Caveats |

## Variant decision rule

When authors disagree:

1. Create a `VARIANT-###` record in `sources/variants/`
2. List competing options with source citations
3. Product + tradition reviewer choose `supported`, `unsupported`, or `research_only`
4. Engines read the chosen variant ID — never a hidden default

## Stop condition for implementers

If a rule lacks an Approved source or explicit `product_rule`, mark `Source Needed` and stop that rule.

# Internal Verification Console (Phase 22 / CONSOLE-01)

**Status:** Implemented (functional, intentionally unpolished)  
**Entry points:**
- `uvicorn console.app:app --app-dir .` from repo root
- or `bhava360-console` after `pip install -e '.[console]'`

## What it shows

- Birth/event input + ayanamsa/house configuration
- Planet longitudes, signs, nakshatras, rasi houses, dignity
- Ascendant summary
- Vimshottari balance
- Parashara rule outcomes with versions/sources/activation
- Ashtakavarga SAV total
- KP config isolation + Sun lord chain (when selected)
- Raw JSON report + `/export.json`

## What it deliberately does not include

- Consumer branding, animations, prediction cards
- Subscriptions, onboarding, marketing
- LLM narrative generation

## Tests

`tests/unit/test_console.py` covers health, HTML form, JSON API, and KP path.

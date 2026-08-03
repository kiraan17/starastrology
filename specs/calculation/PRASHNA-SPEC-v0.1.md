# Prashna scaffold (P19b)

**Module:** `bhava360.engines.prashna`  
**Engine:** `Prashna` `0.1.0-sphuta-scaffold`  
**Status:** Candidate  
**Techniques:** TEC-086 (thin), TEC-088 (manual passthrough)

## Scope

### Calculable
- Query-time chart (`input_kind=prashna`)
- **Trisphuta** = Lagna + Moon + Sun
- **Gulika** = Lagna at start of daytime Gulika kala (Candidate)
- **Chatusphuta** = Trisphuta + Gulika
- Arudha Lagna of Prashna Lagna (same pada rule as Jaimini A1)

### Manual (never fabricated)
- Ashtamangala shell/cowrie counts — operator-supplied only
- Missing counts → `awaiting_manual_input`

## Deferred

- Full Prashna Marga interpretive pack (SRC-011)
- Advanced sphutas / Tamil Aroodha (TEC-087)
- Ashtamangala verdict tables
- KP Horary number path

## Hard rule

Manual systems stay manual — engine must not invent ritual counts from chart data.

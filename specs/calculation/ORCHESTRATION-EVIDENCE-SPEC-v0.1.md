# Evidence / conflict orchestration scaffold (P23a)

**Module:** `bhava360.engines.orchestration`  
**Engine:** `Orchestration` `0.1.0-evidence-scaffold`  
**Status:** Candidate  
**Technique:** TEC-096

## Scope

Consumes verification engine sections and produces:

| Output | Rule |
|--------|------|
| Evidence envelope | Normalized items from Parashara/KP/Lal Kitab/SA/Rectification (extensible) |
| Product weights | Candidate per-school display weights × outcome score |
| Conflict groups | Cross-school groups kept separate (`blended=false`, `resolution=keep_separate`) |
| Safety gates | Restricted visible; prohibited blocked |
| Prediction candidates | Per-domain support/oppose lists; `blended_total=null` |

Stamp: `evidence_orchestration_candidate_v1`

## Policy

- SRC-015 school isolation — never silently blend
- SRC-014 safety claim policy — restricted/prohibited gated
- Orchestration never replaces school engines

## Deferred

- Approved weight schedules
- Full domain taxonomy
- Expert review hooks
- Evidence persistence

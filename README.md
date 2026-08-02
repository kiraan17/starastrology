# BHAVA360 / starastrology

Deterministic astrology **backend** programme. Customer frontend is out of scope until backend validation gates pass.

## Start here

1. [Project charter](docs/requirements/PROJECT-CHARTER.md)
2. [Controlling requirements v1.0](docs/requirements/BHAVA360-Backend-Requirements-v1.0.md)
3. [AI instructions](AGENTS.md)
4. [Status workflow](docs/status/STATUS-WORKFLOW.md)
5. [Technique registry](registry/TECHNIQUE-REGISTRY.md) *(blocked on 96-item inventory)*
6. [Build plan using VedAstro as reference](docs/architecture/BUILD-PLAN-VEDASTRO-REFERENCE.md)
7. [Initial backlog](backlog/INITIAL-BACKLOG.md)

## Current phase

**P12b — Ashtakavarga Shodhana / Sodhya Pinda done**

Trikona + Ekadhipatya (+ SAV Mandala) reductions and Sodhya Pinda in `bhava360.engines.ashtakavarga` (`0.2.0-shodhana`). Console shows reduced SAV total and Sodhya Pinda.

## Principles (short)

- Deterministic calculation and rules before any generative explanation
- Independent astrology schools (Parashara, KP, Jaimini, Nadi, …)
- Traceable, versioned results
- Internal verification console only — not the final product UI
- **Jaimini** is the astrology system; **Gemini** is an AI product name

## Disclaimer

Astrology interpretations are not established scientific predictions. Product copy must not present medical, legal, financial, safety or longevity conclusions as certain facts or professional advice.

This interpretation is for entertainment purposes only.

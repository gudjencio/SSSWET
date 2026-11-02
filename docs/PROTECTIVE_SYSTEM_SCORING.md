# Protective System Scoring

SSSWET uses an evidence-gated scoring model to compare protective-system and assistive-exoskeleton development candidates without turning missing information into artificial scores.

## Purpose

The score is a research prioritisation aid. It does **not** certify a product, establish a protection rating, prove a system is safe for deployment, or indicate combat effectiveness.

The model can be used for systems such as:

- Aegis Modular
- Bastion Impact
- Atlas Assist
- Lifeline Rescue
- Sentinel Environment
- Guardian Monitor

The same framework can be applied to later revisions when their evidence is recorded separately.

## Dimensions

Each dimension uses a 0–5 scale and should be accompanied by evidence metadata.

| Dimension | Weight |
| --- | ---: |
| Protection evidence | 20% |
| Mass efficiency | 8% |
| Mobility | 8% |
| Energy efficiency | 5% |
| Thermal management | 8% |
| Maintainability | 8% |
| Safety | 20% |
| Human factors | 8% |
| Cost efficiency | 5% |
| Evidence maturity | 10% |

Safety and documented protection evidence receive the strongest weights. Cost cannot compensate for an inadequate safety case.

## Evidence states

Every dimension may be marked as:

- `unknown` — no defensible value is available
- `target` — a design objective, not an observed result
- `observed` — measured or documented in a defined configuration, with sources
- `verified` — independently checked evidence with sources

A target must never be presented as measured performance.

## Ranking gate

A candidate is rankable only when all ten dimensions have values and these gates are complete:

1. intended use is defined
2. relevant hazards are defined
3. a measurable test plan is defined
4. safety review is complete

Candidates that fail a gate are reported as `not_ready` rather than receiving a zero. This prevents missing evidence from being mistaken for poor engineering performance and prevents unsupported designs from winning a ranking by assumption.

## Interpretation

A high score means that the documented candidate currently presents a stronger evidence-backed development profile under the selected weighting. It does not mean that the candidate is certified, production-ready, medically validated, military-grade, bulletproof, blast-proof, chemical-proof, radiation-proof, or otherwise suitable for a specific hazard without configuration-specific independent testing.

## Development use

The scoring engine is intended to help the research team decide which candidate deserves further investigation. Before prototype work, the project should still document the intended use, hazard envelope, human factors, failure behaviour, test methods, regulatory requirements, lifecycle costs, and independent verification plan.

Protective applications may include lawful civil-protection, emergency, occupational, rescue, environmental-protection, and other defensive uses. Weapon design, weapon integration, targeting, and offensive autonomy are outside this framework.

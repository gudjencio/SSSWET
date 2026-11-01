# Research programme prioritisation framework

SSSWET uses a transparent, human-entered rubric to help teams compare research programmes when sufficient information is available.

## Criteria and weights

| Criterion | Weight |
| --- | ---: |
| Potential societal benefit | 20% |
| Ecological and animal benefit | 20% |
| Evidence maturity | 15% |
| Technical feasibility | 15% |
| Resource accessibility | 10% |
| Safety and legal readiness | 20% |
| **Total** | **100%** |

Each criterion is assessed from 0 to 5. A higher safety and legal readiness score means stronger safeguards and a clearer responsible pathway; it does not mean that risk is absent.

## Comparison rules

- Assessments must be based on documented reasons and current evidence.
- Missing values remain unassessed. They are never silently converted to zero.
- A programme receives a comparable overall score only when all six criteria are assessed.
- Only complete assessments appear in the ranked list. Incomplete assessments remain visible separately.
- Equal scores are ordered by programme identifier for deterministic presentation.
- The score is a weighted decision-support index, normalized to 0–100. It is not a probability, scientific confidence measure, feasibility guarantee or safety certificate.

## Governance

The framework does not automatically select projects, allocate donations, authorize experiments, approve products or determine funding. Human reviewers remain responsible for conflicts of interest, source quality, legal obligations, ethics, safety and periodic reassessment. A strong score cannot override a legal prohibition, an unresolved safety concern or the absence of required independent review.

The local API exposes the rubric at `/api/research-priority-framework`. The scoring functions are available to local research workflows; assessments are not automatically created from incomplete catalogue metadata.

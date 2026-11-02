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


## Recording assessments

The local interface includes a form for all 40 programme identifiers. Each submission requires a reviewer label and written rationale; evidence references can be added as URLs or citations. Scores may be left unassessed, in which case the entry remains incomplete and is excluded from the ranked comparison.

Assessment records are stored in the local SQLite research database as append-only history. A later submission becomes the current assessment for that programme without overwriting earlier entries. The assessment API is:

- `GET /api/research-priority-assessments` — current comparisons and recent history.
- `POST /api/research-priority-assessments` — append a new human-entered assessment.

Submissions are accepted only by the local engine from loopback clients and approved project origins. The browser interface must be connected to the local engine to save records. The public static site does not store assessments centrally, and clearing browser cache does not replace the local database backup.

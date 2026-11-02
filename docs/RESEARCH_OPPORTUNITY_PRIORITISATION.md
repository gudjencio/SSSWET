# Research opportunity prioritisation

This module complements the existing programme-priority rubric. The original rubric considers societal and ecological value; this opportunity index focuses on what research action may be most productive next.

## Dimensions

| Dimension | Weight |
| --- | ---: |
| Evidence maturity | 20% |
| Technical feasibility | 20% |
| Readiness of the next experiment or test | 15% |
| Resource efficiency | 15% |
| Safety and legal readiness | 20% |
| Supported downstream leverage | 10% |
| **Total** | **100%** |

Human reviewers supply five scores from 0 to 5. The sixth score is derived from the number of distinct downstream programmes connected by supported `prerequisite` or `enables` relationships, capped at 5. Proposed, rejected, and superseded edges do not contribute.

A reviewer must explicitly set `dependency_review_complete` to true before the graph-derived score is considered. If dependency coverage has not been reviewed, the leverage dimension remains unknown and the programme is not ranked. Missing scores are never converted to zero.

## Interpretation and safeguards

The resulting 0–100 index is an advisory comparison of research opportunities, not a probability of success, scientific confidence, feasibility guarantee, safety certificate, or funding instruction. A low safety/legal readiness score should trigger human review and may block work regardless of the total. Legal, ethical and safety constraints take precedence over ranking.

The engine does not autonomously discover sources, conduct experiments, assess costs, or assign scores. Reviewers must document the basis for each input through the project's assessment workflow. Reassessments should be append-only and periodically reviewed as evidence changes.

## Python API

```python
from ssswet_core.research_opportunity import evaluate_research_opportunity

result = evaluate_research_opportunity(
    programme_id="energyStorage",
    inputs={
        "evidence_maturity": 3,
        "technical_feasibility": 2,
        "next_experiment_readiness": 4,
        "resource_efficiency": 3,
        "safety_legal_readiness": 4,
        "dependency_review_complete": True,
    },
    dependency_graph=engine.technology_dependencies.graph(),
)
```

The example values are illustrative only and are not assessments of an actual SSSWET programme.

# Independent reviewer selection safeguards

This module creates a deterministic proposal for selecting reviewers from an explicitly supplied candidate pool. It does not contact agents, verify identities, prove independence or adjudicate scientific claims.

## Safeguards

- Excludes the lead researcher, prior reviewers and prior reviewer campaigns when those identifiers are supplied.
- Excludes candidates whose conflict declaration is not `none_declared`.
- Avoids selecting two candidates from the same declared campaign.
- Prioritises complementary review roles using a fixed, inspectable order.
- Identifies overlap with prior evidence references so it can be disclosed rather than silently ignored.
- Reports a shortfall when the candidate pool cannot meet the requested panel size. It never lowers the requirement silently.

## Interpretation

A proposed panel is not an executed assignment. Distinct agent IDs, roles and campaigns are administrative separation signals, not proof of independence. Shared institutions, funding, authorship, data provenance, personal relationships and other conflicts may not be represented in the supplied candidate data. Human review must assess these factors before an assignment is accepted.

The selector does not invoke language models or claim that agents have independently examined evidence. Review submissions must be separately recorded through the scientific review board, with rationale, methods assessment, limitations, evidence references and conflict declarations.

## Example

```python
from ssswet_core.review_assignment import (
    IndependentReviewerSelector, ReviewerCandidate,
)

proposal = IndependentReviewerSelector().propose(
    [
        ReviewerCandidate("reviewer-01", "independent_verifier", "campaign-a"),
        ReviewerCandidate("reviewer-02", "data_analyst", "campaign-b"),
    ],
    excluded_reviewer_ids={"original-reviewer"},
    prior_source_refs={"source-123"},
    required_count=2,
)
```

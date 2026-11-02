# Research decision lineage

SSSWET's research decision ledger preserves how a research position changes over time. It complements technology dossiers, source-linked agent memories and peer review by keeping decision rationale and correction lineage explicit.

## What is recorded

Each decision event records a subject identifier, decision identifier, review status, rationale, actor, evidence references and reviewer identifiers. A replacement decision receives a new identifier and links to the decision it supersedes. The earlier record remains available and is marked as superseded in a separate event.

Supported review statuses are:

- `proposed`
- `supported`
- `challenged`
- `superseded`
- `withdrawn`
- `rejected`
- `unresolved`

Statuses describe the recorded review process. They are not a scientific truth score, certification, or substitute for expert judgement.

## Integrity safeguards

- Events are append-only; database triggers reject updates and deletions.
- Corrections create a new decision instead of rewriting the previous rationale.
- Supersession requires an existing decision on the same subject and supporting evidence references.
- Status transitions are constrained; terminal decisions cannot be reopened.
- Retrieval is bounded and retains provenance and reviewer identifiers.
- The ledger does not automatically resolve disagreements or promote a claim to scientific fact.

## Python API

```python
from ssswet_core.persistence import SQLiteResearchStore
from ssswet_core.research_decision_ledger import ResearchDecisionLedger

ledger = ResearchDecisionLedger(SQLiteResearchStore("research.sqlite3"))
decision = ledger.record(
    subject_id="claim-42",
    rationale="Initial interpretation pending independent review.",
    actor_id="researcher-1",
    evidence_refs=["doi:10.example/source"],
    reviewer_ids=["reviewer-2"],
)
ledger.transition(
    decision["decision_id"],
    status="challenged",
    rationale="A separate dataset reports a different outcome.",
    actor_id="reviewer-2",
    evidence_refs=["dataset:run-18"],
)
```

The ledger records supplied information. It does not authenticate source material, verify reviewer independence, or establish scientific validity.

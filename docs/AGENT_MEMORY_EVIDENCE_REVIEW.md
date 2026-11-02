# Evidence review states for agent memory

SSSWET agent memories preserve research notes and source references. This extension records whether a stored note's source context has been rechecked, needs reassessment, has been superseded, or has been withdrawn.

## Review states

- `unreviewed`: no review event has been recorded for the memory.
- `recheck_required`: a reviewer has identified a reason to reassess the note or its source.
- `revalidated`: a reviewer recorded a recheck and supplied a reference to the review evidence.
- `superseded`: the note is no longer the current working record; retain it for historical traceability.
- `withdrawn`: the note has been withdrawn from current use.

These are workflow annotations, not automated judgements of truth, source quality, or scientific validity. The system does not infer staleness from age alone.

## Integrity and transitions

Review events are append-only and protected against database updates and deletions. Each event requires a reviewer identifier, rationale, and evidence reference. A memory can move from `unreviewed` to a review state; `recheck_required` can be resolved as `revalidated`, `superseded`, or `withdrawn`; a revalidated note can be flagged again if new information appears. Superseded and withdrawn states are terminal.

Search results expose the latest recorded review state and its provenance. Notes without review events remain explicitly labelled `unreviewed`; they are not silently treated as current.

## Python API

```python
memory = engine.agent_identities.remember(
    agent_id="mira-01",
    role="general_researcher",
    content="A test result relevant to the current research question.",
    source_reference="doi:10.example/source",
)
engine.record_agent_memory_review(
    memory_id=memory["memory_id"],
    status="recheck_required",
    rationale="A newer protocol may affect comparability.",
    reviewer_id="elias-01",
    evidence_reference="standard:revision-notice",
)
results = engine.search_team_memories("test result protocol comparability")
```

Retrieval relevance and review state are navigation aids. Before relying on a memory, researchers must inspect its source and the review evidence in context.
# Cross-agent research memory retrieval

SSSWET can retrieve source-linked notes across the research team for a shared research question.

## Behaviour

- Searches each selected agent's bounded recent memory window using the existing relevance ranking.
- Returns the strongest matches across agents with a deterministic tie-break order.
- Preserves agent identity, role, source reference, timestamp, matched terms and retrieval score.
- Does not merge conflicting notes into a single conclusion or promote a note to verified evidence.
- Supports an optional allowlist of agent IDs and a bounded result count.
- Requires a persistent research store; empty queries return no results.

## Python API

```python
results = engine.search_team_memories(
    "thermal protection insulation ageing",
    limit=12,
)
```

To restrict the search to selected agents, pass `agent_ids=["mira-01", "asha-01"]`.

Retrieval relevance is a navigation aid, not a scientific confidence score. Every result must be rechecked against its source and current context before use.

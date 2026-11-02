# Research Knowledge Graph

SSSWET maintains an append-only graph for connecting research artefacts and tracing downstream impact when evidence or interpretations change.

## Scope

The graph can represent:

- memories
- claims
- decisions
- experiments
- evidence
- technology dossiers
- hypotheses

Relationships include `supports`, `contradicts`, `informs`, `tests`, `supersedes`, `documents`, `motivates`, `depends_on`, and `derived_from`.

Edges are directed from an upstream artefact to a downstream artefact. For example, evidence can `support` a claim, and a claim can `inform` a decision. `impact()` follows active downstream relationships to identify artefacts that may need review after an upstream change.

## Integrity rules

- Nodes and relationships are append-only.
- Every relationship requires an evidence reference and actor identifier.
- Relationship states are `proposed`, `reviewed`, or `withdrawn`.
- `supersedes` and `derived_from` relationships cannot form cycles.
- Impact queries are bounded by depth and result count.
- Withdrawn relationships are excluded from impact traversal.
- The graph records associations; it does not establish scientific truth, validation, readiness, or safety.

## Example

```python
graph.add_node(
    node_id="evidence:thermal-test-01",
    node_type="evidence",
    label="Thermal cycling result",
    actor_id="mira",
    source_refs=["lab-record:thermal-test-01"],
)
graph.add_node(
    node_id="claim:material-retention",
    node_type="claim",
    label="Material retained measured strength",
    actor_id="mira",
    source_refs=["lab-record:thermal-test-01"],
)
graph.link(
    source_id="evidence:thermal-test-01",
    target_id="claim:material-retention",
    relation="supports",
    actor_id="elias",
    rationale="The recorded test is relevant to the claim.",
    evidence_refs=["review:thermal-test-01"],
)

impact = graph.impact("evidence:thermal-test-01", max_depth=5, limit=100)
```

This graph complements the technology dependency graph: the dependency graph models technology-level prerequisites and constraints, while this graph models individual research artefacts and their provenance relationships.

# Technology Dependency Graph

SSSWET's technology dependency graph connects existing technology dossiers through explicitly recorded relationships.

## Relationship types

- `prerequisite`: a programme may depend on another programme.
- `enables`: progress in one programme may enable work in another.
- `shares_component`: programmes may share a component, method, or infrastructure.
- `constrains`: a documented limitation in one programme may constrain another.
- `informs`: evidence or methods from one programme may inform another.

For prerequisite relationships, the direction is **prerequisite → dependent programme**.

## Evidence and review

Every relationship begins in the `proposed` state. A relationship can be marked `supported` only with source references and a distinct independent verifier. Reviews are append-only; rejected and superseded relationships remain in the historical record. Supported prerequisite edges are checked to prevent cycles.

The graph does not infer relationships from category membership, similar names, or assumptions. It contains only relationships explicitly submitted through the registry. An empty graph means no relationships have yet been entered, not that the programmes are independent.

## API

```python
graph = engine.technology_dependencies
proposal = graph.add_relation(
    prerequisite_id="energyStorage",
    dependent_id="plasmaPropulsion",
    relation_type="prerequisite",
    rationale="Describe the testable dependency and its scope.",
    actor_id="researcher-agent",
    source_refs=["https://example.org/source"],
)
reviewed = graph.review_relation(
    relation_id=proposal["relation_id"],
    state="supported",
    rationale="Independent assessment and limitations.",
    actor_id="review-agent",
    verifier_actor_id="independent-reviewer",
    source_refs=["doi:..."],
)
```

The example identifiers illustrate API usage only; they do not assert a real SSSWET dependency. Use only source references that have actually been examined.

`graph()` returns relationship history and counts. `graph(include_unverified=False)` returns supported relationships only. `dependencies_for(technology_id)` lists prerequisite relations for a programme.

The graph records research assertions; it does not certify scientific validity, feasibility, safety, or commercial readiness.

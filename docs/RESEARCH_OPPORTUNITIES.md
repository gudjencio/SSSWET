# Research opportunity synthesis

SSSWET's local research core exposes a unified, read-only view of two existing
discovery signals:

- **Research gaps**: missing recorded links around hypotheses, questions,
  experiments and findings, plus explicitly recorded contradictions.
- **Interdisciplinary links**: lexical overlaps between knowledge-graph records
  belonging to different campaigns.

The endpoint is:

`GET /api/research-opportunities`

An optional `limit` parameter controls the number of returned items (1–500).
Each opportunity includes a stable identifier, its type, a review priority,
the related graph-node and campaign identifiers, source signal references,
and a suggested next action. Gap opportunities link to interdisciplinary
opportunities that share one or more graph nodes.

## Interpretation

These results are review leads, not discoveries or validated scientific
relationships. Gap analysis describes omissions in the recorded graph; it
cannot establish that evidence is absent from the wider literature. The
interdisciplinary detector uses normalized lexical overlap, which can produce
coincidental matches and miss synonyms or deeper conceptual relationships.
Scores are ranking heuristics, not probabilities or confidence estimates.

The endpoint is read-only. It does not create tasks, modify graph edges,
promote verification states, execute experiments, or establish scientific
validity. Researchers should inspect primary sources, provenance, methods,
assumptions, uncertainty and relevant safety requirements before acting.

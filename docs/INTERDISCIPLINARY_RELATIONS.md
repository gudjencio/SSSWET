# Interdisciplinary relation discovery

The local research engine can identify possible links between knowledge-graph
records belonging to different campaigns. The current implementation uses
transparent normalized lexical Jaccard overlap over node labels and
descriptions.

Run the read-only report through the local API:

`GET /api/research-relations?limit=100&minimum_shared_terms=2`

Each suggestion includes the two record identifiers, campaign identifiers,
shared terms, overlap score and method. Existing explicit relationships are
excluded from repeat suggestions.

This is a discovery aid, not semantic reasoning or scientific evidence.
Lexical matches can be coincidental and can miss synonyms or deeper conceptual
connections. Suggestions never create graph edges, tasks, transfers, or
verified findings. Researchers must inspect context, methods, source
provenance and uncertainty before recording any relationship.

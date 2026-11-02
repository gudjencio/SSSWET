# Research Knowledge Observatory

The Research Knowledge Observatory provides a read-only consolidated view of records already held by SSSWET.

## Included indicators

- Number of research technology programmes represented in the technology registry.
- Explicit knowledge-graph nodes and recorded relationships.
- Versioned laboratory protocols, research runs and comparisons.
- Evidence dossiers and their recorded source, run, comparison and review-event counts.
- Recorded technology maturity categories and programmes without journal entries.
- Laboratory record-integrity metadata.

## API

When the research API is running, request:

```http
GET /api/research-observatory?limit=200
```

The limit must be an integer from 1 to 500. The response summarizes existing registries; it does not create records or modify verification states.

## Interpretation and limitations

A count of zero means no matching record was returned from the queried registry and limit. It does not prove that no external research exists. Technology maturity is a classification of recorded journal entries, not a feasibility assessment. Record-integrity checks do not establish that an experiment was correctly performed. Dossier review and verification remain distinct.

The observatory does not rank scientific truth, resolve reviewer disagreements, authorize experiments, execute experiments or certify product readiness.

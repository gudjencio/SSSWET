# Scientific-memory intelligence and temporal-quality workflows

This release adds bounded retrieval, agent-context preparation, integrity review, duplicate triage, contradiction dossiers and reproducible exports for the scientific-memory store. It also adds local temporal-coverage diagnostics, auditable GPS-track segmentation and a privacy-reduced Virtual Time Travel export.

These tools organize and inspect records. They do not certify scientific claims, establish source independence, infer events during unrecorded intervals, or guarantee anonymization.

## Ten delivered improvements

1. **Field-weighted scientific-memory retrieval.** `GET /api/scientific-memory/search?q=<terms>` ranks topic, statement and campaign matches with explicit weights and an explainable score breakdown. It searches at most 500 records, returns at most 100, excludes superseded versions by default, and can include history with `include_history=true`. Contested records remain eligible. The score is a ranking signal, not a probability.
2. **Repeatable retrieval evaluation and latency measurement.** The core module exposes `evaluate_retrieval`, `compare_retrieval_cases` and `benchmark_memory_retrieval`. They report precision@k, recall@k, F1@k, MRR, nDCG@k, median latency and p95 latency. Benchmarks require labelled cases; a synthetic fixture demonstrates metric behaviour but is not evidence of general model or agent intelligence.
3. **Bounded agent context packets.** `GET /api/scientific-memory/context?q=<terms>` returns ranked records under a configurable approximate token budget (1–8,000) and item cap (1–50). Source, experiment, graph and provenance references remain attached. Statements are not silently truncated to fit.
4. **Evidence-link and provenance audit.** `GET /api/scientific-memory/integrity` reports unresolved source, experiment and graph references, declared provenance groups and ungrouped sources. A resolved identifier only proves that a local record exists. Missing overlap never proves independence.
5. **Non-destructive duplicate triage.** `GET /api/scientific-memory/duplicates?threshold=0.82` finds exact and near-duplicate current statements with shared terms and source-set differences. The comparison is bounded to 500 current records (at most 124,750 pairs). It counts all qualifying pairs while retaining only the requested top results in memory. It never merges, rewrites or deletes a memory.
6. **Contradiction review dossiers.** `GET /api/scientific-memory/conflicts` joins current memory links to explicit graph `contradicts` edges and provides a review checklist for methods, conditions, units, dates, uncertainty and provenance. It never changes a memory status or adjudicates the claim.
7. **Deterministic memory snapshots.** `GET /api/scientific-memory/snapshot` exports up to 500 immutable versions in stable order with a SHA-256 integrity digest. The response flags a possible truncation when the 500-record ceiling is reached. The core verifier detects accidental or subsequent content changes; a digest does not authenticate the author or establish scientific validity. Snapshot import is deliberately not provided.
8. **Temporal coverage diagnostics.** Virtual Time Travel Mapping now reports the number of timestamped observations, median sampling interval and longest intervals exceeding 15 minutes. A gap means no observation was stored; it is not evidence that an event happened or that interpolation is justified.
9. **Auditable GPS-track segmentation.** Map track lines use one shared, tested segmentation helper. It retains the existing limits (150 m reported accuracy, 15-minute gap, 5 km jump and 70 m/s speed) and adds invalid-coordinate rejection and explicit counts for rejected samples and segment breaks. It does not connect a line across a detected break. The page reuses one cached temporal analysis for the quality panel, model input and map rendering during each refresh, avoiding repeated sorting and distance calculations over the same local event list.
10. **Privacy-reduced local export.** The new export action leaves the existing full index export unchanged. The reduced copy rounds timestamps to the nearest minute, omits free text, sensor values and media, and removes coordinates by default. Users may explicitly include coordinates rounded to 0.001 degrees. This reduces detail but is not an anonymization guarantee; review the file before sharing.

## API reference

All new memory endpoints are read-only:

| Endpoint | Purpose | Main bounds |
|---|---|---|
| `GET /api/scientific-memory/search?q=...` | Explainable ranked retrieval | 500 records, 100 results |
| `GET /api/scientific-memory/context?q=...` | Agent context packet | 8,000 approximate tokens, 50 records |
| `GET /api/scientific-memory/integrity` | Reference and provenance audit | 500 memory versions, 500 experiments, 2,000 graph nodes, up to 8,000 graph edges |
| `GET /api/scientific-memory/duplicates` | Candidate duplicate review | 500 current records, configurable threshold |
| `GET /api/scientific-memory/conflicts` | Contradiction review dossiers | 2,000 graph nodes, up to 8,000 graph edges, 200 retained cases |
| `GET /api/scientific-memory/snapshot` | Versioned integrity snapshot | 500 memory versions |

Example:

```text
GET /api/scientific-memory/search?q=wave%20propagation&limit=20
GET /api/scientific-memory/context?q=wave%20propagation&token_budget=1600&max_items=12
GET /api/scientific-memory/duplicates?threshold=0.82&limit=50
```

## Acceptance criteria and regression controls

- Retrieval is deterministic for identical records and query, field weights are returned, superseded records are excluded unless requested, and graph-contested records are not silently suppressed.
- The evaluation functions return deterministic binary-relevance metrics. A labelled fixture compares a candidate ordering with a baseline ordering; it does not justify a broad quality claim.
- Context packets never exceed their declared approximate budget and preserve all provenance identifiers for every included record.
- Integrity and contradiction reports are read-only. Neither workflow changes scientific status, promotes findings, or infers source independence.
- Duplicate review is capped at 500 current records, performs at most 124,750 pair comparisons, and retains at most the requested 200 candidates. Conflict review also retains at most 200 cases. Neither path has a destructive merge or adjudication path.
- Snapshot verification checks record count and all digested fields. The snapshot is explicitly not a signature.
- No database schema, existing record, or IndexedDB record is changed by these read-only additions; persistent storage growth from the new analysis features is zero.
- The original `/api/scientific-memory`, lineage and full Virtual Time Travel index export remain available.
- GPS segmentation uses the prior map thresholds and adds coordinate validation. It does not create interpolated route points. The temporal-quality module accepts already-sorted local records to avoid redundant sorting, while normalizing unsorted external inputs by default.
- Privacy-safe export is an additional path; the full export and local IndexedDB records are not modified.

## Validation

The repository CI now runs:

```bash
cd core
python -m pytest -q tests/test_memory_intelligence.py tests/test_memory_intelligence_api.py
cd ..
node --check web/temporal-quality.js
node web/test-temporal-quality.cjs
```

The complete CI matrix remains responsible for the full Python and JavaScript regression suites. Latency values are environment-dependent and should be compared on the same runner, Python version and dataset size. No performance or intelligence gain should be claimed without repeated, comparable measurements.

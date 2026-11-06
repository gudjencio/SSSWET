# Research continuity and evidence review upgrades

This release strengthens the evidence intake and research continuity layer while preserving existing APIs.

## Ten independently useful improvements

1. **Strict evidence packet schema:** required fields, bounded content, structured limitations and stable source identifiers are checked before review.
2. **Source-record reconciliation:** optional source records are matched to cited source IDs; mismatches block review and unused records are surfaced.
3. **Provenance visibility:** declared provenance groups are counted and displayed as metadata, never treated as proof of independence.
4. **Reproducibility readiness:** protocol, dataset, run, method and limitations links receive separate checklist results.
5. **Deterministic packet fingerprints:** SHA-256 fingerprints support exact-content change detection; they are not signatures or authenticity proofs.
6. **Bounded batch intake:** up to 500 packets can be checked together, with aggregate blockers and duplicate packet-ID detection.
7. **Explainable freshness assessment:** finite half-life weights are accompanied by recency bands and review prompts without rewriting source claims.
8. **Transparent evidence rubric:** each quality dimension, weight and weak area is returned; a weak dimension can trigger review even when the aggregate score is high.
9. **Provenance-preserving memory compaction:** duplicate statements are compacted while source, experiment, graph and evidence references are unioned and revision IDs/states remain visible.
10. **Bidirectional knowledge-graph impact:** bounded incoming, outgoing or combined traversals and relationship filters make it possible to trace both upstream dependencies and downstream consequences.

## Acceptance and compatibility

- Existing evidence packet callers using the five required fields remain accepted; missing source-record detail is a warning unless source records were supplied and conflict with cited IDs.
- Existing evidence score weights and aggregate formula remain unchanged; review is more conservative when an individual dimension is weak.
- Existing graph traversal remains outgoing-only by default; direction and relation filters are opt-in.
- Memory compaction retains a bounded number of distinct statements while merging provenance references.
- All assessments explicitly avoid scientific adjudication. Passing a structural check is not proof of truth, independence, safety, feasibility or reproducibility.

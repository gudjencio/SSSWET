# Evidence packet quality gate

The packet validator is a deterministic intake check for human review. It validates record structure and traceability metadata; it does not decide whether a scientific claim is true, whether evidence is independent, or whether an experiment or deployment is safe.

## Ten capabilities

1. **Schema integrity:** validates the packet object and required title, summary, source IDs, method and limitations.
2. **Bounded text:** applies explicit field-size limits and normalizes whitespace for validation without rewriting stored source material.
3. **Structured limitations:** accepts a single limitations statement or a list of discrete limitations and rejects empty/malformed entries.
4. **Stable source identifiers:** checks source ID syntax, list bounds and duplicates.
5. **Source-record reconciliation:** optionally checks that supplied source records match referenced source IDs and flags unreferenced records.
6. **Provenance-group visibility:** counts declared provenance groups while explicitly avoiding an automatic claim of source independence.
7. **Reproducibility checklist:** reports whether protocol, dataset, run, method and limitations links are present.
8. **Deterministic fingerprint:** produces a SHA-256 fingerprint of the exact supplied JSON packet for change detection and reproducible review.
9. **Actionable review diagnostics:** separates blockers from warnings and reports review readiness without changing the legacy `valid_for_review` contract.
10. **Bounded batch validation:** validates up to 500 packets, reports duplicate packet IDs and aggregates readiness counts.

## Compatibility and limits

Existing callers that provide the five legacy required fields remain supported. Source records, protocol IDs, dataset IDs and run IDs are additive. If source records are not supplied, the validator warns that source identity has not been independently checked rather than rejecting a previously valid packet. Batch limits and packet byte limits are bounded to avoid unbounded work.

The fingerprint identifies exact supplied packet content; it is not a signature, timestamp authority, source authenticity check or proof of immutability. Provenance-group labels are caller-supplied metadata, not proof of independence. A packet passing validation is merely structurally ready for review.

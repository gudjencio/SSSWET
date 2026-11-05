# Research continuity improvements — 5 November 2026

This release adds ten bounded, deterministic helpers for scientific memory,
agent hand-offs and temporal evidence review.

1. Unicode NFKC/casefold query normalization with stable token ordering.
2. Weighted lexical retrieval with explicit campaign, status and provenance filters; retrieval is not scientific validation.
3. Exact duplicate grouping with merged source-ID visibility, without automatic record merging.
4. Same-topic opposite-polarity triage, explicitly marked as a review candidate rather than a proven contradiction.
5. Versioned memory snapshots with canonical SHA-256 integrity checks.
6. Snapshot validation for schema version, record count and unique memory identifiers.
7. Bounded agent hand-off packets that preserve source IDs, provenance, review state and explicit safety/review constraints.
8. ISO temporal parsing with UTC normalization, date-only precision labels and rejection of timezone-naive datetimes.
9. Inclusive temporal-window retrieval with finite uncertainty checks and deterministic ordering.
10. Temporal evidence review: bounded cadence-based observation-gap screening plus shared-source timeline comparison with combined uncertainty and no causal inference.

## Verification

The accompanying tests use deterministic synthetic records and timestamps. They verify
normalization, filtering, duplicate grouping, polarity triage, snapshot integrity,
handoff bounds, timezone handling, temporal selection, gap bounds and uncertainty
comparison. Passing tests demonstrate implementation behavior only; they do not
establish the truth of any scientific claim or the accuracy of an unrecorded-history
reconstruction.

## Limitations

- Lexical overlap and opposite-polarity rules are screening heuristics.
- Duplicate grouping is conservative and never deletes or merges records.
- Snapshot checksums detect accidental or unauthorized payload changes relative to
  the stored digest; they are not digital signatures or proof of authorship.
- Date-only timestamps are represented at UTC midnight and retain a date precision
  marker; consumers must not treat them as exact instants.
- Observation gaps describe missing records under a declared cadence, not missing
  events in the world.
- Agent hand-offs are context packets, not autonomous scientific approval.

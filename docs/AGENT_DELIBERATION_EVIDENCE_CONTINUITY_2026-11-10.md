# Agent Deliberation and Evidence Continuity

**Status:** experimental research-support utilities  
**Baseline:** main at 628c732839f1a916ceedea6d16efb7b35628118d  
**Immediate predecessor:** f570158bdcbd6145bca4753f109088fc2c714c0c  
**Scope:** ten independent capabilities; no existing database, payment, customer, credential, or legal-policy changes.

## Why this change exists

The existing core already contains scientific memory, peer review, reviewer selection, source-independence helpers, evidence dossiers, contradiction comparison and decision ledgers. Those components are useful individually, but there was no single, typed workflow for preserving claim context, comparing explicit competing predictions, inspecting shared source dependencies, preparing a blind packet, measuring agreement against an adjudicated reference set, mapping arguments, decomposing disagreement, detecting changed review dependencies and assembling a non-voting synthesis.

This update adds those missing research-support operations as separate importable modules. It does not replace or silently rewrite the existing memory, peer-review or review-board records.

## Ten functional improvements

1. **Versioned claim contracts** (claim_specification.py). Claims now have explicit scope, conditions, population, comparator, unit, timeframe, outcome, method, uncertainty note and evidence references. Context comparability excludes the asserted value, so differing values can be compared only when declared contexts match. Fingerprints are deterministic and version chains are checked for gaps or incorrect supersession.
2. **Competing-hypothesis test matrix** (hypothesis_matrix.py). Researchers declare predictions and disconfirming values; observations are matched only on exact normalized variable and condition fields. Negative, mixed and untested outcomes remain distinct and retained.
3. **Explicit source-lineage graph** (source_lineage.py). Shared dataset IDs, author groups, funder groups and parent-source links form conservative dependency clusters. Publisher/domain similarity alone is deliberately ignored. Cycles and missing parent references are surfaced.
4. **Claim-level evidence coverage** (evidence_coverage.py). Supporting, challenging, mixed and inconclusive records are counted separately. Where source metadata exists, corroboration is counted by lineage cluster rather than raw citation count. Missing provenance and coverage gaps remain visible; no aggregate truth score is produced.
5. **Blinded review packet preparation** (blind_review_packet.py). Declared contributor/campaign identity fields are replaced with deterministic salted pseudonyms. Evidence IDs and source references are preserved; the unblinding map is returned separately. Unknown identity-like fields generate warnings.
6. **Reviewer agreement calibration** (reviewer_calibration.py). Multi-class confusion matrices, agreement, Cohen's kappa, macro-F1, Wilson intervals and abstention rates are computed only against explicitly human-adjudicated reference cases. Small samples are flagged; reviewers are not ranked.
7. **Typed argument maps** (argument_map.py). Claims, evidence, assumptions, limitations and methods are connected with declared relations. Missing endpoints, inferential cycles, unsupported claim nodes and orphan evidence are reported. Path tracing is depth- and count-bounded.
8. **Disagreement decomposition** (disagreement_analysis.py). Declared differences in scope, method, measurement, population, timeframe, assumptions and analysis plan are shown alongside position counts and shared source overlap. No vote or automatic resolution occurs.
9. **Review dependency-change triggers** (reassessment_triggers.py). Source and dataset digests, method versions, safety-review versions and memory-version IDs are compared across snapshots. Added, changed and missing dependencies recommend reassessment; a missing reference is not assumed deleted.
10. **Dissent-preserving synthesis** (deliberation_synthesis.py). A deterministic, SHA-256-fingerprinted report preserves every reviewer position, evidence gap, disagreement and re-review trigger. It does not use majority voting, select a winning claim or authorize operational use.

## Acceptance criteria and regression risks

| Capability | Acceptance criterion | Regression risk and control |
|---|---|---|
| Claim contracts | Equivalent context produces the same comparability key; unit/scope differences do not compare; version gaps and bad parent links fail validation | More explicit fields may expose previously implicit context. Existing claim records are not migrated. |
| Hypothesis matrix | Exact declared matches produce consistent/challenged/mixed/untested states; negative findings remain present | Exact matching may leave semantically equivalent wording unmatched. No fuzzy matching is attempted. |
| Source lineage | Explicit shared dataset/author/funder/parent links cluster; same publisher alone does not | Missing lineage metadata can overstate independence. Output says independence is not certified. |
| Evidence coverage | Duplicate citations from one lineage group count once for independent support; unknown provenance is reported | A source can still share undisclosed data. No claim of complete dependency detection. |
| Blind packets | Stable pseudonyms for a fixed salt; packet excludes declared identity fields; source IDs survive | Text and unknown metadata can identify authors. Warnings and a no-anonymity-guarantee flag remain. |
| Reviewer calibration | Metrics match hand-computed fixtures; abstentions are separate; unadjudicated references are rejected | Reference labels may be fallible. Metrics are agreement with the supplied reference only. |
| Argument maps | Missing endpoints and inferential cycles fail; evidence paths are bounded and traceable | Declared links can be wrong. Paths are not proof. |
| Disagreement | Context/method differences and shared source overlap remain visible | Declared fields may be incomplete; no automatic causal explanation is inferred. |
| Reassessment | Added, changed and missing dependencies are distinguished | Missing is not deletion; the tool never launches a review or changes a status. |
| Synthesis | Input order does not change the digest; dissent and unresolved items are retained; no majority vote | Summaries can omit unprovided facts; all submitted review records remain attached. |

## Public API modules

- ssswet_core.claim_specification
- ssswet_core.hypothesis_matrix
- ssswet_core.source_lineage
- ssswet_core.evidence_coverage
- ssswet_core.blind_review_packet
- ssswet_core.reviewer_calibration
- ssswet_core.argument_map
- ssswet_core.disagreement_analysis
- ssswet_core.reassessment_triggers
- ssswet_core.deliberation_synthesis

All inputs are explicit dictionaries or immutable dataclasses. Limits are enforced in code: 2,000 claim versions, 100 hypotheses, 2,000 observations, 2,000 source records, 5,000 evidence records, 100 blind-packet documents, 1 MB per blind packet, 2,000 reviewer cases, 2,000 argument nodes, 10,000 argument edges, 2,000 disagreement records and 5,000 dependencies per snapshot field.

## Measured evaluation and comparison with previous behaviour

The previous main had no integrated claim-contract/hypothesis/lineage/blind-review/calibration/argument-map/reassessment/synthesis pipeline. It did have adjacent utilities such as scientific_memory, peer_review, review_assignment, source_independence, evidence_packet_validator and scientific_review_board; those remain unchanged. The new test fixtures measure deterministic behaviour and expected outputs rather than claiming that an agent became more intelligent.

The dedicated benchmark workflow reports median and p95 latency for synthetic workloads and packet bytes. Its 5-second per-operation ceiling is a broad regression guard, not a performance-gain claim. Results are synthetic and must not be treated as real-world throughput guarantees.

## Safety, privacy and scientific limitations

- These modules do not generate facts, browse external literature, execute agents, contact reviewers, run experiments or make decisions.
- Human-adjudicated reference labels are not ground truth. Reviewer agreement does not certify expertise, independence or competence.
- A blinded packet is not guaranteed anonymous. Free text, citations and unknown fields can identify authors. Review the warnings and source text before sharing.
- Source lineage is only as complete as declared metadata. Common publisher or domain is not used as a proxy for independence.
- Coverage counts and argument paths do not establish truth, causality, reproducibility or safety.
- A reassessment trigger is a review prompt, not a deletion, status change or automatic review.
- The synthesis preserves dissent and does not decide which reviewer is correct.
- Protective/rescue research remains subject to qualified domain review, human factors, safety, ethics, legal requirements and appropriate real-world validation. These utilities do not certify equipment or authorize deployment.

No new runtime dependency is required. Existing database schemas and stored research records are not modified.


## CI evidence — 10 November 2026

The final pull-request CI run completed successfully on Python 3.11, 3.12 and 3.13. The Python 3.12.16 run reports **604 passed** for the full core suite, including 18 focused tests for this update. The independent core-tests workflow also passed.

The dedicated synthetic benchmark completed five repetitions per operation on Python 3.12.16. Values below are p95 latency, not claimed speedups:

| Operation | p95 |
|---|---:|
| Claim specification and history validation | 0.131 ms |
| Source-lineage clustering (1,000 sources) | 11.630 ms |
| Hypothesis matrix (50 hypotheses, 1,000 observations) | 228.322 ms |
| Evidence coverage (100 claims, 1,000 evidence records) | 17.004 ms |
| Blind packet (100 documents) | 1.341 ms |
| Reviewer calibration (200 cases, five reviewers each) | 1.334 ms |
| Argument map (500 nodes, 499 edges) | 1.807 ms |
| Disagreement analysis (1,000 reviews) | 3.906 ms |
| Reassessment comparison (up to 1,000 source digests plus other dependency maps) | 1.123 ms |
| Dissent-preserving synthesis (50 positions) | 1.270 ms |

The 100-document synthetic blind packet occupied **19,861 bytes**. The benchmark artifact is attached to the dedicated [GitHub Actions benchmark run](https://github.com/gudjencio/SSSWET/actions/runs/42784532969). All ten probes remained below the intentionally broad 5,000 ms guard.

These figures describe one hosted runner and fixed synthetic fixtures. They are not mobile-device benchmarks, database storage-growth forecasts, external-provider latency measurements, scientific accuracy results or evidence of increased agent intelligence.

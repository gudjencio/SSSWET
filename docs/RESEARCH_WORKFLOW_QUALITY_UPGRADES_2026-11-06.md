# Research workflow quality upgrades — 6 November 2026

This release strengthens ten existing research-support modules. The comparison baseline is the immediately preceding implementation on the SSSWET main branch before this change. Existing public interfaces and read-only research principles are retained; new report fields are additive.

## Acceptance criteria and previous behaviour

| # | Improvement | Previous behaviour | Acceptance criteria for this revision |
|---|---|---|---|
| 1 | Provenance graph integrity | Returned nodes, edges, roots and an invalid-edge count; cycles and duplicate identifiers were not distinguished. | Deterministic topological order for acyclic graphs; explicit cycle nodes, duplicate node/edge counts, disconnected-component count and malformed-node/link diagnostics. A DAG cross-edge regression must not be misclassified as a cycle. No broken edge is silently repaired. |
| 2 | Agent capability support | Exact single-capability eligibility and a missing-capability summary. | Versioned registration history with mutation-isolated snapshots; deterministic multi-capability recommendations; forbidden-scope exclusion; partial coverage shown explicitly; no automatic assignment or execution. |
| 3 | Dataset governance metadata | Version fingerprints, parent links and same-digest candidates. | Privacy class, consent status, retention policy and access scope are retained; incomplete or risky declarations produce review flags; no automatic deletion, publication or legal-compliance claim. |
| 4 | Preregistration deviations | A complete plan could be frozen and fingerprinted. | Frozen snapshots can be verified; nested changes are enumerated; deviations retain the original fingerprint and require a reason and reviewer identifier; approval is never inferred. |
| 5 | Reproducibility manifests | Canonical manifest creation and top-level comparison. | Environment, random seed and input checksums are included; manifest digest can be verified; nested parameter differences are exposed; malformed or tampered manifests fail verification. |
| 6 | Virtual Time Travel temporal alignment | One observation per source identifier and lexical timestamp ordering. | Distinct observations from the same source/time can coexist; timezone-aware clocks are normalized; naive clocks remain separate; uncertainty windows can be clustered without inferring shared event identity. |
| 7 | Rescue resource allocation | One needs/stock pair was allocated independently, with permissive stock coercion. | Invalid quantities are rejected; multi-request planning honours explicit priority and max-min fairness within equal-priority groups; stock is never over-allocated; human dispatch remains required. |
| 8 | Accessibility audit | Checked image alt attributes and the main landmark. | Adds deterministic checks for document language, accessible button/link names, form labels, duplicate IDs, broken aria-labelledby references, hidden focusable controls and heading-level skips. HTML fragments remain supported without a false document-language warning. |
| 9 | Internationalisation quality | Reported missing translation keys and overall coverage. | Adds locale-tag checks, placeholder parity, extra-key detection, likely untranslated strings and RTL direction hints; semantic translation quality remains a human review task. |
| 10 | Evidence provenance review | Summarized source metadata, declared independence and review coverage. | Adds bounded declared-link resolution, duplicate identifier checks, reviewer-ID completeness and repeated-reviewer diagnostics; unresolved links are reported, not repaired or adjudicated. |

## Regression and safety controls

- Existing dataset registration fields and endpoints remain available. New governance fields have conservative defaults so historical records remain readable and are flagged for review rather than rejected.
- Existing provenance graph keys (nodes, edges, roots, invalid_edge_count) remain present. Iterative strongly connected component traversal retains true depth-first finish order; a cross-edge DAG regression test prevents false cycle reports.
- Agent capability registration history returns detached capability lists, so mutating a returned registration or history snapshot cannot rewrite retained audit history.
- Existing single-request rescue allocation output remains available; invalid boolean, negative, non-integer or excessive stock values are now rejected rather than coerced.
- Existing translation coverage fields remain present.
- Evidence rubric scores remain metadata assessments, not probabilities of truth. Reviewer counts do not prove independence.
- Time overlap is not proof that observations describe the same event. Timezone-naive timestamps are not silently interpreted as UTC.
- Resource plans do not dispatch responders, prescribe treatment, determine evacuation, or authorize field operations.
- Static accessibility checks do not replace keyboard, screen-reader, contrast, usability or expert WCAG review.
- Dataset flags are workflow prompts, not legal advice or a determination that consent or another lawful basis is sufficient.

## Reproducible validation

The Python test suite covers the new behaviour and backward-compatible output keys. The 6 November 2026 GitHub Actions run passed all **553 tests** on Python 3.11, 3.12 and 3.13. The separate core-test workflow also passed all 553 tests.

The Python 3.12 CI performance probe measured five runs per workload:

| Synthetic workload | Size | Median | p95 | Acceptance ceiling |
|---|---:|---:|---:|---:|
| Provenance graph | 1,200 nodes / 1,199 edges | 3.702 ms | 4.396 ms | 2,000 ms |
| Temporal alignment | 1,500 observations | 7.792 ms | 8.341 ms | 2,000 ms |
| Localization audit | 300 source strings / 15 locales | 12.040 ms | 12.413 ms | 2,000 ms |

A representative metadata-only dataset record grew from 179 to 306 serialized JSON bytes after adding governance fields: **127 additional bytes per record** in that sample. This is a JSON serialization sample, not a measurement of SQLite page growth, indexes, compression or a production database. The CI workload used deterministic synthetic data and is a regression ceiling, not a universal performance guarantee.

A synthetic evidence dossier with nine declared links resolved seven and reported two dangling references (77.8% declared-link coverage). This validates the diagnostic path, not the completeness of any real dossier. No memory-retrieval or contradiction-scoring algorithm was changed in this revision, so no such improvement is claimed.

## Known limitations

- Graph diagnostics operate on the supplied bounded graph and cannot identify omitted upstream evidence.
- Capability recommendations depend entirely on declared registry entries and do not assess agent competence.
- Governance flags cannot determine jurisdiction-specific legal requirements or whether a consent process is valid.
- Preregistration snapshots are immutable values returned by the function; durable storage and external timestamping require a separate append-only store.
- SHA-256 detects changed manifest content when the original digest is trusted; it is not a digital signature or proof of authorship.
- Temporal clusters preserve declared uncertainty but do not estimate clock drift or establish causal relationships.
- Fair allocation is a transparent planning aid; real-world urgency, clinical need and local incident command require qualified human decisions.
- HTML checks are static heuristics and may produce false positives or miss accessibility barriers.
- Placeholder checks cover named braces and common printf tokens, not every ICU message format.
- Provenance completeness measures declared references in the supplied dossier only; absent records outside the dossier remain unknown.
- The pull request has not been merged, so the changes are not yet part of the deployed main-branch site or application.

## Run locally

From the repository root, run the Python suite from the core directory with python -m pytest -q, then run python .github/scripts/benchmark_research_quality.py.

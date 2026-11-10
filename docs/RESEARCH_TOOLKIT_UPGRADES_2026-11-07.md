# Research toolkit upgrades — 7 November 2026

This revision adds ten callable, bounded research-support capabilities and one local-only dispatcher. It builds on the current `main` baseline at `4143f7d`, whose immediately preceding commit is `65f76a8`. The baseline already includes versioned scientific memory, append-only knowledge graphs, evidence packet validation, provenance reconciliation, reproducibility diagnostics, memory compaction and the 1,000-programme catalogue. This change adds reusable analysis around those records without rewriting them.

## Ten independently useful improvements

| # | Capability | Previous behaviour | New behaviour and acceptance criteria |
|---|---|---|---|
| 1 | Scientific-memory revision diff and provenance continuity | Memory lineage and append-only history exposed individual revision chains, but there was no bounded, reusable two-snapshot comparison reporting all changed fields and exact provenance deltas. | Compare two snapshots of at most 500 records and 1 MB each. Stable IDs identify additions, absences and changed records; SHA-256 hashes cover complete record payloads; source, experiment, graph, evidence, review and provenance-group changes are explicit. Unknown metadata changes are surfaced rather than silently ignored. Absence is not treated as deletion and no stored record or review state is modified. |
| 2 | Agent capability benchmark | Capability declarations and routing described what an agent says it can do, not how a fixed task set was reviewed. | Versioned case-set fingerprints, reviewer-attributed outcomes, per-capability weighted scores, coverage, abstention and Brier calibration score. Comparisons are like-for-like only when the complete case-set digest matches; changed task definitions suppress the score delta. A score is limited to the named benchmark and never claims general intelligence or real-world competence. |
| 3 | Dataset drift review | Dataset governance and checksums did not compare aggregate feature distributions across versions. | Numeric standardized mean shifts and categorical Jensen–Shannon divergence over caller-supplied aggregates only. Missing/type-changed features are explicit. Counts, categories and thresholds are bounded and validated; no raw rows are accepted or stored and drift is not treated as causality or invalidity. |
| 4 | Virtual Time Travel spatial quality and interpolation | Temporal mapping aligned observations and existing browser track handling segmented tracks, but the Python core lacked a provenance-carrying bounded interpolation helper. | UTC-normalized GPS segmentation with accuracy, time-gap, jump and speed diagnostics; at most 5,000 observations are consumed even from iterators. Spherical interpolation is permitted only strictly between two observations inside a bounded interval. Derived points carry both endpoint IDs/source references and are explicitly not observations. No extrapolation or historical/future reconstruction is claimed. |
| 5 | Civil-rescue inventory freshness | Resource planning allocated aggregate stock without lot-level expiry, inspection or quarantine screening. | Bounded lot-level planning excludes expired, quarantined, overdue-inspection, future-inspection and unverified-storage stock. Eligible stock is allocated by priority, max-min fairness within equal-priority tiers and first-expire-first-out. Human dispatch remains mandatory. |
| 6 | Protective-equipment test comparability | Test results could be compared without a shared, explicit condition key and unit normalization. | Reports are grouped only when method, configuration, conditioning, orientation, metric and unit dimension match. Supported units normalize to SI base units. Reported replicate counts weight record means, while record-level spread and missing uncertainty declarations remain visible. No certification, safety rating or pass/fail verdict is produced. |
| 7 | Preregistration completeness review | Frozen plans verified required identity fields and deviations, but did not provide a structured multi-criterion completeness review. | Fourteen criteria cover question, hypotheses, outcomes, methods, analysis, sample-size rationale, inclusion/exclusion, stopping, missing data, safety-review reference, deviations, randomization and blinding. Randomization/blinding may be marked not applicable only with a reason. This is not ethics approval or scientific approval. |
| 8 | SQLite health and backup verification | The application persisted SQLite data but had no small read-only health report and verified no-overwrite backup helper in the research core. | Read-only quick-check, page/free-list, journal, schema-version and bounded table-count diagnostics without returning row contents. Explicit backups use SQLite's online backup API, run an integrity check, hash files incrementally, verify the destination hash and refuse to overwrite an existing destination. No automatic pruning or retention deletion occurs. |
| 9 | WCAG contrast audit | Structural accessibility checks did not calculate contrast for supplied foreground/background pairs. | WCAG relative-luminance contrast checks for explicit hex/rgb color pairs, with AA/AAA thresholds for normal/large text and 3:1 for UI components. Gradients, transparency, images and final rendered states are not inferred; this does not certify overall accessibility. |
| 10 | BCP-47 locale fallback | The language catalogue and translation QA did not provide a reusable, deterministic runtime fallback resolver for regional/script tags. | Canonicalizes simple BCP-47 tags, resolves exact → progressively less-specific locale → configured fallback, and derives text direction from explicit script subtags before language defaults. It never translates content or claims a locale is fully translated. |

## Local API

The local research server exposes GET `/api/research-toolkit` for the operation catalogue and a loopback-only POST `/api/research-toolkit` dispatcher. The request is capped at 64 KiB. The dispatcher accepts exactly these ten operation keys: `memory_revision_diff`, `agent_benchmark`, `dataset_drift`, `spatiotemporal_track`, `rescue_inventory`, `protective_test_comparison`, `protocol_quality`, `storage_health`, `accessibility_contrast` and `locale_resolve`. It does not mutate the research database; the storage-health operation reads the configured database only.

Python modules remain directly importable from `ssswet_core` for offline use. The local dispatcher is a convenience layer, not an agent executor. Scientific-memory retrieval and Virtual Time Travel temporal-coverage interfaces are maintained separately; this change does not duplicate the existing memory-intelligence proposal.

## Acceptance and regression checks

- The baseline commit and its immediate parent are recorded above; the PR diff is limited to additive toolkit files plus the local dispatcher, README and CI integration.
- Memory snapshot comparison is deterministic, bounded to 500 records/1 MB, hashes full record payloads, surfaces untracked metadata changes and preserves provenance deltas.
- Agent benchmark scores use only reviewer-annotated outcomes; unreviewed cases do not enter the weighted score and changed case definitions invalidate like-for-like score deltas.
- Dataset drift consumes aggregate summaries only; non-finite, fractional sample counts and oversized inputs are rejected.
- Spatial interpolation is impossible outside the two source timestamps or beyond the configured gap; each derived point preserves both source references.
- Rescue allocations never draw from excluded lots, never exceed eligible stock and preserve higher-priority requests before lower-priority tiers.
- Protective test groups never mix different declared conditions or physical dimensions; missing uncertainty is not silently converted to zero.
- A protocol is structurally reviewable only when every mandatory criterion is documented and non-applicability is justified for optional design controls.
- Storage inspection is read-only; backup creation is no-overwrite and verifies both SQLite integrity and the destination SHA-256.
- Contrast thresholds follow WCAG 2.x ratios for the supplied usage class; unsupported colors are reported as invalid, not silently guessed.
- Locale fallback is deterministic, honors explicit RTL/LTR scripts and does not translate.
- New unit tests run under the existing Python CI matrix. A fixed synthetic CI probe measures 500-record memory revision diff p95, 100-feature drift time and 1,500-observation track segmentation time; the memory-diff p95 guard is 2 seconds on the CI runner.

## Regression risks reviewed

- Snapshot absence could be mistaken for deletion: the diff reports absence only and never changes the append-only store.
- Metadata-only changes could be lost: complete record hashes and untracked-field lists expose changes outside the named scientific fields.
- Benchmark scores could be overgeneralized: reports are bound to a benchmark ID/version and case-set digest, include coverage and explicitly disallow general-intelligence claims.
- Drift alerts could be mistaken for causal explanations: only descriptive distribution differences are reported.
- Interpolated map points could be mistaken for captured evidence: every point is marked derived and not_an_observation, with source endpoint IDs.
- Rescue allocation could be mistaken for dispatch: the planner is informational and explicitly requires human dispatch and separate operational authorization.
- Protective test comparisons could be mistaken for certification: only matched-condition summaries are returned; no pass/fail or safety rating is produced.
- Protocol completeness could be mistaken for approval: safety/ethics approval remains false in every report.
- Backup creation could overwrite or prune history: destination creation is atomic/no-overwrite and no deletion policy is added.
- Static contrast checks could miss rendered gradients or alpha compositing: unsupported/unknown rendered states must be measured separately.
- Locale fallback could imply translation quality: the result explicitly reports that translation completeness is not guaranteed.

## Limits

Benchmarks are synthetic and runner-specific. Memory-diff latency excludes database/network costs. Dataset drift depends on the correctness of supplied aggregates. Spatial interpolation is a geometric convenience, not a reconstructed path or a measurement. Inventory freshness is only as reliable as supplied dates and storage checks. Protective test comparability depends on accurate declared metadata and does not establish independent replication. Contrast audits require actual rendered color pairs. Locale resolution does not perform machine translation. Human, scientific, ethics, safety, privacy, cybersecurity and legal review remain mandatory.

# Research toolkit upgrades — 7 November 2026

This revision adds ten callable, bounded research-support capabilities and one local-only dispatcher. The changes extend the existing scientific-memory, agent, dataset, Virtual Time Travel Mapping, civil-rescue, protective-systems, preregistration, storage, accessibility and localization work without changing existing stored records or scientific review states.

## Ten independently useful improvements

| # | Capability | Previous behaviour | New behaviour and acceptance criteria |
|---|---|---|---|
| 1 | Scientific-memory retrieval and evaluation | Existing memory views exposed stored records, but there was no standalone, reproducible bounded ranking/evaluation helper in the core toolkit. | Deterministic field-weighted retrieval over at most 500 records, at most 100 results, stable ID tie-breaking, explicit matched fields and preserved source/experiment/graph/evidence/review references. Contested records are not suppressed. Labelled evaluation reports precision@k, recall@k, F1@k, MRR and nDCG@k; an optional benchmark reports median/p95 in-process latency. |
| 2 | Agent capability benchmark | Capability declarations and routing described what an agent says it can do, not how a fixed task set was reviewed. | Versioned case-set fingerprints, reviewer-attributed outcomes, per-capability weighted scores, coverage, abstention and Brier calibration score. Comparisons distinguish shared, added and removed cases. A score is limited to the named benchmark and never claims general intelligence or real-world competence. |
| 3 | Dataset drift review | Dataset governance and checksums did not compare aggregate feature distributions across versions. | Numeric standardized mean shifts and categorical Jensen–Shannon divergence over caller-supplied aggregates only. Missing/type-changed features are explicit. Thresholds are visible; no raw rows are accepted or stored and drift is not treated as causality or invalidity. |
| 4 | Virtual Time Travel spatial quality and interpolation | Temporal mapping aligned observations and existing browser track handling segmented tracks, but the Python core lacked a provenance-carrying bounded interpolation helper. | UTC-normalized GPS segmentation with accuracy, time-gap, jump and speed diagnostics; spherical interpolation only strictly between two observations inside a bounded interval. Derived points carry both endpoint IDs/source references and are explicitly not observations. No extrapolation or historical/future reconstruction is claimed. |
| 5 | Civil-rescue inventory freshness | Resource planning allocated aggregate stock without lot-level expiry, inspection or quarantine screening. | Bounded lot-level planning excludes expired, quarantined, overdue-inspection, future-inspection and unverified-storage stock. Eligible stock is allocated by priority, max-min fairness within equal-priority tiers and first-expire-first-out. Human dispatch remains mandatory. |
| 6 | Protective-equipment test comparability | Test results could be compared without a shared, explicit condition key and unit normalization. | Reports are grouped only when method, configuration, conditioning, orientation, metric and unit dimension match. Supported units normalize to SI base units; replicate counts and declared uncertainty remain visible. No certification, safety rating or pass/fail verdict is produced. |
| 7 | Preregistration completeness review | Frozen plans verified required identity fields and deviations, but did not provide a structured multi-criterion completeness review. | Fourteen criteria cover question, hypotheses, outcomes, methods, analysis, sample-size rationale, inclusion/exclusion, stopping, missing data, safety-review reference, deviations, randomization and blinding. Randomization/blinding may be marked not applicable only with a reason. This is not ethics approval or scientific approval. |
| 8 | SQLite health and backup verification | The application persisted SQLite data but had no small read-only health report and verified no-overwrite backup helper in the research core. | Read-only quick-check, page/free-list, journal, schema-version and bounded table-count diagnostics without returning row contents. Explicit backups use SQLite's online backup API, run an integrity check, hash the result and refuse to overwrite an existing destination. No automatic pruning or retention deletion occurs. |
| 9 | WCAG contrast audit | Structural accessibility checks did not calculate contrast for supplied foreground/background pairs. | WCAG relative-luminance contrast checks for explicit hex/rgb color pairs, with AA/AAA thresholds for normal/large text and 3:1 for UI components. Gradients, transparency, images and final rendered states are not inferred; this does not certify overall accessibility. |
| 10 | BCP-47 locale fallback | The language catalogue and translation QA did not provide a reusable, deterministic runtime fallback resolver for regional/script tags. | Canonicalizes simple BCP-47 tags, resolves exact → progressively less-specific locale → configured fallback, and returns RTL/LTR direction. It never translates content or claims a locale is fully translated. |

## Local API

The local research server exposes GET /api/research-toolkit for the operation catalogue and a loopback-only POST /api/research-toolkit dispatcher. The request is capped at 64 KiB. The dispatcher accepts one tool key matching one of the ten operation names above. It does not mutate the research database; the storage-health operation reads the configured database only. The endpoint is not enabled for remote/public callers.

Python modules remain directly importable from ssswet_core for offline use. The local dispatcher is a convenience layer, not an agent executor.

## Acceptance and regression checks

- Existing scientific-memory versions, source references, review decisions, datasets and experiments are not rewritten.
- Retrieval is bounded and deterministic; labelled metrics and median/p95 latency are reported separately from any scientific-quality judgement.
- Agent benchmark scores are computed only from reviewer-annotated outcomes; unreviewed cases are exposed and do not enter the reviewed weighted score.
- Dataset drift consumes aggregate summaries only; invalid, non-finite and oversized inputs are rejected.
- Spatial interpolation is impossible outside the two source timestamps or beyond the configured gap; each derived point preserves both source references.
- Rescue allocations never draw from excluded lots and never exceed eligible stock.
- Protective test groups never mix different declared test conditions or physical dimensions.
- A protocol is structurally reviewable only when every mandatory criterion is documented and non-applicability is justified for optional design controls.
- Storage inspection is read-only; backup creation verifies the destination and refuses overwrite.
- Contrast thresholds follow WCAG 2.x ratios for the supplied usage class; unsupported colors are reported as invalid, not silently guessed.
- Locale fallback is deterministic, preserves RTL direction for known RTL language subtags, and does not translate.
- New unit tests run under the existing Python CI matrix. A fixed synthetic CI probe measures retrieval p95, 100-feature drift time and 1,500-observation track segmentation time; the retrieval p95 guard is 2 seconds on the CI runner.

## Regression risks reviewed

- Ranking scores could be mistaken for evidence quality: outputs label them as retrieval/navigation scores and preserve contested state.
- Benchmark scores could be overgeneralized: reports are bound to a benchmark ID/version and case-set digest, include coverage, and explicitly disallow general-intelligence claims.
- Drift alerts could be mistaken for causal explanations: only descriptive distribution differences are reported.
- Interpolated map points could be mistaken for captured evidence: every point is marked derived and not_an_observation, with source endpoint IDs.
- Rescue allocation could be mistaken for dispatch: the planner is informational and explicitly requires human dispatch and separate operational authorization.
- Protective test comparisons could be mistaken for certification: only matched-condition summaries are returned; no pass/fail or safety rating is produced.
- Protocol completeness could be mistaken for approval: safety/ethics approval remains false in every report.
- Backup creation could overwrite or prune history: destination creation is no-overwrite and no deletion policy is added.
- Static contrast checks could miss rendered gradients or alpha compositing: unsupported/unknown rendered states must be measured separately.
- Locale fallback could imply translation quality: the result explicitly reports that translation completeness is not guaranteed.

## Limits

All benchmarks are synthetic and runner-specific. Retrieval latency excludes database/network costs. Aggregate drift depends on the correctness of the supplied summaries. Spatial interpolation is a geometric convenience, not a reconstructed path or a measurement. Inventory freshness is only as reliable as the supplied dates and storage checks. Protective test comparability depends on accurate declared metadata and does not establish independent replication. Contrast audits require actual rendered color pairs. Locale resolution does not perform machine translation. Human, scientific, ethics, safety, privacy, cybersecurity and legal review remain mandatory.

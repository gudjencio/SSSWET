# SSSWET — Research infrastructure upgrades — 2026-11-03 run 4

This release adds ten independently useful, bounded improvements. The previous version already included unit normalization, sensitivity analysis, data-quality profiling, provenance graphs, result caching, schema versioning, localization fallback, and related evidence/research infrastructure. This run therefore focuses on the next layer: freshness, source independence, decision traceability, stopping conditions, workload distribution, observation quality, rescue readiness, and Virtual Time evidence calibration.

## 1. Evidence freshness scoring
`evidence_freshness.py` provides a deterministic half-life score for age-sensitive evidence. It changes prioritization metadata only; it does not rewrite source claims or declare old evidence false.

## 2. Source independence grouping
`source_independence.py` groups sources by explicit publisher/DOI/domain identifiers so duplicated reporting is not silently counted as independent corroboration.

## 3. Consensus matrix
`consensus_matrix.py` builds a deterministic subject/value count matrix after case normalization. It exposes agreement structure without converting agreement into scientific truth.

## 4. Reproducibility gap inspection
`reproducibility_gap.py` reports missing manifest fields and missing declared artifacts. It complements the existing reproducibility manifest and does not establish validity.

## 5. Bounded decision traces
`decision_trace.py` normalizes ordered research decisions with explicit reasons and a hard event bound, improving auditability without retaining unbounded history.

## 6. Research stop conditions
`research_stop_conditions.py` adds iteration, failure, and no-progress limits. This prevents long-running research loops from becoming unbounded.

## 7. Capability-aware agent load balancing
`agent_load_balancer.py` ranks eligible agents deterministically by load, completed work, and identifier while excluding blocked/retired agents.

## 8. Observation quality scoring
`observation_quality.py` measures completeness of source, timestamp, and value fields. Missing information is reported rather than inferred.

## 9. Rescue readiness checks
`rescue_readiness.py` adds a human-controlled readiness checklist for communications, resources, dispatch confirmation, and medical authority. It explicitly never performs automated dispatch.

## 10. Virtual Time observation confidence
`virtual_time_confidence.py` labels recorded Virtual Time Mapping evidence using observation count and completeness. It explicitly never recovers or reconstructs unrecorded history.

## Acceptance criteria
- All ten modules are deterministic for identical inputs.
- Bounds and invalid-input checks are explicit where unbounded growth is possible.
- Source independence is represented separately from agreement.
- Research-loop termination is measurable.
- Rescue functionality remains human-controlled.
- Virtual Time confidence is derived only from recorded observations.
- Regression coverage is provided by `core/tests/test_upgrades_2026_11_03_run4.py`.

## Regression fixes included before this run
The preceding CI run exposed three compatibility/test failures: bounded-retention ordering, legacy construction of `ClaimConflict`, and an outdated JavaScript feature-string assertion. These were corrected before adding the ten new modules.

## Limitations
These utilities do not prove scientific truth, increase intelligence by assertion, recover historical events, certify equipment, make medical decisions, or replace scientific review, safety review, ethics, privacy, cybersecurity, legal requirements, or human dispatch authority.

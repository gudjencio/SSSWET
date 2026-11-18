# Upgrade plan — current-main integration, 18 November 2026, run 6

## Baseline inspected before implementation
- Current main: `85afc7f649edf2e3a42e85bb167c9478d06dab06`.
- Immediately preceding main commit: `8099f6c232e60d5541c76544b59686d16c41f12f`.
- The latest baseline isolates public-report patch validation from secret-bearing workflow context; the preceding commit upgrades the public report processor to Node 24. Neither includes energy-storage assurance.
- Candidate PR #73 was inspected: ten retrospective utilities, focused tests, documentation and benchmark. Its acceptance plan was committed before the candidate implementation. The current-main integration transplants the additive feature onto the newer baseline and re-applies only the intended CI and README additions.

## Ten acceptance criteria
1. Validate supplied sample logs with a hard 20,000-row cap, unique IDs, explicit timezone, strictly monotonic per-session timestamps, finite numeric fields, provenance, and whitelist-only normalized records.
2. Segment only researcher-declared session/cycle IDs; retain incomplete cycles and mode-order anomalies.
3. Integrate capacity by trapezoidal method, preserve source/calibration provenance and reject caller-declared excessive gaps.
4. Integrate measured voltage-current energy and report charge/discharge ratio unchanged, including values above 100% with review flags.
5. Fit descriptive capacity trends only with at least three distinct cycle measurements; retain uncertainty and evidence references; never extrapolate.
6. Screen temperature observations only against caller-supplied limits, report counts and confirmed adjacent same-side spans, and expose gaps/limitations.
7. Screen cell-voltage spread against caller-supplied review thresholds while preserving missing/insufficient observations.
8. Flag robust-MAD anomalies with provenance; never delete or silently alter source observations.
9. Canonicalize/fingerprint protocol revisions and diff field/list paths under bounded nesting and size.
10. Create deterministic evidence manifests with sample/protocol digests, source/calibration references, tamper verification, explicit not-reviewed/not-release state and a 2 MiB maximum.

## Additional regression criteria
- Huge integers normalize to validation errors, not uncaught OverflowError.
- Integrations reject non-finite intermediate or accumulated results.
- Overflowed anomaly scores are flagged with null scores; outputs remain strict JSON.
- Cycle-number precision remains exactly representable.
- Nested protocol arrays diff by index and nesting bounds apply; malformed mixed keys raise ValueError.

## Measurable validation
- Focused positive, negative, boundary and tamper tests for all ten capabilities.
- Full core tests and CI on Python 3.11, 3.12 and 3.13.
- Synthetic benchmark: 2,000 samples, five repetitions; every workload p95 < 2,000 ms.
- Evidence packet <= 2 MiB; deterministic digest; tampered packet and mismatched supplied-sample digest fail.
- No runtime dependencies, hardware-control endpoint, browser asset changes or modifications to existing APIs.

## Regression risks and mitigations
- Strict validation may reject oversized, unordered or timezone-naive input; explicit errors and documented limits.
- Current is represented as non-negative magnitude with declared mode for direction; rest/mixed intervals are not bridged.
- Thresholds are review values, not safety recommendations.
- Incomplete cycles, gaps, anomalies and negative findings remain visible.
- Packets omit raw samples and do not authenticate source/instrument authorship.
- Synthetic benchmarks are not field tests or battery safety validation.
- CI changes are additive and must preserve the current security workflow and all existing checks.

## Additional numerical/resource acceptance — after initial CI review
- Trend fitting must remain finite for large-but-valid capacity measurements by using scaled calculations; any unrepresentable slope/relative-change is rejected rather than serialized as NaN or infinity.
- Round-trip ratios must reject unrepresentable numeric results instead of returning non-finite percentages.
- Protocol size limits are checked before flattening to prevent oversized inputs from causing avoidable expansion.
- Tests cover constant 1e308 capacities, an extreme but finite-input energy ratio, and a payload just over the 1 MB protocol limit with flattening disabled.
- Trapezoid averaging must avoid false overflow for large finite endpoints when the average and integrated result are representable; test this positive case alongside overflow rejection.

# Upgrade plan — current-main integration, 18 November 2026

## Baseline inspected before transplant/integration
- Current main: `85afc7f649edf2e3a42e85bb167c9478d06dab06` (85afc7f)
- Immediately preceding main commit: `8099f6c232e60d5541c76544b59686d16c41f12f` (8099f6c)
- The latest baseline isolates public-report patch validation from secret-bearing workflow context; the preceding commit upgrades the public report processor to Node 24. Neither includes energy-storage assurance.
- Existing candidate PR #73 (head `e75934323e264079a73dffac01b2fc69457c4728`) was inspected: 659-line core module, 32 focused tests, guide, benchmark, workflow, README and acceptance plan. Its branch is based on the immediately preceding main commit, so this integration transplants only feature files and re-applies additive CI/docs changes onto current main. Pre-merge candidate CI passed 867 core tests on Python 3.11/3.12/3.13; the Python 3.12 benchmark completed. The existing PR is not merged.

## Ten acceptance criteria
1. Validate supplied sample logs with a hard 20,000-row cap, unique IDs, explicit timezone, strictly monotonic per-session timestamps, finite fields, provenance and whitelist-only normalized records.
2. Segment only researcher-declared session/cycle IDs; preserve incomplete cycles and mode-order anomalies.
3. Integrate capacity by trapezoidal method, preserve source/calibration refs and reject caller-defined excessive gaps.
4. Integrate voltage-current energy and report round-trip ratio unchanged, including >100% with review flags.
5. Fit descriptive trend only with >=3 unique cycle observations; retain uncertainty and evidence refs, no extrapolation.
6. Count caller-limit temperature observations and only confirmed same-side adjacent spans; never claim clearance.
7. Screen declared cell-voltage spread using a caller threshold; retain missing/insufficient observations.
8. Flag robust-MAD anomalies with provenance and retain original observations.
9. Canonicalize/fingerprint protocol revisions and diff field/list paths under a 16-level nesting and 1 MiB input limit.
10. Create deterministic evidence manifests with sample/protocol digests, provenance and calibration refs, tamper verification, explicit not-reviewed/not-release state, and <=2 MiB cap.

## Additional regression criteria
- Conversion of huge integers must return a bounded validation error, not raise OverflowError.
- Integration must refuse non-finite intermediate or accumulated results.
- Robust anomaly scores that overflow must be flagged with null numeric score; outputs must remain strict JSON.
- Cycle numbers must remain exactly representable in trend analysis.
- Nested protocol arrays are diffed by index; nesting limit applies to arrays as well as objects; malformed key types return ValueError.

## Measurable validation
- Focused tests for all ten capabilities and the new edge cases.
- Full core suite across Python 3.11, 3.12 and 3.13.
- Synthetic benchmark: 2,000 samples, five repeats; every workload p95 < 2,000 ms.
- Evidence packet <= 2 MiB; deterministic digest; tampered packet and mismatched source-sample digest fail.
- No runtime dependency, hardware-control endpoint or existing UI/API modification.

## Regression risks and mitigation
- Validation is stricter than untrusted input ingestion: errors remain explicit and are documented.
- Current is represented as non-negative magnitude; declared mode determines charge/discharge. Mixed/rest intervals are not integrated across.
- Caller thresholds are review values, never operating/safety guidance.
- Incomplete cycles, missing values, anomalies and negative findings remain visible.
- Manifests do not include raw sample rows and do not authenticate instrument/source authorship.
- Benchmark data is synthetic, not field testing or battery safety validation.
- CI workflow edit is additive and restricted to Python 3.12 benchmark execution; the mainline security patch remains intact.

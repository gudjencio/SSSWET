# Upgrade plan — 18 November 2026, run 6

## Baseline inspected before implementation
- Current main: 8099f6c232e60d5541c76544b59686d16c41f12f
- Immediately preceding main commit: 2e99fd4da6532442a132bae06df7052adbdf8ad6
- The latest main commit changes only the public-report processor action pins and the Node-24 pin regression test. Its parent upgrades Pages deployment action pins. The energy-storage assurance module is not present on main.
- Existing open PR #26 contains a candidate module and tests, but its branch is 36 commits behind main and is not mergeable. This run will transplant the additive feature into a fresh branch based on current main, not merge its stale workflow/README edits.

## Ten acceptance criteria (feature scope)
1. Validate researcher-supplied sample logs with a hard 20,000-row limit, unique IDs, explicit timezone, monotonic session timestamps, finite values, declared provenance, and whitelist-only normalized fields.
2. Segment only declared session/cycle IDs; retain incomplete cycles and unexpected mode order as flags without inferring boundaries.
3. Integrate capacity by trapezoidal method with source/calibration provenance and reject gaps above a caller-declared limit.
4. Integrate measured voltage-current energy and compare charge/discharge ratios; preserve values above 100% and flag review instead of clipping.
5. Fit descriptive capacity trend only with at least three distinct cycle measurements; report residual quality and never extrapolate.
6. Screen temperature observations only against caller-supplied limits, report counts and confirmed adjacent spans, and expose gaps/limitations.
7. Compare cell-voltage spread to a caller-supplied review threshold while preserving missing/insufficient readings.
8. Flag robust-MAD signal outliers with provenance; never delete or silently alter samples.
9. Canonicalize and hash protocol revisions; report added/removed/changed paths and preserve prior revision.
10. Create a bounded deterministic evidence manifest with source/sample/calibration references, canonical hashes, tamper checks and explicit non-review/non-release state.

## Measurable validation
- Focused positive/negative regression tests for all ten functions; full core test suite on Python 3.11/3.12/3.13.
- Synthetic benchmark: 2,000 samples, five repeats, median/p95 for each capability, p95 < 2,000 ms; evidence packet <= 2 MiB.
- Packet digest and supplied-sample digest must verify; tampered content must fail.
- No runtime dependency; no hardware-control API; CI-only benchmark on Python 3.12.

## Regression risks and mitigations
- New bounded API could reject oversized, unordered or timezone-naive logs; rejection is explicit and limits are documented.
- Integration assumes positive current magnitude with mode as direction; mixed/rest intervals cannot be bridged.
- Caller-supplied thresholds are screening parameters, not safety guidance or certification.
- Incomplete cycle IDs, anomalies and negative findings remain visible.
- No raw sample rows are placed in the evidence packet; raw files remain caller-governed.
- Synthetic performance results are not field-device or battery safety validation.

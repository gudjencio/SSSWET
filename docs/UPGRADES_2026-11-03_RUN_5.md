# SSSWET — Research infrastructure upgrades — 2026-11-03 run 5

This release adds ten bounded research utilities, alongside a calibration correction for Virtual Time confidence.

## Improvements

1. **Sample-size planning** — estimates the sample size for a mean at a stated confidence and margin of error, with assumptions returned explicitly.
2. **Multiple-testing adjustment** — implements Bonferroni, Holm, and Benjamini–Hochberg adjustments while preserving input order.
3. **Prediction calibration metrics** — reports Brier score and equal-width expected calibration error for binary probabilities.
4. **Missingness profiling** — reports column and row missingness without changing the supplied dataset.
5. **Outlier review flags** — uses IQR fences to flag unusual observations; never removes or edits records.
6. **Dataset split leakage checks** — detects repeated identifiers across declared splits and rejects duplicates within a split.
7. **Experiment preregistration snapshots** — creates canonical, fingerprinted plan snapshots when required design fields are present.
8. **Privacy field-name audit** — flags potentially identifying field names without inspecting values or deleting data.
9. **Research-task dependency ordering** — produces a stable topological order and explicitly reports unknown dependencies or cycles.
10. **Numeric distribution drift** — measures standardized mean shifts between reference and current numeric samples without inferring causes.

## Virtual Time confidence calibration

The high-confidence threshold now requires at least 20 observations and at least 95% completeness. Ten complete observations remain medium. This corrects the previous mismatch between the intended conservative threshold and the implementation.

## Acceptance criteria

- Deterministic outputs for identical inputs, apart from no timestamps or random identifiers being generated.
- Explicit finite-input validation and bounded collection sizes.
- Multiple-testing methods preserve original p-value order and monotonic adjusted values.
- Calibration metrics count every valid observation, including probability 1.0.
- Outlier and missingness tools never mutate source records.
- Leakage checks report identifier overlap rather than claiming semantic leakage detection.
- Privacy checks inspect field names only and make no claim of complete anonymization.
- Dependency ordering is stable and detects cycles.
- Statistical outputs expose assumptions and do not claim causal or scientific validity.
- Regression coverage is provided by core/tests/test_upgrades_2026_11_03_run5.py.

## Limitations

These utilities support analysis and review; they do not replace statistical consultation, preregistered institutional processes, scientific peer review, privacy review, safety review, or domain-specific validation. A sample-size estimate based on a mean does not apply automatically to proportions, clustered designs, repeated measures, finite populations, or non-independent observations. Drift flags are descriptive and do not identify a cause.

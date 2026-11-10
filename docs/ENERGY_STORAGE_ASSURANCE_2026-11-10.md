# Field energy-storage assurance

**Status:** experimental, retrospective research utilities.  
**Module:** \`core/ssswet_core/energy_storage_assurance.py\`  
**Introduced:** 2026-11-10

This module adds a bounded analysis path for researcher-supplied field-power and
energy-storage logs. It may support evaluation of batteries used in sensors,
communications, mobility aids, protective equipment and rescue-support devices.
It does not control hardware, prescribe charging procedures, predict thermal
runaway, certify a battery, or authorize operational use.

## Ten functional improvements

1. **Validated sample ingestion.** Enforces a 20,000-sample ceiling, timezone-aware
   timestamps, unique sample IDs, per-session monotonic time, finite non-negative
   current, positive voltage, bounded cell arrays and declared source IDs. Unknown
   input fields are omitted from normalized records rather than copied into reports.
2. **Explicit cycle segmentation.** Groups only by researcher-declared session and
   cycle IDs. Incomplete cycles and unexpected charge/discharge order remain visible
   with review flags; no threshold-based cycle boundaries are guessed.
3. **Capacity integration.** Integrates current magnitude using the trapezoidal
   rule and reports Ah, interval count, source IDs, calibration references and the
   largest observed interval. Gaps beyond the caller-supplied limit stop analysis.
4. **Energy and round-trip analysis.** Integrates measured voltage multiplied by
   current to Wh, then compares charge and discharge energy. Ratios above 100% are
   reported unchanged with a review flag rather than clipped or silently accepted.
5. **Capacity-fade trend.** Fits a descriptive least-squares line to at least three
   unique cycle measurements. Reports slope, observed relative change and
   descriptive R-squared; it does not forecast end-of-life or extrapolate.
6. **Temperature-excursion accounting.** Counts observations outside explicit
   researcher-supplied limits and sums only adjacent intervals whose two endpoints
   are outside on the same side. It does not interpolate crossings or call a range
   safe.
7. **Cell-voltage imbalance screening.** Calculates per-sample max-minus-min cell
   voltage spread against a caller-supplied review threshold. Missing or insufficient
   cell measurements remain visible.
8. **Robust signal-anomaly screening.** Uses median absolute deviation on selected
   current, voltage and temperature fields. It flags candidate observations but
   never deletes or edits source samples.
9. **Protocol revision comparison.** Produces deterministic SHA-256 fingerprints
   and field-path differences for bounded JSON-compatible protocol revisions.
10. **Reproducible evidence packet.** Creates a deterministic, bounded manifest
    containing sample and protocol digests, source/session/cycle identifiers,
    calibration references, caller-supplied metrics and explicit review limitations.
    A verifier can check manifest integrity and optionally compare supplied samples.

## Input format

Each sample is a JSON-compatible object with these required fields:

- \`sample_id\`, \`session_id\`, \`cycle_id\`, \`source_id\`: non-empty identifiers.
- \`timestamp_utc\`: ISO-8601 timestamp with an explicit timezone.
- \`mode\`: \`charge\`, \`discharge\` or \`rest\`.
- \`current_a\`: non-negative current magnitude in amperes.
- \`voltage_v\`: positive voltage in volts.

Optional fields are \`temperature_c\`, \`cell_voltages_v\`,
\`calibration_refs\`, \`current_std_a\`, \`voltage_std_v\` and
\`temperature_std_c\`. Current is represented as a magnitude; the explicit
\`mode\` carries charge/discharge direction. The input order is preserved.
Timestamps must strictly increase within each session, not across unrelated
sessions. The module does not silently sort, merge or infer missing records.

## Example

Run from the repository root:

\`\`\`python
from ssswet_core.energy_storage_assurance import (
    integrate_capacity,
    round_trip_efficiency,
    validate_energy_samples,
)

samples = validate_energy_samples(researcher_supplied_samples)
capacity = integrate_capacity(
    samples, cycle_id="cycle-01", mode="discharge",
    session_id="session-01", max_gap_seconds=120,
)
efficiency = round_trip_efficiency(
    samples, cycle_id="cycle-01",
    session_id="session-01", max_gap_seconds=120,
)
\`\`\`

The example assumes that the supplied sample IDs, source IDs, timestamps,
calibration references and cycle labels have already been reviewed by the
researcher. The functions do not retrieve or upload source files.

## Acceptance criteria and regression controls

- All ten operations have direct positive and negative tests.
- The test suite covers invalid timestamps, duplicate IDs, non-finite values,
  negative current, input limits, session ambiguity, cycle gaps, rest-mode gaps,
  unexpected cycle order, >100% energy ratios, duplicate cycle numbers,
  missing temperature/cell data, robust-outlier flags, protocol changes and
  manifest tampering.
- The existing Python CI matrix remains Python 3.11, 3.12 and 3.13.
- A synthetic benchmark runs all ten operations on bounded data and applies a
  broad 2,000 ms p95 regression ceiling per operation. It is a regression guard,
  not a hardware-performance claim.
- No runtime dependency, persistent database table, existing endpoint, existing
  research record, public catalogue or payment/customer setting is changed.

## Comparison with previous behaviour

The inspected \`main\` baseline and its immediate predecessor contained no
dedicated field energy-storage analysis module. Researchers could retain dataset
metadata and use general-purpose research utilities, but had no integrated,
bounded path for cycle-aware Ah/Wh calculations, explicit gap rejection,
capacity-trend description, caller-threshold excursion screening, protocol
fingerprints and a deterministic energy-test evidence manifest. The new module
adds those operations without changing existing APIs or stored data.

## Limitations and interpretation

- Trapezoidal integration assumes the supplied samples reasonably represent the
  signal between adjacent points. Long gaps are rejected; shorter gaps may still
  hide transients.
- Charge/discharge mode, cycle IDs, current convention, source IDs, calibration
  references and measurement uncertainty are supplied by the researcher and are
  not independently authenticated.
- Temperature and cell-spread thresholds are caller-provided review limits, not
  manufacturer limits or safety thresholds.
- Median-absolute-deviation flags are screening leads; real transients and sensor
  faults can both appear as outliers.
- Capacity fade is a descriptive fit to observed points only; it is not a
  degradation model or lifetime prediction.
- The evidence packet hashes normalized metadata and declared metrics. It does
  not contain raw samples, authenticate authorship, authenticate calibration
  certificates, or establish scientific validity.
- Do not include personal data, private operational details, credentials or
  confidential material in public examples, test fixtures or evidence packets.
- No output is a charging instruction, safety clearance, certification,
  deployment approval, medical recommendation or rescue dispatch decision.
  Human engineering, scientific, safety, privacy, ethics and legal review remain
  necessary for any real-world application.

# Virtual Time Mapping: independent local-frame validation

## Purpose

The local-frame alignment utility fits a two-dimensional rigid transform (rotation and translation, with no scale or shear) from paired landmarks. Its in-sample residuals describe how well that transform fits the same landmarks used to estimate it. They are not an independent test of the transform.

The companion module `ssswet_core.vtt_local_frame_validation` adds a separate hold-out check. It applies an already-fitted transform to additional paired landmarks and reports their residuals without refitting.

## Usage

Run from the `core` directory:

```python
from ssswet_core.vtt_local_frame_alignment import fit_local_frame_alignment
from ssswet_core.vtt_local_frame_validation import validate_local_frame_alignment

fit_points = [
    {"landmark_id": "fit-1", "source": [0, 0], "target": [10, 20],
     "source_uncertainty": 0.01, "target_uncertainty": 0.01},
    {"landmark_id": "fit-2", "source": [1, 0], "target": [10, 21],
     "source_uncertainty": 0.01, "target_uncertainty": 0.01},
    {"landmark_id": "fit-3", "source": [0, 1], "target": [9, 20],
     "source_uncertainty": 0.01, "target_uncertainty": 0.01},
]
alignment = fit_local_frame_alignment(
    fit_points, source_frame_id="local-a", target_frame_id="local-b",
    coordinate_unit="m",
)

check_points = [
    {"landmark_id": "check-1", "source": [1, 1], "target": [9, 21],
     "source_uncertainty": 0.02, "target_uncertainty": 0.03},
    {"landmark_id": "check-2", "source": [2, 1], "target": [9, 22],
     "source_uncertainty": 0.02, "target_uncertainty": 0.03},
    {"landmark_id": "check-3", "source": [-1, 2], "target": [8, 19],
     "source_uncertainty": 0.02, "target_uncertainty": 0.03},
]
report = validate_local_frame_alignment(alignment, check_points)
print(report["validation_status"])
print(report["rms_residual"], report["maximum_residual"])
```

## Interpretation

- `rms_residual` and `maximum_residual` are calculated only from the supplied hold-out landmarks.
- Each validation ID must be unique and must not occur in the fitted transform's residual list.
- At least three hold-out landmarks are required for the module's basic screening-count flag. Three points are not a statistical guarantee of spatial coverage or generalization.
- The result distinguishes `insufficient_holdout_count`, `holdout_residuals_within_declared_bounds`, and `holdout_residuals_exceed_declared_bounds`.
- The transform and validation-input SHA-256 values are deterministic content fingerprints. They are not signatures, evidence of authenticity, or proof that landmarks were independently surveyed.
- Distinct IDs prevent accidental reuse of the same recorded identifier, but cannot prove that two records represent independently measured physical points. Researchers must maintain that provenance separately.

## Uncertainty semantics

`source_uncertainty` and `target_uncertainty` are interpreted as user-declared absolute radial coordinate bounds expressed in the same `coordinate_unit` as the landmarks. Their sum is used as a conservative residual bound by the triangle inequality. These values are not standard deviations, confidence intervals, or calibrated probability distributions. The fit and hold-out utilities do not propagate uncertainty in the estimated transform parameters; a passing result is only a coordinate-residual screen, not a complete uncertainty budget. If the input bounds have different meanings or units, the result is not interpretable and must not be used.

## Scientific and spatial limits

- The validator does not refit, optimize, scale, or otherwise alter the transform.
- It validates a two-dimensional rigid transform only. It does not perform CRS conversion, georeferencing, camera-pose estimation, 3D reconstruction, map extrapolation, or missing-location inference.
- The method assumes both frames already use compatible planar coordinates and the same declared unit.
- Hold-out residuals within declared bounds show agreement with those supplied bounds for the tested points only. They do not establish accuracy elsewhere, independence of the survey, or scientific validity of the underlying observations.
- No unrecorded past or future state is recovered.

## Privacy and operation

This is a deterministic Python-core calculation. It does not access the browser, IndexedDB, camera, microphone, GPS, network, or SSSWET API. Callers should use opaque local evidence references rather than embedding personal information in IDs or free-text references. No raw media is required.

## Regression acceptance criteria

The dedicated tests require:

1. A synthetic rigid transform to produce zero hold-out residual within numerical tolerance.
2. An out-of-bound check point to be identified without changing the fitted transform.
3. Validation IDs to be disjoint from fit IDs and unique within the hold-out set.
4. One- and two-point hold-out sets to be reported as insufficient for the minimum screening count.
5. Reversed input order to produce identical fingerprints.
6. Changed coordinates to change the validation-input fingerprint.
7. Inconsistent matrices, non-finite values, negative uncertainty and oversized inputs to be rejected.
8. Output to explicitly deny CRS conversion, missing-location inference and historical/future recovery.

The tests use synthetic coordinates and do not measure real-world survey accuracy.

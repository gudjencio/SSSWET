from __future__ import annotations

from copy import deepcopy
from math import isfinite

import pytest

from ssswet_core.vtt_local_frame_alignment import fit_local_frame_alignment
from ssswet_core.vtt_local_frame_validation import validate_local_frame_alignment


def fitted_alignment():
    fit_points = [
        {"landmark_id": "fit-1", "source": [0, 0], "target": [10, 20],
         "source_uncertainty": 0.01, "target_uncertainty": 0.01},
        {"landmark_id": "fit-2", "source": [1, 0], "target": [10, 21],
         "source_uncertainty": 0.01, "target_uncertainty": 0.01},
        {"landmark_id": "fit-3", "source": [0, 1], "target": [9, 20],
         "source_uncertainty": 0.01, "target_uncertainty": 0.01},
    ]
    return fit_local_frame_alignment(
        fit_points, source_frame_id="local-a", target_frame_id="local-b",
        coordinate_unit="m",
    )


def holdout_points():
    return [
        {"landmark_id": "check-1", "source": [1, 1], "target": [9, 21],
         "source_uncertainty": 0.02, "target_uncertainty": 0.03, "source_ref": "local-check-1"},
        {"landmark_id": "check-2", "source": [2, 1], "target": [9, 22],
         "source_uncertainty": 0.02, "target_uncertainty": 0.03, "source_ref": "local-check-2"},
        {"landmark_id": "check-3", "source": [-1, 2], "target": [8, 19],
         "source_uncertainty": 0.02, "target_uncertainty": 0.03, "source_ref": "local-check-3"},
    ]


def test_holdout_validation_applies_transform_without_refitting():
    alignment = fitted_alignment()
    before = deepcopy(alignment)
    checks = holdout_points()
    result = validate_local_frame_alignment(alignment, checks)

    assert result["validation_status"] == "holdout_residuals_within_declared_bounds"
    assert result["validation_landmark_count"] == 3
    assert result["minimum_screening_count_met"] is True
    assert result["rms_residual"] == pytest.approx(0.0, abs=1e-12)
    assert result["maximum_residual"] == pytest.approx(0.0, abs=1e-12)
    assert result["all_residuals_within_declared_bounds"] is True
    assert result["validation_landmarks_used_to_refit_transform"] is False
    assert result["measurement_independence_established"] is False
    assert alignment == before


def test_holdout_validation_reports_out_of_bound_check_points():
    alignment = fitted_alignment()
    checks = holdout_points()
    checks[1]["target"] = [12, 22]
    result = validate_local_frame_alignment(alignment, checks)

    assert result["validation_status"] == "holdout_residuals_exceed_declared_bounds"
    assert result["all_residuals_within_declared_bounds"] is False
    assert result["outside_declared_bounds_ids"] == ["check-2"]
    assert result["maximum_residual"] > 0


def test_holdout_validation_requires_ids_disjoint_from_fit_set():
    checks = holdout_points()
    checks[0]["landmark_id"] = "fit-1"
    with pytest.raises(ValueError, match="disjoint"):
        validate_local_frame_alignment(fitted_alignment(), checks)


def test_holdout_validation_rejects_duplicate_ids_and_oversized_sets():
    checks = holdout_points()
    checks[1]["landmark_id"] = checks[0]["landmark_id"]
    with pytest.raises(ValueError, match="unique"):
        validate_local_frame_alignment(fitted_alignment(), checks)
    with pytest.raises(ValueError, match="1 to 200"):
        validate_local_frame_alignment(fitted_alignment(), holdout_points() * 67)


def test_holdout_validation_marks_small_samples_as_insufficient():
    result = validate_local_frame_alignment(fitted_alignment(), holdout_points()[:2])
    assert result["validation_status"] == "insufficient_holdout_count"
    assert result["minimum_screening_count_met"] is False
    assert result["all_residuals_within_declared_bounds"] is True


def test_holdout_fingerprints_are_order_independent_and_content_sensitive():
    alignment = fitted_alignment()
    checks = holdout_points()
    first = validate_local_frame_alignment(alignment, checks)
    second = validate_local_frame_alignment(alignment, list(reversed(checks)))
    assert first["transform_sha256"] == second["transform_sha256"]
    assert first["validation_input_sha256"] == second["validation_input_sha256"]

    changed = deepcopy(checks)
    changed[0]["target"] = [9.1, 21]
    third = validate_local_frame_alignment(alignment, changed)
    assert third["validation_input_sha256"] != first["validation_input_sha256"]


def test_holdout_validation_rejects_inconsistent_or_nonfinite_transform():
    alignment = fitted_alignment()
    alignment["transform"]["matrix"][0][0] += 0.1
    with pytest.raises(ValueError, match="inconsistent"):
        validate_local_frame_alignment(alignment, holdout_points())

    alignment = fitted_alignment()
    alignment["transform"]["translation"][0] = float("inf")
    with pytest.raises(ValueError, match="finite"):
        validate_local_frame_alignment(alignment, holdout_points())


def test_holdout_validation_rejects_invalid_uncertainty_and_numeric_overflow():
    checks = holdout_points()
    checks[0]["source_uncertainty"] = -1
    with pytest.raises(ValueError, match="non-negative"):
        validate_local_frame_alignment(fitted_alignment(), checks)

    checks = holdout_points()
    checks[0]["source"] = [10**10000, 0]
    with pytest.raises(ValueError, match="finite"):
        validate_local_frame_alignment(fitted_alignment(), checks)


def test_holdout_validation_is_deterministic_and_reports_declared_bound_semantics():
    result = validate_local_frame_alignment(fitted_alignment(), holdout_points())
    assert len(result["transform_sha256"]) == 64
    assert len(result["validation_input_sha256"]) == 64
    assert result["uncertainty_semantics"].startswith("Declared absolute radial")
    assert result["geographic_crs_conversion_performed"] is False
    assert result["unrecorded_locations_inferred"] is False
    assert result["historical_or_future_reality_recovered"] is False
    assert isfinite(result["rms_residual"])

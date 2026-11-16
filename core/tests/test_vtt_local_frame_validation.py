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



def support_fit_landmarks():
    return [
        {"landmark_id": "fit-a", "source": [0, 0], "target": [10, 20],
         "source_uncertainty": 0.01, "target_uncertainty": 0.02},
        {"landmark_id": "fit-b", "source": [4, 0], "target": [14, 20],
         "source_uncertainty": 0.01, "target_uncertainty": 0.02},
        {"landmark_id": "fit-c", "source": [4, 4], "target": [14, 24],
         "source_uncertainty": 0.01, "target_uncertainty": 0.02},
        {"landmark_id": "fit-d", "source": [0, 4], "target": [10, 24],
         "source_uncertainty": 0.01, "target_uncertainty": 0.02},
    ]


def test_spatial_support_classifies_inside_boundary_and_outside_fit_hulls():
    fit = support_fit_landmarks()
    alignment = fit_local_frame_alignment(
        fit, source_frame_id="local-a", target_frame_id="local-b",
        coordinate_unit="m",
    )
    checks = [
        {"landmark_id": "inside", "source": [1, 1], "target": [11, 21],
         "source_uncertainty": 0.01, "target_uncertainty": 0.01},
        {"landmark_id": "boundary", "source": [2, 0], "target": [12, 20],
         "source_uncertainty": 0.01, "target_uncertainty": 0.01},
        {"landmark_id": "outside", "source": [5, 1], "target": [15, 21],
         "source_uncertainty": 0.01, "target_uncertainty": 0.01},
    ]
    before = deepcopy(alignment)
    report = validate_local_frame_alignment(alignment, checks, fit_landmarks=fit)

    assert report["fit_landmark_input_verified"] is True
    assert report["spatial_support_assessed"] is True
    assert report["fit_input_sha256"] == alignment["fit_input_sha256"]
    support_by_id = {row["landmark_id"]: row for row in report["residuals"]}
    assert support_by_id["inside"]["source_spatial_support"] == "inside_fit_hull"
    assert support_by_id["boundary"]["source_spatial_support"] == "boundary_fit_hull"
    assert support_by_id["outside"]["source_spatial_support"] == "outside_fit_hull"
    assert support_by_id["inside"]["target_spatial_support"] == "inside_fit_hull"
    assert support_by_id["boundary"]["target_spatial_support"] == "boundary_fit_hull"
    assert support_by_id["outside"]["target_spatial_support"] == "outside_fit_hull"
    assert support_by_id["inside"]["spatial_support_status"] == "within_fit_hulls"
    assert support_by_id["boundary"]["spatial_support_status"] == "within_fit_hulls"
    assert support_by_id["outside"]["spatial_support_status"] == "outside_fit_hull"
    assert report["within_fit_hulls_count"] == 2
    assert report["outside_fit_hull_count"] == 1
    assert report["indeterminate_spatial_support_count"] == 0
    assert report["spatial_support_summary"]["source_frame"]["fit_hull_vertex_count"] == 4
    assert alignment == before


def test_spatial_support_requires_exact_fitted_input_digest_and_identifiers():
    fit = support_fit_landmarks()
    alignment = fit_local_frame_alignment(
        fit, source_frame_id="local-a", target_frame_id="local-b",
        coordinate_unit="m",
    )
    checks = [{
        "landmark_id": "check-one", "source": [1, 1], "target": [11, 21],
        "source_uncertainty": 0.01, "target_uncertainty": 0.01,
    }]
    for field, value in (("source", [-1, 0]), ("source_uncertainty", 0.5), ("source_ref", "changed-ref")):
        changed = deepcopy(fit)
        changed[0][field] = value
        with pytest.raises(ValueError, match="digest"):
            validate_local_frame_alignment(alignment, checks, fit_landmarks=changed)
    wrong_ids = deepcopy(fit)
    wrong_ids[0]["landmark_id"] = "other-fit"
    with pytest.raises(ValueError, match="exactly match"):
        validate_local_frame_alignment(alignment, checks, fit_landmarks=wrong_ids)


def test_spatial_support_is_indeterminate_for_collinear_fit_landmarks():
    fit = [
        {"landmark_id": "line-a", "source": [0, 0], "target": [10, 20],
         "source_uncertainty": 0.01, "target_uncertainty": 0.01},
        {"landmark_id": "line-b", "source": [2, 0], "target": [12, 20],
         "source_uncertainty": 0.01, "target_uncertainty": 0.01},
        {"landmark_id": "line-c", "source": [4, 0], "target": [14, 20],
         "source_uncertainty": 0.01, "target_uncertainty": 0.01},
    ]
    alignment = fit_local_frame_alignment(
        fit, source_frame_id="line-a", target_frame_id="line-b",
        coordinate_unit="m",
    )
    checks = [{
        "landmark_id": "line-check", "source": [1, 0], "target": [11, 20],
        "source_uncertainty": 0.01, "target_uncertainty": 0.01,
    }]
    report = validate_local_frame_alignment(alignment, checks, fit_landmarks=fit)
    assert report["spatial_support_assessed"] is True
    assert report["indeterminate_spatial_support_count"] == 1
    assert report["residuals"][0]["source_spatial_support"] == "insufficient_2d_fit_hull"
    assert report["residuals"][0]["target_spatial_support"] == "insufficient_2d_fit_hull"


def test_fit_input_fingerprint_is_order_independent_and_legacy_alignment_is_not_assessed():
    fit = support_fit_landmarks()
    alignment = fit_local_frame_alignment(
        fit, source_frame_id="local-a", target_frame_id="local-b",
        coordinate_unit="m",
    )
    reversed_alignment = fit_local_frame_alignment(
        list(reversed(fit)), source_frame_id="local-a", target_frame_id="local-b",
        coordinate_unit="m",
    )
    assert alignment["fit_input_sha256"] == reversed_alignment["fit_input_sha256"]
    checks = [{
        "landmark_id": "legacy-check", "source": [1, 1], "target": [11, 21],
        "source_uncertainty": 0.01, "target_uncertainty": 0.01,
    }]
    report = validate_local_frame_alignment(alignment, checks)
    assert report["spatial_support_assessed"] is False
    assert report["not_assessed_spatial_support_count"] == 1
    assert report["residuals"][0]["spatial_support_status"] == "not_assessed"

    legacy_alignment = deepcopy(alignment)
    legacy_alignment.pop("fit_input_sha256")
    legacy_report = validate_local_frame_alignment(legacy_alignment, checks)
    assert legacy_report["spatial_support_assessed"] is False
    with pytest.raises(ValueError, match="does not bind"):
        validate_local_frame_alignment(legacy_alignment, checks, fit_landmarks=fit)



def test_source_and_target_hull_support_are_reported_independently():
    fit = support_fit_landmarks()
    alignment = fit_local_frame_alignment(
        fit, source_frame_id="local-a", target_frame_id="local-b",
        coordinate_unit="m",
    )
    checks = [{
        "landmark_id": "mixed-support", "source": [1, 1], "target": [20, 20],
        "source_uncertainty": 0.01, "target_uncertainty": 0.01,
    }]
    report = validate_local_frame_alignment(alignment, checks, fit_landmarks=fit)
    row = report["residuals"][0]
    assert row["source_spatial_support"] == "inside_fit_hull"
    assert row["target_spatial_support"] == "outside_fit_hull"
    assert row["spatial_support_status"] == "outside_fit_hull"
    assert report["outside_fit_hull_count"] == 1

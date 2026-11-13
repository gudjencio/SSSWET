"""Independent hold-out checks for Virtual Time Mapping local-frame transforms.

The validator evaluates a previously fitted 2D rigid transform against a
separate set of paired landmarks. It never refits the transform.
"""
from __future__ import annotations

import hashlib
import json
from math import cos, hypot, isfinite, sin, sqrt
from typing import Any

MAX_VALIDATION_LANDMARKS = 200
MAX_IDENTIFIER_LENGTH = 160
MAX_REFERENCE_LENGTH = 500
MIN_SCREENING_LANDMARKS = 3
_NUMERIC_TOLERANCE = 1e-9


def _number(value: Any, field: str, *, nonnegative: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be numeric")
    try:
        result = float(value)
    except (OverflowError, TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be finite") from exc
    if not isfinite(result) or (nonnegative and result < 0):
        raise ValueError(
            f"{field} must be finite" + (" and non-negative" if nonnegative else "")
        )
    return result


def _identifier(value: Any, field: str, *, maximum: int = MAX_IDENTIFIER_LENGTH) -> str:
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > maximum:
        raise ValueError(f"{field} must contain 1 to {maximum} characters")
    return value.strip()


def _point(value: Any, field: str) -> tuple[float, float]:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError(f"{field} must contain exactly two coordinates")
    return (_number(value[0], field), _number(value[1], field))


def _close(actual: float, expected: float) -> bool:
    return abs(actual - expected) <= _NUMERIC_TOLERANCE * max(1.0, abs(expected))


def _canonical_digest(payload: dict[str, Any]) -> str:
    try:
        encoded = json.dumps(
            payload, ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("validation payload is not canonically serializable") from exc
    return hashlib.sha256(encoded).hexdigest()


def _read_alignment(alignment: Any) -> dict[str, Any]:
    if not isinstance(alignment, dict):
        raise ValueError("alignment must be an object")
    version = alignment.get("schema_version")
    if isinstance(version, bool) or version != 1:
        raise ValueError("alignment schema_version 1 is required")

    source_frame_id = _identifier(alignment.get("source_frame_id"), "source_frame_id", maximum=120)
    target_frame_id = _identifier(alignment.get("target_frame_id"), "target_frame_id", maximum=120)
    coordinate_unit = _identifier(alignment.get("coordinate_unit"), "coordinate_unit", maximum=120)
    if source_frame_id == target_frame_id:
        raise ValueError("source and target frames must be distinct")

    if alignment.get("transform_is_extrapolated") is not False:
        raise ValueError("only a non-extrapolated fitted transform can be checked")
    if alignment.get("geographic_crs_conversion_performed") is not False:
        raise ValueError("geographic CRS conversion is outside this validator")
    if alignment.get("unrecorded_locations_inferred") is not False:
        raise ValueError("alignment must not claim inferred locations")
    if alignment.get("historical_or_future_reality_recovered") is not False:
        raise ValueError("alignment must not claim historical or future recovery")

    fit_residuals = alignment.get("residuals")
    fit_count = alignment.get("landmark_count")
    if (
        not isinstance(fit_count, int) or isinstance(fit_count, bool)
        or not 2 <= fit_count <= 200
        or not isinstance(fit_residuals, list)
        or len(fit_residuals) != fit_count
    ):
        raise ValueError("alignment must retain its bounded fitted-landmark identifiers")

    fit_ids = set()
    for item in fit_residuals:
        if not isinstance(item, dict):
            raise ValueError("fitted residual records must be objects")
        landmark_id = _identifier(item.get("landmark_id"), "fitted landmark_id")
        if landmark_id in fit_ids:
            raise ValueError("fitted landmark IDs must be unique")
        fit_ids.add(landmark_id)

    transform = alignment.get("transform")
    if not isinstance(transform, dict):
        raise ValueError("alignment transform must be an object")
    angle = _number(transform.get("rotation_radians"), "rotation_radians")
    translation = transform.get("translation")
    if not isinstance(translation, (list, tuple)) or len(translation) != 2:
        raise ValueError("transform translation must contain two coordinates")
    tx, ty = (_number(translation[0], "translation"), _number(translation[1], "translation"))

    raw_matrix = transform.get("matrix")
    if not isinstance(raw_matrix, (list, tuple)) or len(raw_matrix) != 3:
        raise ValueError("transform matrix must be 3 by 3")
    matrix = []
    for row in raw_matrix:
        if not isinstance(row, (list, tuple)) or len(row) != 3:
            raise ValueError("transform matrix must be 3 by 3")
        matrix.append([_number(value, "transform matrix") for value in row])

    c, s = cos(angle), sin(angle)
    expected = [[c, -s, tx], [s, c, ty], [0.0, 0.0, 1.0]]
    if any(
        not _close(matrix[row][column], expected[row][column])
        for row in range(3) for column in range(3)
    ):
        raise ValueError("transform matrix is inconsistent with its rotation and translation")
    determinant = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    if not isfinite(determinant) or not _close(determinant, 1.0):
        raise ValueError("transform matrix is not a proper 2D rigid rotation")

    normalized_transform = {
        "rotation_radians": angle,
        "translation": [tx, ty],
        "matrix": matrix,
    }
    transform_payload = {
        "schema_version": 1,
        "source_frame_id": source_frame_id,
        "target_frame_id": target_frame_id,
        "coordinate_unit": coordinate_unit,
        "transform": normalized_transform,
    }
    return {
        "source_frame_id": source_frame_id,
        "target_frame_id": target_frame_id,
        "coordinate_unit": coordinate_unit,
        "matrix": matrix,
        "fit_ids": fit_ids,
        "transform_sha256": _canonical_digest(transform_payload),
    }


def validate_local_frame_alignment(
    alignment: dict[str, Any],
    validation_landmarks: list[dict[str, Any]],
) -> dict[str, Any]:
    """Evaluate a fitted transform on separate landmark IDs without refitting.

    source_uncertainty and target_uncertainty are interpreted as declared
    absolute radial bounds in coordinate_unit. Their sum is a conservative
    residual bound under the triangle inequality; it is not a confidence
    interval or a standard deviation.
    """
    fitted = _read_alignment(alignment)
    if (
        not isinstance(validation_landmarks, list)
        or not 1 <= len(validation_landmarks) <= MAX_VALIDATION_LANDMARKS
    ):
        raise ValueError(
            f"validation_landmarks must contain 1 to {MAX_VALIDATION_LANDMARKS} records"
        )

    normalized = []
    seen = set()
    for item in validation_landmarks:
        if not isinstance(item, dict):
            raise ValueError("every validation landmark must be an object")
        landmark_id = _identifier(item.get("landmark_id"), "landmark_id")
        if landmark_id in seen:
            raise ValueError("validation landmark IDs must be unique")
        if landmark_id in fitted["fit_ids"]:
            raise ValueError("validation landmark IDs must be disjoint from fitted landmark IDs")
        seen.add(landmark_id)

        source = _point(item.get("source"), "source")
        target = _point(item.get("target"), "target")
        source_bound = _number(item.get("source_uncertainty"), "source_uncertainty", nonnegative=True)
        target_bound = _number(item.get("target_uncertainty"), "target_uncertainty", nonnegative=True)
        combined_bound = source_bound + target_bound
        if not isfinite(combined_bound):
            raise ValueError("combined declared uncertainty bound exceeds finite numeric range")
        source_ref = item.get("source_ref", "")
        if not isinstance(source_ref, str) or len(source_ref) > MAX_REFERENCE_LENGTH:
            raise ValueError(f"source_ref must be text of at most {MAX_REFERENCE_LENGTH} characters")

        normalized.append({
            "landmark_id": landmark_id,
            "source": [source[0], source[1]],
            "target": [target[0], target[1]],
            "source_uncertainty": source_bound,
            "target_uncertainty": target_bound,
            "declared_combined_uncertainty_bound": combined_bound,
            "source_ref": source_ref,
        })

    matrix = fitted["matrix"]
    residuals = []
    residual_values = []
    for item in sorted(normalized, key=lambda row: row["landmark_id"]):
        x, y = item["source"]
        predicted_x = matrix[0][0] * x + matrix[0][1] * y + matrix[0][2]
        predicted_y = matrix[1][0] * x + matrix[1][1] * y + matrix[1][2]
        if not isfinite(predicted_x) or not isfinite(predicted_y):
            raise ValueError("predicted validation coordinate exceeds finite numeric range")
        delta_x = predicted_x - item["target"][0]
        delta_y = predicted_y - item["target"][1]
        residual = hypot(delta_x, delta_y)
        if not isfinite(residual):
            raise ValueError("validation residual exceeds finite numeric range")
        bound = item["declared_combined_uncertainty_bound"]
        tolerance = max(_NUMERIC_TOLERANCE, abs(bound) * 1e-12)
        within = residual <= bound + tolerance
        residual_values.append(residual)
        residuals.append({
            "landmark_id": item["landmark_id"],
            "residual": residual,
            "declared_combined_uncertainty_bound": bound,
            "within_declared_bound": within,
            "source_ref": item["source_ref"],
        })

    count = len(residuals)
    rms = hypot(*residual_values) / sqrt(count)
    maximum = max(residual_values)
    within_count = sum(item["within_declared_bound"] for item in residuals)
    all_within = within_count == count
    minimum_count_met = count >= MIN_SCREENING_LANDMARKS
    if not minimum_count_met:
        status = "insufficient_holdout_count"
    elif all_within:
        status = "holdout_residuals_within_declared_bounds"
    else:
        status = "holdout_residuals_exceed_declared_bounds"

    input_payload = {
        "schema_version": 1,
        "source_frame_id": fitted["source_frame_id"],
        "target_frame_id": fitted["target_frame_id"],
        "coordinate_unit": fitted["coordinate_unit"],
        "transform_sha256": fitted["transform_sha256"],
        "validation_landmarks": normalized,
    }
    return {
        "schema_version": 1,
        "method": "apply_existing_2d_rigid_transform_without_refitting",
        "source_frame_id": fitted["source_frame_id"],
        "target_frame_id": fitted["target_frame_id"],
        "coordinate_unit": fitted["coordinate_unit"],
        "transform_sha256": fitted["transform_sha256"],
        "validation_input_sha256": _canonical_digest(input_payload),
        "validation_landmark_count": count,
        "minimum_screening_landmarks": MIN_SCREENING_LANDMARKS,
        "minimum_screening_count_met": minimum_count_met,
        "residuals": residuals,
        "rms_residual": rms,
        "maximum_residual": maximum,
        "within_declared_bounds_count": within_count,
        "outside_declared_bounds_ids": [
            item["landmark_id"] for item in residuals if not item["within_declared_bound"]
        ],
        "all_residuals_within_declared_bounds": all_within,
        "validation_status": status,
        "validation_ids_disjoint_from_fit_ids": True,
        "measurement_independence_established": False,
        "spatial_generalization_established": False,
        "validation_landmarks_used_to_refit_transform": False,
        "geographic_crs_conversion_performed": False,
        "unrecorded_locations_inferred": False,
        "historical_or_future_reality_recovered": False,
        "uncertainty_semantics": (
            "Declared absolute radial coordinate bounds combined by the triangle "
            "inequality; not standard deviations or confidence intervals."
        ),
    }

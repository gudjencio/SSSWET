"""Conservative 2D point-covariance propagation for Virtual Time Mapping.

The rotation is treated as exact. transform_covariance is the covariance
of translation only, expressed in the target frame. Point and translation
errors are assumed independent; rotation-parameter uncertainty and
cross-covariance are not represented.
"""
from __future__ import annotations

from math import atan2, cos, hypot, isfinite, sin, sqrt
from typing import Any

CHI_SQUARE_2D_95 = 5.991464547107979
MAX_ABSOLUTE_INPUT = 1e100
_MATRIX_TOLERANCE = 1e-9
_PSD_RELATIVE_TOLERANCE = 1e-12


def _number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must contain finite numeric values")
    try:
        result = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError(f"{field} must contain finite numeric values") from exc
    if not isfinite(result) or abs(result) > MAX_ABSOLUTE_INPUT:
        raise ValueError(f"{field} must contain finite values within the supported numeric range")
    return result


def _vector(value: Any, field: str) -> tuple[float, float]:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError(f"{field} must contain exactly two coordinates")
    return (_number(value[0], field), _number(value[1], field))


def _matrix(value: Any, field: str) -> list[list[float]]:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError(f"{field} must be a 2 by 2 matrix")
    rows = []
    for row in value:
        if not isinstance(row, (list, tuple)) or len(row) != 2:
            raise ValueError(f"{field} must be a 2 by 2 matrix")
        rows.append([_number(item, field) for item in row])
    return rows


def _rotation(value: Any) -> list[list[float]]:
    matrix = _matrix(value, "rotation_matrix")
    a, b = matrix[0]
    c, d = matrix[1]
    row0_norm = a * a + b * b
    row1_norm = c * c + d * d
    row_dot = a * c + b * d
    determinant = a * d - b * c
    if (
        abs(row0_norm - 1.0) > _MATRIX_TOLERANCE
        or abs(row1_norm - 1.0) > _MATRIX_TOLERANCE
        or abs(row_dot) > _MATRIX_TOLERANCE
        or abs(determinant - 1.0) > _MATRIX_TOLERANCE
    ):
        raise ValueError("rotation_matrix must be a proper orthonormal 2D rotation")
    return matrix


def _project_covariance(value: Any, field: str) -> list[list[float]]:
    matrix = _matrix(value, field)
    a, b = matrix[0]
    c, d = matrix[1]
    scale = max(abs(a), abs(b), abs(c), abs(d), 1e-300)
    tolerance = _PSD_RELATIVE_TOLERANCE * scale
    if abs(b - c) > tolerance:
        raise ValueError(f"{field} must be symmetric")
    off_diagonal = (b + c) / 2.0

    midpoint = (a + d) / 2.0
    half_difference = (a - d) / 2.0
    radius = hypot(half_difference, off_diagonal)
    largest = midpoint + radius
    smallest = midpoint - radius
    if not isfinite(largest) or not isfinite(smallest) or smallest < -tolerance:
        raise ValueError(f"{field} must be positive semidefinite")

    # Remove only tiny negative eigenvalues attributable to floating-point
    # round-off; materially indefinite covariance matrices are rejected above.
    largest = max(0.0, largest)
    smallest = max(0.0, smallest)
    if radius <= tolerance:
        diagonal = max(0.0, midpoint)
        return [[diagonal, 0.0], [0.0, diagonal]]

    angle = 0.5 * atan2(2.0 * off_diagonal, a - d)
    vx, vy = cos(angle), sin(angle)
    wx, wy = -vy, vx
    out00 = largest * vx * vx + smallest * wx * wx
    out01 = largest * vx * vy + smallest * wx * wy
    out11 = largest * vy * vy + smallest * wy * wy
    out00 = 0.0 if abs(out00) <= tolerance else out00
    out01 = 0.0 if abs(out01) <= tolerance else out01
    out11 = 0.0 if abs(out11) <= tolerance else out11
    return [[out00, out01], [out01, out11]]


def _eigenvalues_symmetric_2x2(matrix: list[list[float]]) -> tuple[float, float, float]:
    a, b = matrix[0]
    _, d = matrix[1]
    angle = 0.5 * atan2(2.0 * b, a - d)
    midpoint = (a + d) / 2.0
    radius = hypot((a - d) / 2.0, b)
    return max(0.0, midpoint + radius), max(0.0, midpoint - radius), angle


def transform_point_with_covariance(
    point: list[float] | tuple[float, float],
    rotation_matrix: list[list[float]] | tuple[tuple[float, float], tuple[float, float]],
    translation: list[float] | tuple[float, float],
    point_covariance: list[list[float]] | tuple[tuple[float, float], tuple[float, float]],
    transform_covariance: list[list[float]] | tuple[tuple[float, float], tuple[float, float]],
    *,
    coordinate_unit: str,
) -> dict:
    """Transform a 2D point and propagate its declared covariance.

    point_covariance is expressed in the source frame. The rotation is
    treated as exact and pushes it into the target frame as R C R^T.
    transform_covariance is translation-only covariance in the target
    frame. It is added under an explicit independence assumption.

    The reported 95% ellipse is conditional on a bivariate-Gaussian error
    interpretation. It is not an absolute error bound or a calibrated GPS
    confidence region.
    """
    if not isinstance(coordinate_unit, str) or not coordinate_unit.strip() or len(coordinate_unit.strip()) > 32:
        raise ValueError("coordinate_unit must contain 1 to 32 characters")
    x, y = _vector(point, "point")
    tx, ty = _vector(translation, "translation")
    rotation = _rotation(rotation_matrix)
    point_cov = _project_covariance(point_covariance, "point_covariance")
    translation_cov = _project_covariance(transform_covariance, "transform_covariance")

    r00, r01 = rotation[0]
    r10, r11 = rotation[1]
    transformed_x = r00 * x + r01 * y + tx
    transformed_y = r10 * x + r11 * y + ty
    if (not isfinite(transformed_x) or not isfinite(transformed_y)
            or abs(transformed_x) > MAX_ABSOLUTE_INPUT or abs(transformed_y) > MAX_ABSOLUTE_INPUT):
        raise ValueError("transformed point exceeds finite numeric range")

    # R C R^T, evaluated explicitly for deterministic 2D arithmetic.
    pc00, pc01 = point_cov[0]
    _, pc11 = point_cov[1]
    rc00 = r00 * pc00 + r01 * pc01
    rc01 = r00 * pc01 + r01 * pc11
    rc10 = r10 * pc00 + r11 * pc01
    rc11 = r10 * pc01 + r11 * pc11
    rotated00 = rc00 * r00 + rc01 * r01
    rotated01a = rc00 * r10 + rc01 * r11
    rotated01b = rc10 * r00 + rc11 * r01
    rotated11 = rc10 * r10 + rc11 * r11

    covariance = [
        [rotated00 + translation_cov[0][0], (rotated01a + rotated01b) / 2.0 + translation_cov[0][1]],
        [(rotated01a + rotated01b) / 2.0 + translation_cov[1][0], rotated11 + translation_cov[1][1]],
    ]
    covariance = _project_covariance(covariance, "propagated covariance")
    if not all(isfinite(item) and abs(item) <= MAX_ABSOLUTE_INPUT for row in covariance for item in row):
        raise ValueError("propagated covariance exceeds finite numeric range")

    major_eigenvalue, minor_eigenvalue, orientation = _eigenvalues_symmetric_2x2(covariance)
    major_axis = sqrt(major_eigenvalue * CHI_SQUARE_2D_95)
    minor_axis = sqrt(minor_eigenvalue * CHI_SQUARE_2D_95)
    if not all(isfinite(item) for item in (major_axis, minor_axis, orientation)):
        raise ValueError("uncertainty ellipse exceeds finite numeric range")

    return {
        "schema_version": 1,
        "method": "linear_point_covariance_pushforward_plus_translation_covariance",
        "coordinate_unit": coordinate_unit.strip(),
        "transformed_point": [transformed_x, transformed_y],
        "covariance": covariance,
        "point_covariance_after_rotation": [
            [rotated00, (rotated01a + rotated01b) / 2.0],
            [(rotated01a + rotated01b) / 2.0, rotated11],
        ],
        "translation_covariance": translation_cov,
        "covariance_eigenvalues": {
            "major": major_eigenvalue,
            "minor": minor_eigenvalue,
        },
        "major_95_ellipse_axis": major_axis,
        "minor_95_ellipse_axis": minor_axis,
        "ellipse_axis_semantics": "semi-axis lengths in coordinate_unit",
        "major_axis_orientation_radians": orientation,
        "confidence_level": 0.95,
        "confidence_region_method": "two_dimensional_chi_square_contour",
        "confidence_region_assumption": (
            "Nominal 95% contour conditional on bivariate-Gaussian errors, "
            "exact rotation, and independent point and translation errors."
        ),
        "assumptions": {
            "rotation_treated_as_exact": True,
            "transform_covariance_is_translation_only": True,
            "point_and_translation_errors_assumed_independent": True,
            "cross_covariance_modelled": False,
            "rotation_parameter_uncertainty_included": False,
        },
        "geographic_conversion_performed": False,
        "unrecorded_locations_inferred": False,
        "historical_or_future_reality_recovered": False,
    }

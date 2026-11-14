"""Propagate 2D local-frame point covariance through a validated rigid transform."""
from __future__ import annotations
import math
from .assurance_common import finite_number, text

CHI2_2D_95 = 5.991464547107979


def _vector(value, field):
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError(f"{field} must contain two numbers")
    return [finite_number(item, field) for item in value]


def _matrix(value, field):
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError(f"{field} must be a 2x2 matrix")
    rows = [_vector(row, field) for row in value]
    if abs(rows[0][1] - rows[1][0]) > 1e-9:
        raise ValueError(f"{field} must be symmetric")
    a, b, d = rows[0][0], rows[0][1], rows[1][1]
    if a < -1e-10 or d < -1e-10 or a * d - b * b < -1e-10:
        raise ValueError(f"{field} must be positive semidefinite")
    return [[a, b], [b, d]]


def transform_point_with_covariance(point, rotation, translation, source_covariance, registration_covariance, *, coordinate_unit: str) -> dict:
    p = _vector(point, "point")
    t = _vector(translation, "translation")
    if not isinstance(rotation, (list, tuple)) or len(rotation) != 2:
        raise ValueError("rotation must be a 2x2 matrix")
    r = [_vector(row, "rotation") for row in rotation]
    dot00 = r[0][0] ** 2 + r[1][0] ** 2
    dot11 = r[0][1] ** 2 + r[1][1] ** 2
    dot01 = r[0][0] * r[0][1] + r[1][0] * r[1][1]
    determinant = r[0][0] * r[1][1] - r[0][1] * r[1][0]
    if max(abs(dot00 - 1), abs(dot11 - 1), abs(dot01), abs(determinant - 1)) > 1e-6:
        raise ValueError("rotation must be a proper orthonormal 2D rotation")
    cs = _matrix(source_covariance, "source_covariance")
    cr = _matrix(registration_covariance, "registration_covariance")
    unit = text(coordinate_unit, "coordinate_unit", 40)
    mapped = [r[0][0] * p[0] + r[0][1] * p[1] + t[0], r[1][0] * p[0] + r[1][1] * p[1] + t[1]]
    temp = [[sum(r[i][k] * cs[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
    propagated = [[sum(temp[i][k] * r[j][k] for k in range(2)) + cr[i][j] for j in range(2)] for i in range(2)]
    a, b, d = propagated[0][0], (propagated[0][1] + propagated[1][0]) / 2, propagated[1][1]
    mean = (a + d) / 2
    radius = math.sqrt(max(0.0, ((a - d) / 2) ** 2 + b ** 2))
    eigen_max, eigen_min = max(0.0, mean + radius), max(0.0, mean - radius)
    angle = 0.5 * math.atan2(2 * b, a - d) if abs(a - d) + abs(b) > 1e-15 else 0.0
    return {"transformed_point": [round(value, 12) for value in mapped], "covariance": [[round(value, 12) for value in row] for row in propagated], "major_95_ellipse_axis": math.sqrt(eigen_max * CHI2_2D_95), "minor_95_ellipse_axis": math.sqrt(eigen_min * CHI2_2D_95), "major_axis_angle_radians": angle, "coordinate_unit": unit, "uncertainty_model": "independent_gaussian_2d_covariance_approximation", "geographic_conversion_performed": False, "3d_reconstruction_performed": False, "physical_accuracy_certified": False}

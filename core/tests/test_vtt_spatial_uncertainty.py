import math
import random

import pytest

from ssswet_core.vtt_spatial_uncertainty import transform_point_with_covariance


def test_rotated_point_covariance_and_translation_covariance_are_combined():
    result = transform_point_with_covariance(
        [1, 0], [[0, -1], [1, 0]], [10, 20],
        [[4, 0], [0, 1]], [[1, 0], [0, 1]], coordinate_unit="m",
    )
    assert result["schema_version"] == 1
    assert result["transformed_point"] == [10.0, 21.0]
    assert result["covariance"] == [[2.0, 0.0], [0.0, 5.0]]
    assert result["major_95_ellipse_axis"] > result["minor_95_ellipse_axis"]
    assert result["confidence_level"] == 0.95
    assert result["assumptions"]["rotation_parameter_uncertainty_included"] is False
    assert "rotation_uncertainty_covariance" not in result
    assert result["geographic_conversion_performed"] is False


def test_zero_covariance_produces_zero_semiaxes():
    result = transform_point_with_covariance(
        [2, -3], [[1, 0], [0, 1]], [4, 5],
        [[0, 0], [0, 0]], [[0, 0], [0, 0]], coordinate_unit="m",
    )
    assert result["transformed_point"] == [6.0, 2.0]
    assert result["covariance"] == [[0.0, 0.0], [0.0, 0.0]]
    assert result["major_95_ellipse_axis"] == 0.0
    assert result["minor_95_ellipse_axis"] == 0.0


def test_covariance_is_rotated_into_target_axes_before_translation_uncertainty():
    result = transform_point_with_covariance(
        [0, 0], [[0, -1], [1, 0]], [0, 0],
        [[9, 0], [0, 1]], [[0, 0], [0, 0]], coordinate_unit="m",
    )
    assert result["covariance"][0][0] == pytest.approx(1)
    assert result["covariance"][0][1] == pytest.approx(0)
    assert result["covariance"][1][0] == pytest.approx(0)
    assert result["covariance"][1][1] == pytest.approx(9)
    assert result["major_axis_orientation_radians"] == pytest.approx(math.pi / 2)


def test_rejects_non_rotation_and_reflection_matrices():
    for matrix in ([[2, 0], [0, 1]], [[1, 0], [0, -1]]):
        with pytest.raises(ValueError, match="proper orthonormal"):
            transform_point_with_covariance(
                [0, 0], matrix, [0, 0], [[1, 0], [0, 1]],
                [[0, 0], [0, 0]], coordinate_unit="m",
            )


def test_rejects_nonsymmetric_and_indefinite_covariances():
    with pytest.raises(ValueError, match="positive semidefinite"):
        transform_point_with_covariance(
            [0, 0], [[1, 0], [0, 1]], [0, 0],
            [[1, 2], [2, 1]], [[0, 0], [0, 0]], coordinate_unit="m",
        )
    with pytest.raises(ValueError, match="symmetric"):
        transform_point_with_covariance(
            [0, 0], [[1, 0], [0, 1]], [0, 0],
            [[1, 0], [1, 1]], [[0, 0], [0, 0]], coordinate_unit="m",
        )


def test_rejects_invalid_dimensions_nonfinite_values_and_bad_units():
    with pytest.raises(ValueError, match="exactly two"):
        transform_point_with_covariance(
            [0], [[1, 0], [0, 1]], [0, 0],
            [[1, 0], [0, 1]], [[0, 0], [0, 0]], coordinate_unit="m",
        )
    with pytest.raises(ValueError, match="finite"):
        transform_point_with_covariance(
            [float("nan"), 0], [[1, 0], [0, 1]], [0, 0],
            [[1, 0], [0, 1]], [[0, 0], [0, 0]], coordinate_unit="m",
        )
    with pytest.raises(ValueError, match="coordinate_unit"):
        transform_point_with_covariance(
            [0, 0], [[1, 0], [0, 1]], [0, 0],
            [[1, 0], [0, 1]], [[0, 0], [0, 0]], coordinate_unit="",
        )


def test_small_roundoff_negative_eigenvalue_is_clipped_but_material_negative_is_rejected():
    result = transform_point_with_covariance(
        [0, 0], [[1, 0], [0, 1]], [0, 0],
        [[1, 0], [0, -1e-14]], [[0, 0], [0, 0]], coordinate_unit="m",
    )
    assert result["covariance"][1][1] == 0.0
    with pytest.raises(ValueError, match="positive semidefinite"):
        transform_point_with_covariance(
            [0, 0], [[1, 0], [0, 1]], [0, 0],
            [[1, 0], [0, -1e-4]], [[0, 0], [0, 0]], coordinate_unit="m",
        )


def test_covariance_result_is_symmetric_and_discloses_gaussian_assumption():
    result = transform_point_with_covariance(
        [3, 4], [[0.8, -0.6], [0.6, 0.8]], [1, 2],
        [[2, 0.2], [0.2, 1]], [[0.5, 0.1], [0.1, 0.7]], coordinate_unit="ft",
    )
    assert result["covariance"][0][1] == pytest.approx(result["covariance"][1][0])
    assert "bivariate-Gaussian" in result["confidence_region_assumption"]
    assert result["assumptions"]["point_and_translation_errors_assumed_independent"] is True
    assert result["historical_or_future_reality_recovered"] is False


def test_optional_rotation_variance_adds_first_order_jacobian_covariance():
    result = transform_point_with_covariance(
        [2, 0], [[1, 0], [0, 1]], [0, 0],
        [[0, 0], [0, 0]], [[0, 0], [0, 0]], coordinate_unit="m",
        rotation_variance_radians2=0.01,
    )
    assert result["schema_version"] == 2
    assert result["rotation_jacobian_target_units_per_radian"] == [0.0, 2.0]
    assert result["rotation_uncertainty_covariance"] == [[0.0, 0.0], [0.0, 0.04]]
    assert result["covariance"] == [[0.0, 0.0], [0.0, 0.04]]
    assert result["rotation_standard_deviation_radians"] == pytest.approx(0.1)
    assert result["assumptions"]["rotation_parameter_uncertainty_included"] is True
    assert result["assumptions"]["rotation_treated_as_exact"] is False
    assert result["assumptions"]["rotation_linearization"] == "first_order_small_angle_delta_method"
    assert "first-order small-angle" in result["confidence_region_assumption"]


def test_rotation_variance_is_combined_with_point_and_translation_covariance():
    result = transform_point_with_covariance(
        [1, 0], [[0, -1], [1, 0]], [10, 20],
        [[0, 0], [0, 0]], [[1, 0], [0, 1]], coordinate_unit="m",
        rotation_variance_radians2=0.01,
    )
    assert result["transformed_point"] == [10.0, 21.0]
    assert result["rotation_jacobian_target_units_per_radian"] == [-1.0, 0.0]
    assert result["rotation_uncertainty_covariance"] == [[0.01, 0.0], [0.0, 0.0]]
    assert result["covariance"][0][0] == pytest.approx(1.01)
    assert result["covariance"][0][1] == pytest.approx(0.0)
    assert result["covariance"][1][0] == pytest.approx(0.0)
    assert result["covariance"][1][1] == pytest.approx(1.0)


def test_explicit_zero_rotation_variance_uses_schema_v2_without_changing_covariance():
    result = transform_point_with_covariance(
        [2, 3], [[1, 0], [0, 1]], [4, 5],
        [[1, 0], [0, 2]], [[0.5, 0], [0, 0.5]], coordinate_unit="m",
        rotation_variance_radians2=0.0,
    )
    assert result["schema_version"] == 2
    assert result["covariance"] == [[1.5, 0.0], [0.0, 2.5]]
    assert result["rotation_uncertainty_covariance"] == [[0.0, 0.0], [0.0, 0.0]]
    assert result["assumptions"]["rotation_parameter_uncertainty_included"] is True
    assert result["assumptions"]["rotation_treated_as_exact"] is True
    assert result["assumptions"]["rotation_linearization"] == "not_required_zero_declared_variance"


def test_rotation_variance_rejects_negative_nonfinite_boolean_and_large_values():
    for invalid in (-0.01, float("nan"), float("inf"), True, 0.0625000001):
        with pytest.raises(ValueError, match="rotation_variance_radians2"):
            transform_point_with_covariance(
                [1, 2], [[1, 0], [0, 1]], [0, 0],
                [[0, 0], [0, 0]], [[0, 0], [0, 0]], coordinate_unit="m",
                rotation_variance_radians2=invalid,
            )
    boundary = transform_point_with_covariance(
        [1, 0], [[1, 0], [0, 1]], [0, 0],
        [[0, 0], [0, 0]], [[0, 0], [0, 0]], coordinate_unit="m",
        rotation_variance_radians2=0.0625,
    )
    assert boundary["rotation_standard_deviation_radians"] == 0.25


def test_small_angle_delta_method_matches_seeded_monte_carlo_rotation_only():
    rng = random.Random(20261115)
    point = (2.0, 3.0)
    theta = 0.4
    variance = 0.0001
    sigma = math.sqrt(variance)
    rotation = [[math.cos(theta), -math.sin(theta)], [math.sin(theta), math.cos(theta)]]
    result = transform_point_with_covariance(
        list(point), rotation, [0, 0],
        [[0, 0], [0, 0]], [[0, 0], [0, 0]], coordinate_unit="m",
        rotation_variance_radians2=variance,
    )
    jx, jy = result["rotation_jacobian_target_units_per_radian"]
    expected = [[variance * jx * jx, variance * jx * jy],
                [variance * jx * jy, variance * jy * jy]]

    samples = []
    for _ in range(40000):
        perturbed = theta + rng.gauss(0.0, sigma)
        samples.append((
            math.cos(perturbed) * point[0] - math.sin(perturbed) * point[1],
            math.sin(perturbed) * point[0] + math.cos(perturbed) * point[1],
        ))
    mean_x = sum(row[0] for row in samples) / len(samples)
    mean_y = sum(row[1] for row in samples) / len(samples)
    empirical = [
        [sum((row[0] - mean_x) ** 2 for row in samples) / (len(samples) - 1),
         sum((row[0] - mean_x) * (row[1] - mean_y) for row in samples) / (len(samples) - 1)],
        [sum((row[0] - mean_x) * (row[1] - mean_y) for row in samples) / (len(samples) - 1),
         sum((row[1] - mean_y) ** 2 for row in samples) / (len(samples) - 1)],
    ]
    for i in range(2):
        for j in range(2):
            assert empirical[i][j] == pytest.approx(expected[i][j], rel=0.04, abs=1e-7)

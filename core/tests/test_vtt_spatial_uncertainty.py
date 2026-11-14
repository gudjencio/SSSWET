import math

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

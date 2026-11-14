from __future__ import annotations

import math

import pytest

from ssswet_core.vtt_local_frame_alignment import fit_local_frame_alignment


def _fit(landmarks):
    return fit_local_frame_alignment(
        landmarks,
        source_frame_id="local-source",
        target_frame_id="local-target",
        coordinate_unit="m",
    )


def test_alignment_rejects_overflowed_combined_uncertainty_bound():
    landmarks = [
        {"landmark_id": "a", "source": [0, 0], "target": [0, 0],
         "source_uncertainty": 1e308, "target_uncertainty": 1e308},
        {"landmark_id": "b", "source": [1, 0], "target": [1, 0],
         "source_uncertainty": 1e308, "target_uncertainty": 1e308},
    ]
    with pytest.raises(ValueError, match="combined declared uncertainty bound"):
        _fit(landmarks)


def test_alignment_uses_overflow_safe_rms_for_large_finite_residuals():
    landmarks = [
        {"landmark_id": "a", "source": [0, 0], "target": [0, 0],
         "source_uncertainty": 0, "target_uncertainty": 0},
        {"landmark_id": "b", "source": [1, 0], "target": [1e155, 0],
         "source_uncertainty": 0, "target_uncertainty": 0},
        {"landmark_id": "c", "source": [0, 1], "target": [0, 1e155],
         "source_uncertainty": 0, "target_uncertainty": 0},
    ]
    result = _fit(landmarks)

    assert math.isfinite(result["rms_residual"])
    assert result["rms_residual"] == pytest.approx(6.666666666666666e154, rel=1e-12)
    assert math.isfinite(result["maximum_residual"])
    assert result["all_residuals_within_declared_bounds"] is False


def test_alignment_converts_unrepresentable_integer_coordinates_to_value_error():
    landmarks = [
        {"landmark_id": "a", "source": [10**10000, 0], "target": [0, 0],
         "source_uncertainty": 0, "target_uncertainty": 0},
        {"landmark_id": "b", "source": [1, 0], "target": [1, 0],
         "source_uncertainty": 0, "target_uncertainty": 0},
    ]
    with pytest.raises(ValueError, match="finite"):
        _fit(landmarks)

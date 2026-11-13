"""Local planar landmark alignment for Virtual Time Mapping."""
from __future__ import annotations

from math import atan2, cos, hypot, isfinite, sin, sqrt
from typing import Any

MAX_LANDMARKS = 200


def _number(value: Any, field: str, *, nonnegative: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be numeric")
    result = float(value)
    if not isfinite(result) or (nonnegative and result < 0):
        raise ValueError(f"{field} must be finite" + (" and non-negative" if nonnegative else ""))
    return result


def _point(value: Any, field: str) -> tuple[float, float]:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError(f"{field} must contain exactly two coordinates")
    return _number(value[0], field), _number(value[1], field)


def fit_local_frame_alignment(
    landmarks: list[dict[str, Any]], *,
    source_frame_id: str, target_frame_id: str, coordinate_unit: str,
) -> dict[str, Any]:
    """Fit a 2D rigid transform from paired landmarks and report residual bounds.

    This is not a geographic CRS converter, a 3D reconstruction tool or a
    method for estimating unobserved locations.
    """
    for value, field in (
        (source_frame_id, "source_frame_id"),
        (target_frame_id, "target_frame_id"),
        (coordinate_unit, "coordinate_unit"),
    ):
        if not isinstance(value, str) or not value.strip() or len(value) > 120:
            raise ValueError(f"{field} must contain 1 to 120 characters")
    if source_frame_id == target_frame_id:
        raise ValueError("source and target frames must be distinct")
    if not isinstance(landmarks, list) or not 2 <= len(landmarks) <= MAX_LANDMARKS:
        raise ValueError(f"landmarks must contain 2 to {MAX_LANDMARKS} paired records")

    normalized = []
    seen = set()
    for item in landmarks:
        if not isinstance(item, dict):
            raise ValueError("every landmark must be an object")
        landmark_id = item.get("landmark_id")
        if not isinstance(landmark_id, str) or not landmark_id.strip() or len(landmark_id) > 160:
            raise ValueError("landmark_id must contain 1 to 160 characters")
        landmark_id = landmark_id.strip()
        if landmark_id in seen:
            raise ValueError("landmark IDs must be unique")
        seen.add(landmark_id)
        source = _point(item.get("source"), "source")
        target = _point(item.get("target"), "target")
        source_bound = _number(item.get("source_uncertainty"), "source_uncertainty", nonnegative=True)
        target_bound = _number(item.get("target_uncertainty"), "target_uncertainty", nonnegative=True)
        normalized.append({
            "landmark_id": landmark_id, "source": source, "target": target,
            "declared_bound": source_bound + target_bound,
            "source_ref": item.get("source_ref") if isinstance(item.get("source_ref"), str) else "",
        })

    source_center = tuple(sum(item["source"][axis] for item in normalized) / len(normalized) for axis in (0, 1))
    target_center = tuple(sum(item["target"][axis] for item in normalized) / len(normalized) for axis in (0, 1))
    dot = cross = spread = 0.0
    for item in normalized:
        sx, sy = item["source"][0] - source_center[0], item["source"][1] - source_center[1]
        tx, ty = item["target"][0] - target_center[0], item["target"][1] - target_center[1]
        dot += sx * tx + sy * ty
        cross += sx * ty - sy * tx
        spread += sx * sx + sy * sy
    covariance_norm = hypot(dot, cross)
    if spread <= 1e-12 or covariance_norm <= 1e-12:
        raise ValueError("landmarks are geometrically degenerate for 2D rigid alignment")

    angle = atan2(cross, dot)
    c, s = cos(angle), sin(angle)
    tx = target_center[0] - (c * source_center[0] - s * source_center[1])
    ty = target_center[1] - (s * source_center[0] + c * source_center[1])
    residuals = []
    squared = []
    for item in sorted(normalized, key=lambda row: row["landmark_id"]):
        x, y = item["source"]
        predicted = (c * x - s * y + tx, s * x + c * y + ty)
        residual = hypot(predicted[0] - item["target"][0], predicted[1] - item["target"][1])
        within = residual <= item["declared_bound"] + 1e-9
        residuals.append({
            "landmark_id": item["landmark_id"], "residual": residual,
            "declared_combined_uncertainty_bound": item["declared_bound"],
            "within_declared_bound": within, "source_ref": item["source_ref"],
        })
        squared.append(residual * residual)
    rms = sqrt(sum(squared) / len(squared))
    maximum = max((item["residual"] for item in residuals), default=0.0)
    return {
        "schema_version": 1,
        "source_frame_id": source_frame_id.strip(),
        "target_frame_id": target_frame_id.strip(),
        "coordinate_unit": coordinate_unit.strip(),
        "transform": {
            "rotation_radians": angle, "translation": [tx, ty],
            "matrix": [[c, -s, tx], [s, c, ty], [0.0, 0.0, 1.0]],
        },
        "landmark_count": len(normalized),
        "residuals": residuals,
        "rms_residual": rms,
        "maximum_residual": maximum,
        "all_residuals_within_declared_bounds": all(item["within_declared_bound"] for item in residuals),
        "alignment_status": "residuals_within_declared_bounds" if all(item["within_declared_bound"] for item in residuals) else "residuals_exceed_declared_bounds",
        "transform_is_extrapolated": False,
        "geographic_crs_conversion_performed": False,
        "unrecorded_locations_inferred": False,
        "historical_or_future_reality_recovered": False,
    }

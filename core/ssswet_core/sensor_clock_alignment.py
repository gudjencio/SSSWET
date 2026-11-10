"""Robust, bounded alignment of independently clocked sensor streams.

The mapper is descriptive: it never changes source timestamps and never
extrapolates outside the interval covered by synchronization anchors.
"""
from __future__ import annotations

from math import isfinite
from statistics import median

MAX_ANCHORS = 200
MAX_OBSERVATIONS = 10_000


def _number(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError(f"{label} must be a finite number")
    return float(value)


def fit_clock_map(anchors: list[dict], *, max_drift_ppm: float = 5_000.0) -> dict:
    """Fit reference = slope * sensor + offset using Theil-Sen medians."""
    if not isinstance(anchors, list) or not 2 <= len(anchors) <= MAX_ANCHORS:
        raise ValueError(f"anchors must contain 2 to {MAX_ANCHORS} items")
    drift_limit = _number(max_drift_ppm, "max_drift_ppm")
    if not 0 < drift_limit <= 100_000:
        raise ValueError("max_drift_ppm must be in (0, 100000]")
    points, source_ids = [], set()
    for anchor in anchors:
        if not isinstance(anchor, dict):
            raise ValueError("each anchor must be an object")
        source_id = anchor.get("source_id")
        if not isinstance(source_id, str) or not source_id.strip() or len(source_id) > 200 or source_id in source_ids:
            raise ValueError("anchor source_id values must be unique non-empty strings")
        source_ids.add(source_id)
        sensor = _number(anchor.get("sensor_seconds"), "sensor_seconds")
        reference = _number(anchor.get("reference_seconds"), "reference_seconds")
        uncertainty = _number(anchor.get("uncertainty_seconds", 0.0), "uncertainty_seconds")
        if uncertainty < 0:
            raise ValueError("uncertainty_seconds cannot be negative")
        points.append((sensor, reference, uncertainty, source_id))
    points.sort(key=lambda item: item[0])
    if any(points[i][0] == points[i - 1][0] for i in range(1, len(points))):
        raise ValueError("sensor anchor times must be distinct")
    slopes = [
        (right[1] - left[1]) / (right[0] - left[0])
        for index, left in enumerate(points)
        for right in points[index + 1:]
    ]
    positive_slopes = [slope for slope in slopes if isfinite(slope) and slope > 0]
    if not positive_slopes:
        raise ValueError("anchors do not define a forward-running clock")
    slope = median(positive_slopes)
    drift_ppm = (slope - 1.0) * 1_000_000
    if abs(drift_ppm) > drift_limit:
        raise ValueError("estimated clock drift exceeds the configured limit")
    offset = median(reference - slope * sensor for sensor, reference, _, _ in points)
    residual_rows = [
        {"source_id": source_id, "residual_seconds": abs(reference - (slope * sensor + offset)), "declared_uncertainty_seconds": uncertainty}
        for sensor, reference, uncertainty, source_id in points
    ]
    residuals = sorted(item["residual_seconds"] for item in residual_rows)
    p95_index = max(0, min(len(residuals) - 1, int(0.95 * len(residuals) + 0.999999) - 1))
    residual_p95 = residuals[p95_index]
    anchor_uncertainty = max(item[2] for item in points)
    return {
        "schema_version": 1,
        "method": "theil_sen_pairwise_median",
        "slope": slope,
        "offset_seconds": offset,
        "drift_ppm": drift_ppm,
        "sensor_interval_seconds": [points[0][0], points[-1][0]],
        "reference_interval_seconds": [slope * points[0][0] + offset, slope * points[-1][0] + offset],
        "anchor_count": len(points),
        "source_ids": sorted(source_ids),
        "anchor_residuals": residual_rows,
        "residual_p95_seconds": residual_p95,
        "residual_max_seconds": residuals[-1],
        "alignment_uncertainty_seconds": residual_p95 + anchor_uncertainty,
        "extrapolation_allowed": False,
        "source_timestamps_mutated": False,
    }


def align_observations(observations: list[dict], clock_map: dict) -> dict:
    """Return aligned copies for observations inside the anchor interval only."""
    if not isinstance(observations, list) or len(observations) > MAX_OBSERVATIONS:
        raise ValueError(f"observations must be a list of at most {MAX_OBSERVATIONS} items")
    if not isinstance(clock_map, dict) or clock_map.get("schema_version") != 1 or clock_map.get("extrapolation_allowed") is not False:
        raise ValueError("a supported non-extrapolating clock map is required")
    interval = clock_map.get("sensor_interval_seconds")
    if not isinstance(interval, list) or len(interval) != 2:
        raise ValueError("clock map has no valid sensor interval")
    lower, upper = _number(interval[0], "interval start"), _number(interval[1], "interval end")
    slope, offset = _number(clock_map.get("slope"), "slope"), _number(clock_map.get("offset_seconds"), "offset_seconds")
    base_uncertainty = _number(clock_map.get("alignment_uncertainty_seconds"), "alignment_uncertainty_seconds")
    if slope <= 0 or base_uncertainty < 0 or lower >= upper:
        raise ValueError("clock map parameters are invalid")
    aligned, rejected = [], []
    for index, observation in enumerate(observations):
        if not isinstance(observation, dict):
            raise ValueError("each observation must be an object")
        timestamp = _number(observation.get("sensor_seconds"), "sensor_seconds")
        source_id = observation.get("source_id")
        if not isinstance(source_id, str) or not source_id.strip():
            raise ValueError("each observation needs a source_id")
        if not lower <= timestamp <= upper:
            rejected.append({"index": index, "source_id": source_id, "reason": "outside_anchor_interval"})
            continue
        local_uncertainty = _number(observation.get("uncertainty_seconds", 0.0), "uncertainty_seconds")
        if local_uncertainty < 0:
            raise ValueError("observation uncertainty cannot be negative")
        aligned.append({
            "source_id": source_id,
            "original_sensor_seconds": timestamp,
            "aligned_reference_seconds": slope * timestamp + offset,
            "combined_uncertainty_seconds": base_uncertainty + local_uncertainty,
            "derived": True,
            "source_timestamp_preserved": True,
        })
    return {"aligned": aligned, "rejected": rejected, "aligned_count": len(aligned), "rejected_count": len(rejected), "extrapolated_count": 0}

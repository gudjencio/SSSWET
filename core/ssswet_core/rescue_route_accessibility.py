"""Non-operational civil-rescue route segment accessibility screening."""
from __future__ import annotations

from math import isfinite
from typing import Any

MAX_SEGMENTS = 500


def _finite(value: Any, field: str, *, minimum: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be numeric")
    result = float(value)
    if not isfinite(result) or (minimum is not None and result < minimum):
        raise ValueError(f"{field} must be finite and in range")
    return result


def review_route_accessibility(
    segments: list[dict[str, Any]], *,
    minimum_clear_width_m: float,
    maximum_slope_percent: float,
    allowed_surfaces: list[str],
    maximum_obstructions: int = 0,
) -> dict[str, Any]:
    """Screen declared route measurements; never generate routes or dispatch responders."""
    min_width = _finite(minimum_clear_width_m, "minimum_clear_width_m", minimum=0)
    max_slope = _finite(maximum_slope_percent, "maximum_slope_percent", minimum=0)
    if isinstance(maximum_obstructions, bool) or not isinstance(maximum_obstructions, int) or maximum_obstructions < 0:
        raise ValueError("maximum_obstructions must be a non-negative integer")
    if not isinstance(allowed_surfaces, list) or not allowed_surfaces:
        raise ValueError("allowed_surfaces must be a non-empty list")
    surfaces = set()
    for surface in allowed_surfaces:
        if not isinstance(surface, str) or not surface.strip() or len(surface) > 100:
            raise ValueError("surface names must contain 1 to 100 characters")
        surfaces.add(surface.strip().casefold())
    if not isinstance(segments, list) or not 1 <= len(segments) <= MAX_SEGMENTS:
        raise ValueError(f"segments must contain 1 to {MAX_SEGMENTS} records")

    results = []
    previous_end = None
    continuity_gaps = []
    for index, item in enumerate(segments):
        if not isinstance(item, dict):
            raise ValueError("every route segment must be an object")
        segment_id = item.get("segment_id")
        start = item.get("from_node")
        end = item.get("to_node")
        if not isinstance(segment_id, str) or not segment_id.strip() or len(segment_id) > 160:
            raise ValueError("segment_id must contain 1 to 160 characters")
        if not isinstance(start, str) or not start.strip() or not isinstance(end, str) or not end.strip():
            raise ValueError("from_node and to_node are required")
        start, end = start.strip(), end.strip()
        if start == end:
            raise ValueError("a route segment must connect two distinct nodes")
        if previous_end is not None and start != previous_end:
            continuity_gaps.append({"previous_segment_end": previous_end, "current_segment_start": start, "segment_index": index})
        previous_end = end

        missing = []
        failures = []
        width = item.get("clear_width_m")
        slope = item.get("slope_percent")
        surface = item.get("surface")
        obstructions = item.get("obstruction_count")
        if width is None:
            missing.append("clear_width_m")
        else:
            width = _finite(width, "clear_width_m", minimum=0)
            if width < min_width:
                failures.append("clear_width_below_declared_minimum")
        if slope is None:
            missing.append("slope_percent")
        else:
            slope = _finite(slope, "slope_percent", minimum=0)
            if slope > max_slope:
                failures.append("slope_above_declared_maximum")
        if not isinstance(surface, str) or not surface.strip():
            missing.append("surface")
        elif surface.strip().casefold() not in surfaces:
            failures.append("surface_not_in_declared_allowlist")
        if obstructions is None:
            missing.append("obstruction_count")
        elif isinstance(obstructions, bool) or not isinstance(obstructions, int) or obstructions < 0:
            raise ValueError("obstruction_count must be a non-negative integer")
        elif obstructions > maximum_obstructions:
            failures.append("obstruction_count_above_declared_maximum")
        results.append({
            "segment_id": segment_id.strip(), "from_node": start, "to_node": end,
            "missing_measurements": missing, "criteria_failures": failures,
            "status": "criteria_not_met" if failures else "measurements_incomplete" if missing else "within_declared_screening_limits",
        })

    any_failure = any(item["criteria_failures"] for item in results)
    any_missing = any(item["missing_measurements"] for item in results)
    status = (
        "route_disconnected" if continuity_gaps else
        "declared_criteria_not_met" if any_failure else
        "incomplete_measurements" if any_missing else
        "within_declared_screening_limits"
    )
    return {
        "status": status, "segments": results,
        "continuity_gaps": continuity_gaps,
        "criteria": {
            "minimum_clear_width_m": min_width,
            "maximum_slope_percent": max_slope,
            "allowed_surfaces": sorted(surfaces),
            "maximum_obstructions": maximum_obstructions,
        },
        "route_generated": False,
        "responder_dispatch_performed": False,
        "operational_accessibility_certified": False,
        "real_world_safety_established": False,
    }

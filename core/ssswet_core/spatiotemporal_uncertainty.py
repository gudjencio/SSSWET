"""Propagate declared GPS and timestamp uncertainty for recorded observations."""
from __future__ import annotations

from datetime import datetime, timezone
from math import atan2, cos, isfinite, radians, sin, sqrt

EARTH_RADIUS_M = 6_371_008.8
MAX_OBSERVATIONS = 5_000
MAX_LOCATION_UNCERTAINTY_M = 100_000
MAX_TIME_UNCERTAINTY_SECONDS = 86_400


def _number(value, field, maximum):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(float(value)) or not 0 <= value <= maximum:
        raise ValueError(f"{field} must be a finite number between 0 and {maximum}")
    return float(value)


def _timestamp(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("timestamp must be a timezone-aware ISO timestamp")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("timestamp must be a timezone-aware ISO timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamp must include a timezone")
    return parsed.astimezone(timezone.utc)


def _observation(item):
    if not isinstance(item, dict):
        raise ValueError("each observation must be an object")
    latitude = item.get("latitude")
    longitude = item.get("longitude")
    for value, field, lower, upper in (
        (latitude, "latitude", -90, 90),
        (longitude, "longitude", -180, 180),
    ):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(float(value)) or not lower <= value <= upper:
            raise ValueError(f"{field} is outside its valid range")
    return {
        "event_id": str(item.get("event_id", "")),
        "session_id": str(item.get("session_id", "")),
        "source_id": str(item.get("source_id", "")),
        "timestamp": _timestamp(item.get("timestamp")),
        "time_uncertainty_seconds": _number(item.get("time_uncertainty_seconds", 0), "time_uncertainty_seconds", MAX_TIME_UNCERTAINTY_SECONDS),
        "latitude": float(latitude),
        "longitude": float(longitude),
        "location_accuracy_m": _number(item.get("location_accuracy_m", 0), "location_accuracy_m", MAX_LOCATION_UNCERTAINTY_M),
    }


def _distance(a, b):
    lat1, lat2 = radians(a["latitude"]), radians(b["latitude"])
    delta_lat = radians(b["latitude"] - a["latitude"])
    delta_lon = radians(((b["longitude"] - a["longitude"] + 540) % 360) - 180)
    h = sin(delta_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
    return 2 * EARTH_RADIUS_M * atan2(sqrt(min(1.0, h)), sqrt(max(0.0, 1.0 - h)))


def compare_observations(first: dict, second: dict) -> dict:
    a, b = _observation(first), _observation(second)
    if a["session_id"] != b["session_id"]:
        return {"status": "different_recording_session", "comparison_performed": False, "event_identity_established": False}
    center_seconds = (b["timestamp"] - a["timestamp"]).total_seconds()
    elapsed_lower = center_seconds - a["time_uncertainty_seconds"] - b["time_uncertainty_seconds"]
    elapsed_upper = center_seconds + a["time_uncertainty_seconds"] + b["time_uncertainty_seconds"]
    center_distance = _distance(a, b)
    distance_lower = max(0.0, center_distance - a["location_accuracy_m"] - b["location_accuracy_m"])
    distance_upper = center_distance + a["location_accuracy_m"] + b["location_accuracy_m"]
    if elapsed_upper <= 0:
        status, speed_lower, speed_upper = "time_order_reversed", None, None
    elif elapsed_lower <= 0:
        status = "time_intervals_overlap"
        speed_lower = distance_lower / elapsed_upper
        speed_upper = None
    else:
        status = "bounded"
        speed_lower = distance_lower / elapsed_upper
        speed_upper = distance_upper / elapsed_lower
    return {
        "status": status,
        "center_elapsed_seconds": center_seconds,
        "elapsed_interval_seconds": {"lower": elapsed_lower, "upper": elapsed_upper},
        "center_distance_m": center_distance,
        "distance_interval_m": {"lower": distance_lower, "upper": distance_upper},
        "speed_interval_mps": {"lower": speed_lower, "upper": speed_upper},
        "source_ids": sorted({a["source_id"], b["source_id"]}),
        "event_ids": [a["event_id"], b["event_id"]],
        "uncertainty_propagated": True,
        "event_identity_established": False,
        "extrapolation_performed": False,
        "scientific_validity_established": False,
    }


def analyze_segments(observations: list[dict]) -> dict:
    if not isinstance(observations, list) or len(observations) > MAX_OBSERVATIONS:
        raise ValueError(f"observations must be a list of at most {MAX_OBSERVATIONS}")
    results = [compare_observations(observations[index], observations[index + 1]) for index in range(len(observations) - 1)]
    return {
        "segments": results,
        "segment_count": len(results),
        "bounded_segment_count": sum(item.get("status") == "bounded" for item in results),
        "overlapping_time_interval_count": sum(item.get("status") == "time_intervals_overlap" for item in results),
        "unrecorded_history_recovered": False,
        "future_prediction_performed": False,
    }

"""Quality-gated GPS track segmentation and bounded interpolation for VTT.

Only observed points are evidence. Interpolated points are explicitly derived,
never extrapolated, and retain the endpoint observation references.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from math import acos, asin, atan2, cos, degrees, isfinite, radians, sin, sqrt
from typing import Iterable

MAX_OBSERVATIONS = 5000
EARTH_RADIUS_M = 6_371_008.8

def _timestamp(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("timestamp must be an ISO-8601 string with a timezone")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("timestamp must be a valid ISO-8601 value") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timezone-naive timestamps are not accepted")
    return parsed.astimezone(timezone.utc)

def _positive_finite(value, field):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a positive finite number")
    try:
        numeric = float(value)
    except (OverflowError, ValueError):
        raise ValueError(f"{field} must be a positive finite number") from None
    if not isfinite(numeric) or not 0 < numeric <= 1_000_000:
        raise ValueError(f"{field} must be a positive finite number")
    return numeric

@dataclass(frozen=True)
class SpatialObservation:
    observation_id: str
    latitude: float
    longitude: float
    timestamp: str
    accuracy_m: float
    source_ref: str

    def __post_init__(self):
        if not isinstance(self.observation_id, str) or not self.observation_id.strip():
            raise ValueError("observation_id is required")
        if not isinstance(self.source_ref, str) or not self.source_ref.strip():
            raise ValueError("source_ref is required")
        for value, field, low, high in ((self.latitude, "latitude", -90, 90), (self.longitude, "longitude", -180, 180)):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or not low <= value <= high:
                raise ValueError(f"{field} is outside its valid range")
        if isinstance(self.accuracy_m, bool) or not isinstance(self.accuracy_m, (int, float)) or not isfinite(self.accuracy_m) or not 0 <= self.accuracy_m <= 10000:
            raise ValueError("accuracy_m must be finite and between 0 and 10000")
        _timestamp(self.timestamp)

    def utc_datetime(self):
        return _timestamp(self.timestamp)

def haversine_m(a: SpatialObservation, b: SpatialObservation) -> float:
    lat1, lat2 = radians(a.latitude), radians(b.latitude)
    dlat = lat2 - lat1
    dlon = radians(((b.longitude - a.longitude + 180) % 360) - 180)
    value = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_M * asin(min(1.0, sqrt(value)))

def segment_track(observations: Iterable[SpatialObservation], *, max_gap_seconds: float = 900, max_accuracy_m: float = 150, max_jump_m: float = 5000, max_speed_mps: float = 70) -> dict:
    values = []
    try:
        for item in observations:
            if len(values) >= MAX_OBSERVATIONS:
                raise ValueError(f"at most {MAX_OBSERVATIONS} observations are supported")
            values.append(item)
    except TypeError as exc:
        raise ValueError("observations must be an iterable of SpatialObservation instances") from exc
    if any(not isinstance(item, SpatialObservation) for item in values):
        raise ValueError("all observations must be SpatialObservation instances")
    if len({item.observation_id for item in values}) != len(values):
        raise ValueError("observation IDs must be unique")
    max_gap_seconds = _positive_finite(max_gap_seconds, "max_gap_seconds")
    max_accuracy_m = _positive_finite(max_accuracy_m, "max_accuracy_m")
    max_jump_m = _positive_finite(max_jump_m, "max_jump_m")
    max_speed_mps = _positive_finite(max_speed_mps, "max_speed_mps")
    ordered = sorted(values, key=lambda item: (item.utc_datetime(), item.observation_id))
    accepted, rejected = [], []
    for item in ordered:
        if item.accuracy_m > max_accuracy_m:
            rejected.append({"observation_id": item.observation_id, "reason": "accuracy_exceeds_threshold"})
        else:
            accepted.append(item)
    segments, breaks, current = [], [], []
    for item in accepted:
        if not current:
            current = [item]
            continue
        previous = current[-1]
        elapsed = (item.utc_datetime() - previous.utc_datetime()).total_seconds()
        distance = haversine_m(previous, item)
        reason = None
        if elapsed <= 0:
            reason = "non_increasing_timestamp"
        elif elapsed > max_gap_seconds:
            reason = "time_gap_exceeds_threshold"
        elif distance > max_jump_m:
            reason = "distance_jump_exceeds_threshold"
        elif distance / elapsed > max_speed_mps:
            reason = "speed_exceeds_threshold"
        if reason:
            segments.append(current)
            breaks.append({"from_observation_id": previous.observation_id, "to_observation_id": item.observation_id,
                           "reason": reason, "elapsed_seconds": elapsed, "distance_m": round(distance, 3)})
            current = [item]
        else:
            current.append(item)
    if current:
        segments.append(current)
    return {
        "segments": [[asdict(item) for item in segment] for segment in segments],
        "breaks": breaks, "rejected": rejected, "input_count": len(values),
        "accepted_count": sum(len(segment) for segment in segments), "segment_count": len(segments),
        "thresholds": {"max_gap_seconds": max_gap_seconds, "max_accuracy_m": max_accuracy_m,
                       "max_jump_m": max_jump_m, "max_speed_mps": max_speed_mps},
        "observations_are_unchanged": True,
    }

def interpolate_between(left: SpatialObservation, right: SpatialObservation, timestamp: str, *, max_gap_seconds: float = 300) -> dict:
    if not isinstance(left, SpatialObservation) or not isinstance(right, SpatialObservation):
        raise ValueError("left and right must be SpatialObservation instances")
    max_gap_seconds = _positive_finite(max_gap_seconds, "max_gap_seconds")
    if left.observation_id == right.observation_id:
        raise ValueError("interpolation endpoints must be distinct observations")
    start, end, target = left.utc_datetime(), right.utc_datetime(), _timestamp(timestamp)
    gap = (end - start).total_seconds()
    if gap <= 0 or gap > max_gap_seconds:
        raise ValueError("endpoint interval is non-positive or exceeds max_gap_seconds")
    elapsed = (target - start).total_seconds()
    if not 0 < elapsed < gap:
        raise ValueError("interpolation time must be strictly between the two observations")
    fraction = elapsed / gap
    lat1, lon1, lat2, lon2 = map(radians, (left.latitude, left.longitude, right.latitude, right.longitude))
    vector_a = (cos(lat1) * cos(lon1), cos(lat1) * sin(lon1), sin(lat1))
    vector_b = (cos(lat2) * cos(lon2), cos(lat2) * sin(lon2), sin(lat2))
    dot = max(-1.0, min(1.0, sum(a * b for a, b in zip(vector_a, vector_b))))
    omega = acos(dot)
    if abs(omega) < 1e-12:
        vector = tuple((1 - fraction) * a + fraction * b for a, b in zip(vector_a, vector_b))
    elif abs(sin(omega)) < 1e-12:
        raise ValueError("antipodal endpoints do not define a unique short interpolation path")
    else:
        scale_a, scale_b = sin((1 - fraction) * omega) / sin(omega), sin(fraction * omega) / sin(omega)
        vector = tuple(scale_a * a + scale_b * b for a, b in zip(vector_a, vector_b))
    x, y, z = vector
    latitude = degrees(atan2(z, sqrt(x * x + y * y)))
    longitude = ((degrees(atan2(y, x)) + 540) % 360) - 180
    return {
        "latitude": latitude, "longitude": longitude, "timestamp_utc": target.isoformat(),
        "derived": True, "not_an_observation": True, "interpolation_fraction": round(fraction, 8),
        "endpoint_observation_ids": [left.observation_id, right.observation_id],
        "source_refs": [left.source_ref, right.source_ref],
        "endpoint_max_accuracy_m": max(left.accuracy_m, right.accuracy_m),
        "uncertainty_note": "Endpoint accuracy only; interpolation, clock and systematic errors are not fully modelled.",
        "extrapolation_performed": False,
    }

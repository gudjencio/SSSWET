"""Uncertainty-aware temporal evidence mapping.

This module aligns recorded timestamps and declared uncertainty windows. It
cannot recover unrecorded history, identify an event from overlap alone, or
predict the future.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from math import isfinite

MAX_OBSERVATIONS = 5000


@dataclass(frozen=True)
class TemporalObservation:
    timestamp: str
    label: str
    source_id: str
    uncertainty_seconds: float
    time_basis: str = "unspecified"
    observation_type: str = "recorded"
    location_accuracy_m: float | None = None


def _parse_timestamp(value: str):
    if not isinstance(value, str) or not value.strip():
        return None
    raw = value.strip()
    try:
        return datetime.fromisoformat(raw[:-1] + "+00:00" if raw.endswith("Z") else raw)
    except ValueError:
        return None


def _sort_key(observation: TemporalObservation):
    parsed = _parse_timestamp(observation.timestamp)
    if parsed is None:
        return (2, observation.timestamp)
    if parsed.tzinfo is not None:
        return (0, parsed.astimezone(timezone.utc).isoformat())
    return (1, parsed.isoformat())


class VirtualTimeMap:
    """Evidence map for recorded and explicitly uncertain temporal observations."""
    def __init__(self) -> None:
        self._observations: dict[tuple[str, str, str], TemporalObservation] = {}

    def add(self, observation: TemporalObservation) -> None:
        if not isinstance(observation, TemporalObservation):
            raise ValueError("observation must be a TemporalObservation")
        if not isinstance(observation.timestamp, str) or not observation.timestamp.strip():
            raise ValueError("timestamp is required")
        if not isinstance(observation.label, str) or not observation.label.strip():
            raise ValueError("label is required")
        if not isinstance(observation.source_id, str) or not observation.source_id.strip():
            raise ValueError("source_id is required")
        uncertainty = observation.uncertainty_seconds
        if isinstance(uncertainty, bool) or not isinstance(uncertainty, (int, float)) or not isfinite(float(uncertainty)) or uncertainty < 0:
            raise ValueError("uncertainty_seconds must be a finite non-negative number")
        accuracy = observation.location_accuracy_m
        if accuracy is not None and (isinstance(accuracy, bool) or not isinstance(accuracy, (int, float)) or not isfinite(float(accuracy)) or accuracy < 0):
            raise ValueError("location_accuracy_m must be a finite non-negative number or null")
        key = (observation.source_id.strip(), observation.timestamp.strip(), observation.label.strip())
        if key not in self._observations and len(self._observations) >= MAX_OBSERVATIONS:
            raise ValueError(f"temporal map is limited to {MAX_OBSERVATIONS} observations")
        self._observations[key] = observation

    def window(self, *, max_uncertainty_seconds: float | None = None) -> list[TemporalObservation]:
        if max_uncertainty_seconds is not None and (
            isinstance(max_uncertainty_seconds, bool) or not isinstance(max_uncertainty_seconds, (int, float))
            or not isfinite(float(max_uncertainty_seconds)) or max_uncertainty_seconds < 0
        ):
            raise ValueError("max_uncertainty_seconds must be finite and non-negative")
        values = list(self._observations.values())
        if max_uncertainty_seconds is not None:
            values = [item for item in values if item.uncertainty_seconds <= max_uncertainty_seconds]
        return sorted(values, key=_sort_key)

    def temporal_clusters(self, *, limit: int = 2000) -> dict:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= MAX_OBSERVATIONS:
            raise ValueError(f"limit must be between 1 and {MAX_OBSERVATIONS}")
        observations = self.window()
        truncated = len(observations) > limit
        observations = observations[:limit]
        buckets: dict[str, list[tuple[datetime, datetime, TemporalObservation]]] = {"aware": [], "naive": []}
        unparsed = []
        for item in observations:
            parsed = _parse_timestamp(item.timestamp)
            if parsed is None:
                unparsed.append(item)
                continue
            if parsed.tzinfo is None:
                center, bucket = parsed, "naive"
            else:
                center, bucket = parsed.astimezone(timezone.utc), "aware"
            delta = timedelta(seconds=float(item.uncertainty_seconds))
            buckets[bucket].append((center - delta, center + delta, item))
        clusters = []
        for bucket_name, intervals in buckets.items():
            intervals.sort(key=lambda row: (row[0], row[1], row[2].source_id, row[2].label))
            current = None
            for start, end, item in intervals:
                if current is None or start > datetime.fromisoformat(current["end"]):
                    if current is not None:
                        clusters.append(current)
                    current = {"time_basis": bucket_name, "start": start.isoformat(), "end": end.isoformat(), "observations": [asdict(item)]}
                else:
                    if end > datetime.fromisoformat(current["end"]):
                        current["end"] = end.isoformat()
                    current["observations"].append(asdict(item))
            if current is not None:
                clusters.append(current)
        clusters.sort(key=lambda item: (item["time_basis"], item["start"]))
        for cluster in clusters:
            cluster["source_ids"] = sorted({item["source_id"] for item in cluster["observations"]})
            cluster["possible_temporal_overlap"] = len(cluster["observations"]) > 1
            cluster["event_identity_established"] = False
        return {
            "clusters": clusters, "unparsed_observations": [asdict(item) for item in unparsed],
            "observation_count": len(observations), "unparsed_timestamp_count": len(unparsed),
            "truncated": truncated, "time_basis_groups_separated": True,
            "interpretation": "Overlapping uncertainty windows indicate possible temporal overlap, not proof of a shared event.",
            "unrecorded_history_recovered": False,
        }

    def export(self) -> list[dict]:
        return [asdict(item) for item in self.window()]

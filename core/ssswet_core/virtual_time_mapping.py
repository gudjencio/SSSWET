"""Evidence map for historical/temporal research with uncertainty-aware windows."""
from __future__ import annotations
import math
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone, timedelta

def _parse_timestamp(value: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("timestamp must be non-empty ISO-8601 text")
    raw = value.strip()
    if re.fullmatch(r"\d{4}", raw):
        parsed = datetime(int(raw), 1, 1, tzinfo=timezone.utc)
    else:
        try:
            parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("timestamp must be ISO-8601, a date, or a four-digit year") from exc
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)

@dataclass(frozen=True)
class TemporalObservation:
    timestamp: str
    label: str
    source_id: str
    uncertainty_seconds: float
    end_timestamp: str = ""

class VirtualTimeMap:
    """Temporal evidence mapping; it does not enable time travel or predict events."""
    def __init__(self) -> None:
        self._observations: dict[str, TemporalObservation] = {}

    def add(self, observation: TemporalObservation) -> None:
        if not isinstance(observation, TemporalObservation):
            raise TypeError("observation must be a TemporalObservation")
        if isinstance(observation.uncertainty_seconds, bool) or not isinstance(observation.uncertainty_seconds, (int, float)) or not math.isfinite(float(observation.uncertainty_seconds)):
            raise ValueError("uncertainty_seconds must be finite")
        if observation.uncertainty_seconds < 0:
            raise ValueError("uncertainty_seconds must be non-negative")
        if not isinstance(observation.source_id, str) or not observation.source_id.strip():
            raise ValueError("source_id is required")
        start = _parse_timestamp(observation.timestamp)
        if observation.end_timestamp:
            end = _parse_timestamp(observation.end_timestamp)
            if end < start:
                raise ValueError("end_timestamp must not precede timestamp")
        existing = self._observations.get(observation.source_id)
        if existing is not None and existing != observation:
            raise ValueError("source_id already exists; use a new identifier to preserve history")
        self._observations[observation.source_id] = observation

    def window(self, *, max_uncertainty_seconds: float | None = None) -> list[TemporalObservation]:
        if max_uncertainty_seconds is not None:
            if isinstance(max_uncertainty_seconds, bool) or not isinstance(max_uncertainty_seconds, (int, float)) or not math.isfinite(float(max_uncertainty_seconds)) or max_uncertainty_seconds < 0:
                raise ValueError("max_uncertainty_seconds must be finite and non-negative")
        values = list(self._observations.values())
        if max_uncertainty_seconds is not None:
            values = [value for value in values if value.uncertainty_seconds <= max_uncertainty_seconds]
        return sorted(values, key=lambda value: _parse_timestamp(value.timestamp))

    def window_between(self, start: str, end: str, *, include_uncertainty: bool = True,
                       max_uncertainty_seconds: float | None = None) -> list[TemporalObservation]:
        """Return observations whose declared or uncertainty-expanded intervals overlap."""
        lower, upper = _parse_timestamp(start), _parse_timestamp(end)
        if upper < lower:
            raise ValueError("end must not precede start")
        candidates = self.window(max_uncertainty_seconds=max_uncertainty_seconds)
        result = []
        for observation in candidates:
            observed_start = _parse_timestamp(observation.timestamp)
            observed_end = _parse_timestamp(observation.end_timestamp) if observation.end_timestamp else observed_start
            if include_uncertainty:
                margin = timedelta(seconds=float(observation.uncertainty_seconds))
                observed_start -= margin
                observed_end += margin
            if observed_start <= upper and observed_end >= lower:
                result.append(observation)
        return result

    def export(self) -> list[dict]:
        return [asdict(observation) for observation in self.window()]

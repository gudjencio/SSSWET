from dataclasses import dataclass


@dataclass(frozen=True)
class TemporalObservation:
    timestamp: str
    label: str
    source_id: str
    uncertainty_seconds: float


class VirtualTimeMap:
    """Evidence map for historical/temporal research; it does not enable time travel."""
    def __init__(self) -> None:
        self._observations: dict[str, TemporalObservation] = {}

    def add(self, observation: TemporalObservation) -> None:
        if observation.uncertainty_seconds < 0:
            raise ValueError("uncertainty_seconds must be non-negative")
        if not observation.source_id.strip():
            raise ValueError("source_id is required")
        self._observations[observation.source_id] = observation

    def window(self, *, max_uncertainty_seconds: float | None = None) -> list[TemporalObservation]:
        values = list(self._observations.values())
        if max_uncertainty_seconds is not None:
            values = [v for v in values if v.uncertainty_seconds <= max_uncertainty_seconds]
        return sorted(values, key=lambda v: v.timestamp)

    def export(self) -> list[dict]:
        return [o.__dict__.copy() for o in self.window()]

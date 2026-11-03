"""Quality indicators for recorded observations, without inventing missing data."""
from __future__ import annotations


def assess(observation: dict) -> dict:
    required = ("source_id", "timestamp", "value")
    missing = [field for field in required if observation.get(field) in (None, "")]
    score = (len(required) - len(missing)) / len(required)
    return {"score": score, "missing": missing, "complete": not missing}

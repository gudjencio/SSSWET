"""Confidence labels for recorded Virtual Time Mapping observations only."""
from __future__ import annotations


def assess(observations: list[dict]) -> dict:
    count = len(observations)
    complete = sum(1 for item in observations if item.get("source_id") and item.get("timestamp"))
    ratio = complete / count if count else 0.0
    label = "high" if ratio >= 0.9 and count >= 10 else "medium" if ratio >= 0.6 and count >= 3 else "low"
    return {"label": label, "observation_count": count, "complete_ratio": ratio, "unrecorded_history_recovered": False}

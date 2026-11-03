"""Conservative confidence labels for recorded Virtual Time observations only."""
from __future__ import annotations


def assess(observations: list[dict]) -> dict:
    if not isinstance(observations, list):
        raise ValueError("observations must be a list")
    if len(observations) > 100_000:
        raise ValueError("observations exceeds the 100000-record limit")
    count = len(observations)
    complete = sum(1 for item in observations if isinstance(item, dict) and isinstance(item.get("source_id"), str) and item["source_id"].strip() and item.get("timestamp") not in (None, ""))
    ratio = complete / count if count else 0.0
    label = "high" if ratio >= 0.95 and count >= 20 else "medium" if ratio >= 0.6 and count >= 3 else "low"
    return {"label": label, "observation_count": count, "complete_count": complete, "complete_ratio": ratio, "unrecorded_history_recovered": False}

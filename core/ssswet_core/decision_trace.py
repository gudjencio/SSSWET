"""Append-only-friendly decision trace normalization."""
from __future__ import annotations


def normalize(events: list[dict], *, max_events: int = 10000) -> list[dict]:
    if max_events <= 0:
        raise ValueError("max_events must be positive")
    cleaned = []
    for index, event in enumerate(events[:max_events]):
        if not event.get("type") or "decision" not in event:
            raise ValueError("each event needs type and decision")
        cleaned.append({"sequence": index, "type": str(event["type"]), "decision": str(event["decision"]), "reason": str(event.get("reason", ""))})
    return cleaned

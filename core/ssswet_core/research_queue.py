"""Evidence-aware research follow-up queue with deterministic priorities."""
from __future__ import annotations


def prioritize(items: list[dict]) -> list[dict]:
    output = []
    for item in items:
        missing = int(item.get("missing_evidence", 0))
        contradictions = int(item.get("contradictions", 0))
        stale_review = bool(item.get("review_due", False))
        safety_gate = bool(item.get("safety_gate", False))
        priority = min(100, 10 + 8 * missing + 12 * contradictions + (15 if stale_review else 0) + (20 if safety_gate else 0))
        output.append({**item, "priority": priority, "priority_reason": {"missing_evidence": missing, "contradictions": contradictions, "review_due": stale_review, "safety_gate": safety_gate}})
    return sorted(output, key=lambda x: (-x["priority"], str(x.get("id", ""))))

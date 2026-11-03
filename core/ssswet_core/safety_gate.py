"""Explicit human-review gates for higher-risk research actions."""
from __future__ import annotations

BLOCKING = {"human_subjects", "medical_decision", "hazardous_experiment", "privacy_sensitive", "cybersecurity_sensitive"}


def assess(flags: list[str], human_approval: bool = False) -> dict:
    normalized = sorted(set(flags))
    blocking = [flag for flag in normalized if flag in BLOCKING]
    allowed = not blocking or human_approval
    return {"allowed_to_proceed": allowed, "blocking_flags": blocking, "human_approval_required": bool(blocking), "human_approval_recorded": bool(human_approval), "automated_decision": False}

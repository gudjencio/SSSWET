"""Structured failure-mode review without a misleading composite risk score."""
from __future__ import annotations

MAX_FAILURE_MODES = 500
_LEVELS = {1, 2, 3, 4, 5}
_ACTION_STATES = {"open", "in_progress", "closed"}


def assess_failure_modes(modes: list[dict]) -> dict:
    if not isinstance(modes, list) or len(modes) > MAX_FAILURE_MODES:
        raise ValueError(f"modes must be a list of at most {MAX_FAILURE_MODES} entries")
    identifiers, reviewed = set(), []
    for mode in modes:
        if not isinstance(mode, dict):
            raise ValueError("each failure mode must be an object")
        mode_id = mode.get("mode_id")
        if not isinstance(mode_id, str) or not mode_id.strip() or mode_id in identifiers:
            raise ValueError("mode_id values must be unique non-empty strings")
        identifiers.add(mode_id)
        required = ("subsystem", "failure_mode", "effect", "cause")
        if any(not isinstance(mode.get(key), str) or not mode[key].strip() for key in required):
            raise ValueError("subsystem, failure_mode, effect and cause are required")
        for key in ("severity", "occurrence", "detectability"):
            if type(mode.get(key)) is not int or mode[key] not in _LEVELS:
                raise ValueError(f"{key} must be an integer from 1 to 5")
        controls = mode.get("controls", [])
        evidence = mode.get("evidence_refs", [])
        closure = mode.get("closure_evidence_refs", [])
        if any(not isinstance(value, list) or len(value) > 50 or any(not isinstance(item, str) or not item.strip() for item in value) for value in (controls, evidence, closure)):
            raise ValueError("controls and evidence reference fields must be bounded lists of non-empty strings")
        action_state = mode.get("action_state", "open")
        if action_state not in _ACTION_STATES:
            raise ValueError("action_state must be open, in_progress or closed")
        reviewer = mode.get("reviewer")
        if reviewer is not None and (not isinstance(reviewer, str) or len(reviewer) > 200):
            raise ValueError("reviewer must be a string of at most 200 characters")
        if action_state == "closed" and (not reviewer or not closure):
            raise ValueError("closed actions require a reviewer and closure evidence references")
        reasons = []
        if mode["severity"] >= 4 and not controls:
            reasons.append("high_severity_without_declared_controls")
        if not evidence:
            reasons.append("evidence_references_missing")
        if action_state != "closed":
            reasons.append("action_not_closed")
        reviewed.append({
            "mode_id": mode_id,
            "severity": mode["severity"],
            "occurrence": mode["occurrence"],
            "detectability": mode["detectability"],
            "action_state": action_state,
            "reviewer": reviewer,
            "review_reasons": reasons,
            "requires_human_attention": bool(reasons),
            "composite_risk_priority_number": None,
        })
    return {
        "mode_count": len(reviewed),
        "requires_human_attention_count": sum(item["requires_human_attention"] for item in reviewed),
        "results": reviewed,
        "single_composite_risk_score_used": False,
        "safety_certification_or_authorization_granted": False,
    }

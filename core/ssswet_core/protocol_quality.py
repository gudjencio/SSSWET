"""Structured preregistration completeness review without scientific approval."""
from __future__ import annotations
import json

MAX_PROTOCOL_CHARS = 100_000
CRITERIA = (
    "research_question", "hypotheses", "primary_outcome", "method", "analysis_plan",
    "sample_size_rationale", "inclusion_criteria", "exclusion_criteria", "stopping_rule",
    "missing_data_plan", "safety_review_reference", "deviations_policy", "randomization", "blinding",
)
_OPTIONAL_DESIGN_FIELDS = {"randomization", "blinding"}

def assess_protocol_quality(protocol: dict) -> dict:
    if not isinstance(protocol, dict) or len(protocol) > 100:
        raise ValueError("protocol must be an object with at most 100 fields")
    if any(not isinstance(key, str) for key in protocol):
        raise ValueError("protocol keys must be strings")
    try:
        encoded = json.dumps(protocol, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError("protocol must contain finite JSON-compatible values") from exc
    if len(encoded) > MAX_PROTOCOL_CHARS:
        raise ValueError("protocol exceeds 100000 characters")
    checks, blockers = [], []
    for field in CRITERIA:
        value = protocol.get(field)
        if isinstance(value, str) and value.strip():
            checks.append({"criterion": field, "state": "documented"})
        elif isinstance(value, dict) and value.get("status") == "not_applicable" and isinstance(value.get("reason"), str) and value["reason"].strip():
            checks.append({"criterion": field, "state": "not_applicable_with_reason"})
            if field not in _OPTIONAL_DESIGN_FIELDS:
                blockers.append(field)
        else:
            checks.append({"criterion": field, "state": "missing_or_insufficient"})
            blockers.append(field)
    documented = sum(item["state"] == "documented" or
                     (item["state"] == "not_applicable_with_reason" and item["criterion"] in _OPTIONAL_DESIGN_FIELDS)
                     for item in checks)
    return {
        "criteria": checks, "criterion_count": len(CRITERIA), "documented_count": documented,
        "completeness_percent": round(100 * documented / len(CRITERIA), 1),
        "review_blockers": blockers, "structurally_ready_for_independent_review": not blockers,
        "randomization_and_blinding_may_be_not_applicable_only_with_reason": True,
        "scientific_validity_established": False, "ethics_or_safety_approval_granted": False,
        "protocol_modified": False,
    }

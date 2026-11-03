"""Canonical, fingerprinted experiment-plan snapshots for prospective transparency."""
from __future__ import annotations
import hashlib
import json
REQUIRED = ("research_question", "hypotheses", "primary_outcome", "method", "analysis_plan", "stopping_rule")

def freeze(plan: dict) -> dict:
    if not isinstance(plan, dict):
        raise ValueError("plan must be a dictionary")
    if len(plan) > 100 or any(not isinstance(k, str) for k in plan):
        raise ValueError("plan must contain at most 100 string-keyed fields")
    missing = [field for field in REQUIRED if not isinstance(plan.get(field), str) or not plan[field].strip()]
    if missing:
        return {"complete": False, "missing_fields": missing, "fingerprint": None, "snapshot": None}
    try:
        canonical = json.dumps(plan, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError("plan must contain JSON-compatible finite values") from exc
    snapshot = json.loads(canonical)
    return {"complete": True, "missing_fields": [], "fingerprint": hashlib.sha256(canonical.encode("utf-8")).hexdigest(), "snapshot": snapshot, "immutable_by_this_function": True, "scientific_validity_established": False}

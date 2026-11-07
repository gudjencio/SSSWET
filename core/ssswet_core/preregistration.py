"""Canonical experiment-plan snapshots and explicit deviation records."""
from __future__ import annotations
import hashlib
import json

REQUIRED = ("research_question", "hypotheses", "primary_outcome", "method", "analysis_plan", "stopping_rule")
MAX_PLAN_CHARS = 100000


def _canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def freeze(plan: dict) -> dict:
    if not isinstance(plan, dict):
        raise ValueError("plan must be a dictionary")
    if len(plan) > 100 or any(not isinstance(key, str) for key in plan):
        raise ValueError("plan must contain at most 100 string-keyed fields")
    missing = [field for field in REQUIRED if not isinstance(plan.get(field), str) or not plan[field].strip()]
    if missing:
        return {"complete": False, "missing_fields": missing, "fingerprint": None, "snapshot": None}
    try:
        canonical = _canonical(plan)
    except (TypeError, ValueError) as exc:
        raise ValueError("plan must contain JSON-compatible finite values") from exc
    if len(canonical) > MAX_PLAN_CHARS:
        raise ValueError(f"plan exceeds {MAX_PLAN_CHARS} characters")
    snapshot = json.loads(canonical)
    return {
        "complete": True, "missing_fields": [],
        "fingerprint": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        "snapshot": snapshot, "immutable_by_this_function": True,
        "scientific_validity_established": False,
    }


def verify_frozen(frozen: dict) -> dict:
    if not isinstance(frozen, dict) or frozen.get("complete") is not True:
        raise ValueError("a complete frozen registration is required")
    snapshot = frozen.get("snapshot")
    if not isinstance(snapshot, dict):
        raise ValueError("frozen snapshot is missing")
    try:
        expected = hashlib.sha256(_canonical(snapshot).encode("utf-8")).hexdigest()
    except (TypeError, ValueError) as exc:
        raise ValueError("frozen snapshot must contain JSON-compatible finite values") from exc
    actual = frozen.get("fingerprint")
    return {"valid": isinstance(actual, str) and actual == expected,
            "expected_fingerprint": expected, "recorded_fingerprint": actual,
            "original_snapshot_preserved": True}


def _flatten(value: object, prefix: str = "") -> dict[str, object]:
    result: dict[str, object] = {}
    if isinstance(value, dict):
        if not value and prefix:
            result[prefix] = {}
        for key in sorted(value):
            path = f"{prefix}.{key}" if prefix else str(key)
            result.update(_flatten(value[key], path))
    elif isinstance(value, list):
        if not value and prefix:
            result[prefix] = []
        for index, item in enumerate(value):
            result.update(_flatten(item, f"{prefix}[{index}]"))
    else:
        result[prefix] = value
    return result


def compare_frozen(frozen: dict, candidate: dict) -> dict:
    integrity = verify_frozen(frozen)
    if not integrity["valid"]:
        raise ValueError("frozen registration fingerprint does not verify")
    if not isinstance(candidate, dict):
        raise ValueError("candidate plan must be a dictionary")
    try:
        canonical = _canonical(candidate)
    except (TypeError, ValueError) as exc:
        raise ValueError("candidate plan must contain JSON-compatible finite values") from exc
    if len(canonical) > MAX_PLAN_CHARS:
        raise ValueError(f"candidate plan exceeds {MAX_PLAN_CHARS} characters")
    candidate_snapshot = json.loads(canonical)
    before, after = _flatten(frozen["snapshot"]), _flatten(candidate_snapshot)
    paths = sorted(set(before) | set(after))
    changes = [
        {"path": path, "before": before.get(path), "after": after.get(path)}
        for path in paths if before.get(path) != after.get(path) or (path in before) != (path in after)
    ]
    return {
        "base_fingerprint": frozen["fingerprint"],
        "candidate_fingerprint": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        "changed_field_count": len(changes), "changes": changes,
        "original_snapshot_modified": False,
    }


def record_deviation(frozen: dict, revised_plan: dict, *, reason: str, reviewer_id: str) -> dict:
    if not isinstance(reason, str) or not reason.strip() or len(reason.strip()) > 2000:
        raise ValueError("reason must contain 1 to 2000 characters")
    if not isinstance(reviewer_id, str) or not reviewer_id.strip() or len(reviewer_id.strip()) > 120:
        raise ValueError("reviewer_id must contain 1 to 120 characters")
    comparison = compare_frozen(frozen, revised_plan)
    if comparison["changed_field_count"] == 0:
        raise ValueError("a deviation requires at least one changed field")
    payload = {
        **comparison, "reason": reason.strip(), "reviewer_id": reviewer_id.strip(),
        "state": "recorded_pending_review", "approval_granted": False,
        "original_snapshot_preserved": True, "scientific_validity_established": False,
    }
    payload["deviation_id"] = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()
    return payload

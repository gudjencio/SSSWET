"""Canonical experiment-plan snapshots and auditable prospective amendments."""
from __future__ import annotations

import hashlib
import json


REQUIRED = ("research_question", "hypotheses", "primary_outcome", "method", "analysis_plan", "stopping_rule")


def _canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def freeze(plan: dict) -> dict:
    if not isinstance(plan, dict):
        raise ValueError("plan must be a dictionary")
    if len(plan) > 100 or any(not isinstance(k, str) for k in plan):
        raise ValueError("plan must contain at most 100 string-keyed fields")
    missing = [field for field in REQUIRED if not isinstance(plan.get(field), str) or not plan[field].strip()]
    if missing:
        return {"complete": False, "missing_fields": missing, "fingerprint": None, "snapshot": None}
    try:
        canonical = _canonical(plan)
    except (TypeError, ValueError) as exc:
        raise ValueError("plan must contain JSON-compatible finite values") from exc
    snapshot = json.loads(canonical)
    return {"complete": True, "missing_fields": [], "fingerprint": hashlib.sha256(canonical.encode("utf-8")).hexdigest(), "snapshot": snapshot, "immutable_by_this_function": True, "scientific_validity_established": False}


def verify_snapshot(frozen: dict) -> dict:
    if not isinstance(frozen, dict) or frozen.get("complete") is not True:
        return {"valid": False, "reason": "incomplete_snapshot"}
    snapshot = frozen.get("snapshot")
    fingerprint = frozen.get("fingerprint")
    if not isinstance(snapshot, dict) or not isinstance(fingerprint, str):
        return {"valid": False, "reason": "missing_snapshot_or_fingerprint"}
    try:
        actual = hashlib.sha256(_canonical(snapshot).encode("utf-8")).hexdigest()
    except (TypeError, ValueError):
        return {"valid": False, "reason": "non_canonical_snapshot"}
    return {"valid": actual == fingerprint, "expected_fingerprint": fingerprint,
            "actual_fingerprint": actual, "reason": "" if actual == fingerprint else "fingerprint_mismatch"}


def _changes(before: object, after: object, path: str = "") -> list[str]:
    if isinstance(before, dict) and isinstance(after, dict):
        changes = []
        for key in sorted(set(before) | set(after)):
            child = path + "/" + str(key).replace("~", "~0").replace("/", "~1")
            if key not in before or key not in after:
                changes.append(child)
            else:
                changes.extend(_changes(before[key], after[key], child))
        return changes
    if isinstance(before, list) and isinstance(after, list):
        if before == after:
            return []
        return [path or "/"]
    return [] if before == after else [path or "/"]


def amend(previous: dict, revised_plan: dict, *, reason: str, actor: str,
          evidence_refs: list[str] | tuple[str, ...] = ()) -> dict:
    """Create a new snapshot and a transparent diff; never rewrites the prior plan."""
    integrity = verify_snapshot(previous)
    if not integrity["valid"]:
        raise ValueError("previous preregistration snapshot failed integrity verification")
    if not isinstance(reason, str) or not reason.strip() or len(reason.strip()) > 2000:
        raise ValueError("amendment reason must contain 1 to 2000 characters")
    if not isinstance(actor, str) or not actor.strip() or len(actor.strip()) > 120:
        raise ValueError("amendment actor must contain 1 to 120 characters")
    if not isinstance(evidence_refs, (list, tuple)):
        raise ValueError("evidence_refs must be a list or tuple")
    refs = []
    for ref in evidence_refs:
        if not isinstance(ref, str) or not ref.strip() or len(ref.strip()) > 500:
            raise ValueError("each evidence reference must contain 1 to 500 characters")
        if ref.strip() not in refs:
            refs.append(ref.strip())
    updated = freeze(revised_plan)
    if not updated["complete"]:
        raise ValueError("revised plan is incomplete: " + ", ".join(updated["missing_fields"]))
    changed_paths = _changes(previous["snapshot"], updated["snapshot"])
    if not changed_paths:
        raise ValueError("amendment must change at least one plan field")
    return {
        "previous_fingerprint": previous["fingerprint"],
        "new_fingerprint": updated["fingerprint"],
        "changed_paths": changed_paths,
        "change_count": len(changed_paths),
        "reason": reason.strip(),
        "actor": actor.strip(),
        "evidence_refs": refs,
        "previous_snapshot_preserved": True,
        "amendment_is_prospective_record": True,
        "scientific_validity_established": False,
        "snapshot": updated["snapshot"],
    }

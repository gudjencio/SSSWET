"""Tamper-evident, bounded research checkpoints for safe continuity."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone

MAX_BUNDLE_BYTES = 65_536
MAX_REFERENCES = 1_000
_HEX = re.compile(r"^[0-9a-f]{64}$")


def _canonical(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _clean(value, field, maximum=500):
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > maximum:
        raise ValueError(f"{field} must contain 1 to {maximum} characters")
    return value.strip()


def _digest(value, field):
    if not isinstance(value, str) or not _HEX.fullmatch(value):
        raise ValueError(f"{field} must be a 64-character lowercase SHA-256 digest")
    return value


def _unique_ids(values, field):
    if not isinstance(values, list) or len(values) > MAX_REFERENCES:
        raise ValueError(f"{field} must be a list of at most {MAX_REFERENCES} identifiers")
    result = [_clean(value, field, 240) for value in values]
    if len(result) != len(set(result)):
        raise ValueError(f"{field} must not contain duplicates")
    return sorted(result)


def build_checkpoint_bundle(
    *, task_id: str, objective: str, query_plan_sha256: str, context_sha256: str,
    memory_versions: dict, source_fingerprints: dict, decision_ids: list,
    unresolved_questions: list, review_blockers: list, budgets: dict,
    created_at: str | None = None,
) -> dict:
    task_id = _clean(task_id, "task_id", 160)
    objective = _clean(objective, "objective", 2_000)
    query_hash = _digest(query_plan_sha256, "query_plan_sha256")
    context_hash = _digest(context_sha256, "context_sha256")
    if not isinstance(memory_versions, dict) or len(memory_versions) > MAX_REFERENCES:
        raise ValueError("memory_versions must be an object of at most 1000 entries")
    normalized_memory = {}
    for key, version in memory_versions.items():
        key = _clean(key, "memory version key", 240)
        if isinstance(version, bool) or not isinstance(version, int) or version < 1:
            raise ValueError("memory versions must be positive integers")
        normalized_memory[key] = version
    if not isinstance(source_fingerprints, dict) or len(source_fingerprints) > MAX_REFERENCES:
        raise ValueError("source_fingerprints must be an object of at most 1000 entries")
    normalized_sources = {
        _clean(key, "source fingerprint key", 240): _digest(value, "source fingerprint")
        for key, value in source_fingerprints.items()
    }
    if not isinstance(budgets, dict):
        raise ValueError("budgets must be an object")
    max_steps = budgets.get("max_steps")
    max_runtime = budgets.get("max_runtime_seconds")
    if isinstance(max_steps, bool) or not isinstance(max_steps, int) or not 1 <= max_steps <= 1_000_000:
        raise ValueError("budgets.max_steps must be between 1 and 1000000")
    if isinstance(max_runtime, bool) or not isinstance(max_runtime, int) or not 1 <= max_runtime <= 604_800:
        raise ValueError("budgets.max_runtime_seconds must be between 1 and 604800")
    if created_at is None:
        created_at = datetime.now(timezone.utc).isoformat()
    else:
        created_at = _clean(created_at, "created_at", 80)
        try:
            parsed = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("created_at must be a timezone-aware ISO timestamp") from exc
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("created_at must include a timezone")
        created_at = parsed.astimezone(timezone.utc).isoformat()
    payload = {
        "schema_version": 1,
        "task_id": task_id,
        "objective": objective,
        "query_plan_sha256": query_hash,
        "context_sha256": context_hash,
        "memory_versions": dict(sorted(normalized_memory.items())),
        "source_fingerprints": dict(sorted(normalized_sources.items())),
        "decision_ids": _unique_ids(decision_ids, "decision_ids"),
        "unresolved_questions": [_clean(item, "unresolved question", 1_000) for item in unresolved_questions],
        "review_blockers": [_clean(item, "review blocker", 500) for item in review_blockers],
        "budgets": {"max_steps": max_steps, "max_runtime_seconds": max_runtime},
        "created_at": created_at,
        "resume_requires_freshness_check": True,
        "automatic_execution": False,
    }
    if len(_canonical(payload).encode("utf-8")) > MAX_BUNDLE_BYTES:
        raise ValueError(f"checkpoint bundle exceeds {MAX_BUNDLE_BYTES} bytes")
    return {**payload, "bundle_sha256": hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()}


def verify_checkpoint_bundle(bundle: dict) -> dict:
    if not isinstance(bundle, dict):
        return {"valid": False, "reason": "bundle_must_be_an_object"}
    recorded = bundle.get("bundle_sha256")
    payload = {key: value for key, value in bundle.items() if key != "bundle_sha256"}
    try:
        encoded = _canonical(payload).encode("utf-8")
        structurally_valid = (
            payload.get("schema_version") == 1
            and isinstance(payload.get("memory_versions"), dict)
            and isinstance(payload.get("source_fingerprints"), dict)
            and isinstance(payload.get("decision_ids"), list)
            and isinstance(payload.get("review_blockers"), list)
            and len(encoded) <= MAX_BUNDLE_BYTES
        )
        expected = hashlib.sha256(encoded).hexdigest()
    except (TypeError, ValueError):
        structurally_valid, expected = False, None
    valid = bool(structurally_valid and isinstance(recorded, str) and recorded == expected)
    return {"valid": valid, "recorded_sha256": recorded, "expected_sha256": expected, "tampered_or_incomplete": not valid}


def assess_resume(bundle: dict, current_state: dict) -> dict:
    verification = verify_checkpoint_bundle(bundle)
    if not isinstance(current_state, dict):
        raise ValueError("current_state must be an object")
    if not verification["valid"]:
        return {"safe_to_resume": False, "blockers": ["checkpoint_integrity_failed"], "verification": verification, "automatic_execution": False}
    changed_memories = sorted(
        key for key, version in bundle["memory_versions"].items()
        if current_state.get("memory_versions", {}).get(key) != version
    )
    changed_sources = sorted(
        key for key, fingerprint in bundle["source_fingerprints"].items()
        if current_state.get("source_fingerprints", {}).get(key) != fingerprint
    )
    changed_plan = current_state.get("query_plan_sha256") != bundle["query_plan_sha256"]
    changed_context = current_state.get("context_sha256") != bundle["context_sha256"]
    blockers = sorted(set(bundle.get("review_blockers", [])) | set(current_state.get("review_blockers", [])))
    differences = []
    if changed_plan:
        differences.append("query_plan_changed")
    if changed_context:
        differences.append("research_context_changed")
    if changed_memories:
        differences.append("scientific_memory_versions_changed")
    if changed_sources:
        differences.append("source_fingerprints_changed")
    safe = not differences and not blockers
    return {
        "safe_to_resume": safe,
        "changed_query_plan": changed_plan,
        "changed_context": changed_context,
        "changed_memory_keys": changed_memories,
        "changed_source_ids": changed_sources,
        "review_blockers": blockers,
        "differences": differences,
        "automatic_execution": False,
        "human_review_required": not safe,
    }

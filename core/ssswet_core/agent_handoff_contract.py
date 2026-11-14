"""Versioned, bounded agent handoffs. A valid envelope never authorizes execution."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from .assurance_common import aware_datetime, digest, identifier, sha256_hex, text

SCHEMA_VERSION = 1
MAX_SOURCE_REFS = 100
MAX_CONSTRAINTS = 50
MAX_OUTPUTS = 20
MAX_ENVELOPE_BYTES = 250_000


def build_handoff(envelope: dict) -> dict:
    if not isinstance(envelope, dict):
        raise ValueError("handoff must be an object")
    required = {"handoff_id", "created_at", "expires_at", "from_agent", "to_agent", "objective", "constraints", "source_refs", "requested_outputs", "requires_human_review", "safety_state", "budget"}
    if set(envelope) - (required | {"schema_version", "handoff_sha256"}):
        raise ValueError("handoff contains unknown fields")
    missing = required - set(envelope)
    if missing:
        raise ValueError("handoff missing fields: " + ", ".join(sorted(missing)))
    if envelope.get("schema_version", SCHEMA_VERSION) != SCHEMA_VERSION:
        raise ValueError("unsupported handoff schema_version")
    handoff_id = identifier(envelope["handoff_id"], "handoff_id")
    created = aware_datetime(envelope["created_at"], "created_at")
    expires = aware_datetime(envelope["expires_at"], "expires_at")
    if expires <= created:
        raise ValueError("expires_at must be later than created_at")
    source_refs = envelope["source_refs"]
    if not isinstance(source_refs, list) or len(source_refs) > MAX_SOURCE_REFS:
        raise ValueError(f"source_refs must contain at most {MAX_SOURCE_REFS} items")
    normalized_refs = []
    seen = set()
    for ref in source_refs:
        if not isinstance(ref, dict) or set(ref) != {"source_id", "sha256", "source_type"}:
            raise ValueError("each source_ref must contain source_id, sha256 and source_type only")
        source_id = identifier(ref["source_id"], "source_ref.source_id")
        if source_id in seen:
            raise ValueError("source_ref source_id values must be unique")
        seen.add(source_id)
        normalized_refs.append({"source_id": source_id, "sha256": sha256_hex(ref["sha256"], "source_ref.sha256"), "source_type": text(ref["source_type"], "source_ref.source_type", 60)})
    constraints = envelope["constraints"]
    outputs = envelope["requested_outputs"]
    if not isinstance(constraints, list) or len(constraints) > MAX_CONSTRAINTS:
        raise ValueError(f"constraints must contain at most {MAX_CONSTRAINTS} items")
    if not isinstance(outputs, list) or not 1 <= len(outputs) <= MAX_OUTPUTS:
        raise ValueError(f"requested_outputs must contain 1 to {MAX_OUTPUTS} items")
    budget = envelope["budget"]
    if not isinstance(budget, dict) or set(budget) != {"max_steps", "max_runtime_seconds", "max_output_chars"}:
        raise ValueError("budget must contain max_steps, max_runtime_seconds and max_output_chars")
    for key, maximum in (("max_steps", 1000), ("max_runtime_seconds", 3600), ("max_output_chars", 200000)):
        value = budget[key]
        if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= maximum:
            raise ValueError(f"budget.{key} must be between 1 and {maximum}")
    if not isinstance(envelope["requires_human_review"], bool):
        raise ValueError("requires_human_review must be boolean")
    safety_state = envelope["safety_state"]
    if safety_state not in {"not_assessed", "review_required", "reviewed_not_authorized", "blocked"}:
        raise ValueError("safety_state must be an explicit non-authorizing state")
    normalized = {
        "schema_version": SCHEMA_VERSION,
        "handoff_id": handoff_id,
        "created_at": created.isoformat(),
        "expires_at": expires.isoformat(),
        "from_agent": identifier(envelope["from_agent"], "from_agent"),
        "to_agent": identifier(envelope["to_agent"], "to_agent"),
        "objective": text(envelope["objective"], "objective", 5000),
        "constraints": [text(item, "constraint", 1000) for item in constraints],
        "source_refs": sorted(normalized_refs, key=lambda item: item["source_id"]),
        "requested_outputs": [text(item, "requested_output", 500) for item in outputs],
        "requires_human_review": envelope["requires_human_review"],
        "safety_state": safety_state,
        "budget": dict(budget),
    }
    if len(json.dumps(normalized, ensure_ascii=False).encode("utf-8")) > MAX_ENVELOPE_BYTES:
        raise ValueError("handoff exceeds serialized size limit")
    normalized["handoff_sha256"] = digest(normalized)
    return normalized


def validate_handoff(envelope: dict, *, now: str | None = None) -> dict:
    supplied_hash = envelope.get("handoff_sha256") if isinstance(envelope, dict) else None
    normalized = build_handoff({key: value for key, value in envelope.items() if key != "handoff_sha256"})
    if supplied_hash is not None and sha256_hex(supplied_hash, "handoff_sha256") != normalized["handoff_sha256"]:
        raise ValueError("handoff digest mismatch")
    instant = aware_datetime(now, "now") if now is not None else datetime.now(timezone.utc)
    expired = instant > aware_datetime(normalized["expires_at"], "expires_at")
    return {
        "valid": True,
        "expired": expired,
        "handoff_id": normalized["handoff_id"],
        "handoff_sha256": normalized["handoff_sha256"],
        "source_ref_count": len(normalized["source_refs"]),
        "ready_for_human_review": not expired and normalized["safety_state"] != "blocked",
        "execution_authorized": False,
        "limitations": ["A valid handoff is a data contract, not permission to execute work.", "Safety, privacy, legal and human-review gates remain external and mandatory."],
    }

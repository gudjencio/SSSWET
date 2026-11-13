"""Hash-linked metadata receipts for reproducible agent execution traces."""
from __future__ import annotations

import hashlib
import json
import re

_HEX = re.compile(r"^[0-9a-f]{64}$")
HIGH_REVIEW_FLAGS = {"safety", "ethics", "human_subjects", "medical_decision", "privacy_sensitive", "cybersecurity_sensitive"}


def _clean(value, field, maximum=240):
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > maximum:
        raise ValueError(f"{field} must contain 1 to {maximum} characters")
    return value.strip()


def _digest(value, field):
    if not isinstance(value, str) or not _HEX.fullmatch(value):
        raise ValueError(f"{field} must be a 64-character lowercase SHA-256 digest")
    return value


def _canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def build_execution_receipt(
    *, receipt_id: str, task_id: str, contract_id: str, agent_id: str, role: str,
    provider: str, model_label: str, input_refs: list[dict], output_sha256: str,
    toolchain: list[dict], parent_receipt_ids: list[str], step_count: int,
    elapsed_ms: int, max_steps: int, max_runtime_ms: int, execution_status: str,
    risk_flags: list[str] | None = None, reviewer_id: str = "", created_at: str = "",
) -> dict:
    identifiers = {
        "receipt_id": _clean(receipt_id, "receipt_id"),
        "task_id": _clean(task_id, "task_id"),
        "contract_id": _clean(contract_id, "contract_id"),
        "agent_id": _clean(agent_id, "agent_id"),
        "role": _clean(role, "role", 80),
        "provider": _clean(provider, "provider", 120),
        "model_label": _clean(model_label, "model_label", 160),
    }
    if not isinstance(input_refs, list) or len(input_refs) > 100:
        raise ValueError("input_refs must be a list of at most 100 items")
    normalized_inputs = []
    for item in input_refs:
        if not isinstance(item, dict) or set(item) - {"ref_id", "sha256", "role"}:
            raise ValueError("input references may contain only ref_id, sha256 and role")
        normalized_inputs.append({
            "ref_id": _clean(item.get("ref_id"), "input ref_id"),
            "sha256": _digest(item.get("sha256"), "input ref sha256"),
            "role": _clean(item.get("role", "input"), "input role", 80),
        })
    if not isinstance(toolchain, list) or len(toolchain) > 50:
        raise ValueError("toolchain must be a list of at most 50 items")
    normalized_tools = []
    for item in toolchain:
        if not isinstance(item, dict) or set(item) != {"name", "version"}:
            raise ValueError("toolchain entries must contain only name and version")
        normalized_tools.append({"name": _clean(item["name"], "tool name", 120), "version": _clean(item["version"], "tool version", 80)})
    if not isinstance(parent_receipt_ids, list) or len(parent_receipt_ids) > 20:
        raise ValueError("parent_receipt_ids must be a list of at most 20 items")
    parents = sorted({_clean(item, "parent_receipt_id") for item in parent_receipt_ids})
    if len(parents) != len(parent_receipt_ids):
        raise ValueError("parent receipt IDs must be unique")
    for value, field, maximum in (
        (step_count, "step_count", 1_000_000),
        (max_steps, "max_steps", 1_000_000),
        (elapsed_ms, "elapsed_ms", 604_800_000),
        (max_runtime_ms, "max_runtime_ms", 604_800_000),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= maximum:
            raise ValueError(f"{field} must be a bounded non-negative integer")
    if max_steps < 1 or max_runtime_ms < 1:
        raise ValueError("execution budgets must be positive")
    if execution_status not in {"completed", "partial", "failed"}:
        raise ValueError("execution_status must be completed, partial or failed")
    flags = sorted(set(risk_flags or []))
    if any(not isinstance(item, str) or not item.strip() or len(item) > 80 for item in flags):
        raise ValueError("risk_flags must contain bounded non-empty strings")
    if created_at:
        created_at = _clean(created_at, "created_at", 80)
    payload = {
        "schema_version": 1,
        **identifiers,
        "input_refs": sorted(normalized_inputs, key=lambda item: (item["ref_id"], item["role"])),
        "output_sha256": _digest(output_sha256, "output_sha256"),
        "toolchain": sorted(normalized_tools, key=lambda item: (item["name"], item["version"])),
        "parent_receipt_ids": parents,
        "step_count": step_count,
        "elapsed_ms": elapsed_ms,
        "budgets": {"max_steps": max_steps, "max_runtime_ms": max_runtime_ms},
        "budget_compliant": step_count <= max_steps and elapsed_ms <= max_runtime_ms,
        "execution_status": execution_status,
        "risk_flags": flags,
        "reviewer_id": _clean(reviewer_id, "reviewer_id") if reviewer_id else "",
        "human_review_required": bool(set(flags) & HIGH_REVIEW_FLAGS) or execution_status != "completed",
        "raw_prompts_stored": False,
        "raw_outputs_stored": False,
        "secret_values_stored": False,
        "scientific_validity_established": False,
        "created_at": created_at,
    }
    receipt_hash = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()
    return {**payload, "receipt_sha256": receipt_hash}


def verify_execution_receipt(receipt: dict) -> dict:
    if not isinstance(receipt, dict):
        return {"valid": False, "reason": "receipt_must_be_an_object"}
    recorded = receipt.get("receipt_sha256")
    payload = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    try:
        expected = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()
    except (TypeError, ValueError):
        expected = None
    valid = isinstance(recorded, str) and recorded == expected and payload.get("schema_version") == 1
    return {"valid": valid, "recorded_sha256": recorded, "expected_sha256": expected}


def verify_execution_chain(receipts: list[dict]) -> dict:
    if not isinstance(receipts, list) or len(receipts) > 5_000:
        raise ValueError("receipts must be a list of at most 5000 items")
    by_id = {}
    invalid = []
    for receipt in receipts:
        if not isinstance(receipt, dict):
            invalid.append("non_object_receipt")
            continue
        identifier = receipt.get("receipt_id")
        if not isinstance(identifier, str) or not identifier:
            invalid.append("missing_receipt_id")
            continue
        if identifier in by_id:
            invalid.append("duplicate_receipt_id:" + identifier)
        by_id[identifier] = receipt
        if not verify_execution_receipt(receipt)["valid"]:
            invalid.append("invalid_digest:" + identifier)
    missing = sorted({
        parent for receipt in by_id.values()
        for parent in receipt.get("parent_receipt_ids", [])
        if parent not in by_id
    })
    visiting, visited = set(), set()
    cycle = False

    def visit(identifier):
        nonlocal cycle
        if identifier in visiting:
            cycle = True
            return
        if identifier in visited:
            return
        visiting.add(identifier)
        for parent in by_id[identifier].get("parent_receipt_ids", []):
            if parent in by_id:
                visit(parent)
        visiting.remove(identifier)
        visited.add(identifier)

    for identifier in sorted(by_id):
        visit(identifier)
    return {
        "receipt_count": len(by_id),
        "invalid_receipts": sorted(set(invalid)),
        "missing_parent_receipt_ids": missing,
        "cycle_detected": cycle,
        "valid": not invalid and not missing and not cycle,
        "execution_correctness_established": False,
        "agent_intelligence_increased": False,
    }

"""Machine-checkable, least-privilege contracts for research-agent assignments."""
from __future__ import annotations

import re

MAX_REFS = 500
MAX_FIELDS = 100


def _identifier(value, field):
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > 160:
        raise ValueError(f"{field} must contain 1 to 160 characters")
    return value.strip()


def _string_list(values, field, maximum=MAX_REFS):
    if not isinstance(values, list) or len(values) > maximum:
        raise ValueError(f"{field} must be a list of at most {maximum} values")
    cleaned = [_identifier(item, field) for item in values]
    if len(cleaned) != len(set(cleaned)):
        raise ValueError(f"{field} must not contain duplicates")
    return sorted(cleaned)


def build_task_contract(*, task_id: str, objective: str, creator_agent_id: str,
                        assigned_agent_id: str, reviewer_agent_id: str,
                        required_capabilities: list[str], declared_capabilities: list[str],
                        forbidden_capabilities: list[str] | None = None,
                        input_refs: list[str] | None = None,
                        allowed_source_ids: list[str] | None = None,
                        required_output_fields: list[str] | None = None,
                        max_steps: int = 100, max_runtime_seconds: int = 3600) -> dict:
    task_id = _identifier(task_id, "task_id")
    objective = _identifier(objective, "objective")
    creator = _identifier(creator_agent_id, "creator_agent_id")
    assigned = _identifier(assigned_agent_id, "assigned_agent_id")
    reviewer = _identifier(reviewer_agent_id, "reviewer_agent_id")
    if reviewer in {creator, assigned}:
        raise ValueError("reviewer must be distinct from creator and assigned agent")
    required = set(_string_list(required_capabilities, "required_capabilities", 100))
    declared = set(_string_list(declared_capabilities, "declared_capabilities", 100))
    forbidden = set(_string_list(forbidden_capabilities or [], "forbidden_capabilities", 100))
    if not required:
        raise ValueError("at least one required capability is needed")
    missing = sorted(required - declared)
    prohibited = sorted(declared & forbidden)
    if missing:
        raise ValueError("assigned agent lacks required capabilities: " + ", ".join(missing))
    if prohibited:
        raise ValueError("assigned agent declares forbidden capabilities: " + ", ".join(prohibited))
    if not isinstance(max_steps, int) or isinstance(max_steps, bool) or not 1 <= max_steps <= 10000:
        raise ValueError("max_steps must be between 1 and 10000")
    if not isinstance(max_runtime_seconds, int) or isinstance(max_runtime_seconds, bool) or not 1 <= max_runtime_seconds <= 86400:
        raise ValueError("max_runtime_seconds must be between 1 and 86400")
    fields = _string_list(required_output_fields or ["summary", "limitations", "evidence_refs"], "required_output_fields", MAX_FIELDS)
    if not fields:
        raise ValueError("at least one required output field is needed")
    return {
        "schema_version": 1, "task_id": task_id, "objective": objective,
        "creator_agent_id": creator, "assigned_agent_id": assigned,
        "reviewer_agent_id": reviewer, "required_capabilities": sorted(required),
        "declared_capabilities": sorted(declared), "forbidden_capabilities": sorted(forbidden),
        "input_refs": _string_list(input_refs or [], "input_refs"),
        "allowed_source_ids": _string_list(allowed_source_ids or [], "allowed_source_ids"),
        "required_output_fields": fields, "max_steps": max_steps,
        "max_runtime_seconds": max_runtime_seconds,
        "reviewer_must_be_independent_of_assignee": True,
        "automatic_execution": False, "automatic_approval": False,
        "scientific_validity_established": False,
    }


def validate_completion(contract: dict, completion: dict) -> dict:
    """Check a proposed result against its contract without accepting or executing it."""
    if not isinstance(contract, dict) or contract.get("schema_version") != 1:
        raise ValueError("a schema-version-1 task contract is required")
    if not isinstance(completion, dict):
        raise ValueError("completion must be an object")
    output = completion.get("output")
    if not isinstance(output, dict):
        output = {}
    required = contract.get("required_output_fields", [])
    missing = sorted(field for field in required if field not in output or output[field] in (None, "", [], {}))
    evidence_refs = completion.get("evidence_refs", [])
    if not isinstance(evidence_refs, list) or any(not isinstance(item, str) or not item.strip() for item in evidence_refs):
        raise ValueError("evidence_refs must be a list of non-empty strings")
    allowed = set(contract.get("allowed_source_ids", []))
    unapproved = sorted(set(evidence_refs) - allowed)
    if len(evidence_refs) != len(set(evidence_refs)):
        raise ValueError("evidence_refs must not contain duplicates")
    blockers = []
    if missing:
        blockers.append("required_output_fields_missing")
    if unapproved:
        blockers.append("evidence_reference_outside_allowlist")
    return {
        "task_id": contract["task_id"], "missing_output_fields": missing,
        "unapproved_evidence_refs": unapproved, "blockers": blockers,
        "eligible_for_human_review": not blockers,
        "completion_accepted": False, "execution_authorized": False,
        "automatic_approval": False, "scientific_validity_established": False,
    }

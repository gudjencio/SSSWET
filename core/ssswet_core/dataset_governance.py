"""Bounded governance checks for reproducible, privacy-aware dataset release.

The functions in this module evaluate researcher-supplied policy declarations and
metadata. They do not inspect raw participant records, interpret law, grant ethics
approval, delete data, or authorize publication. Every gate is advisory and must
be reviewed by an accountable human before a release decision.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from hashlib import sha256
import json
import re
import heapq
from typing import Any

MAX_POLICY_ITEMS = 500
MAX_FIELDS = 5_000
MAX_CELLS = 20_000
MAX_GRAPH_NODES = 10_000
MAX_GRAPH_EDGES = 50_000
MAX_SPLIT_ROWS = 200_000
MAX_RETENTION_RECORDS = 10_000
MAX_MANIFEST_BYTES = 250_000
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/#-]{0,239}$")
_SENSITIVE_NAME = re.compile(
    r"(^|_)(name|full_name|first_name|last_name|email|phone|telephone|address|"
    r"postal_code|postcode|passport|national_id|ssn|date_of_birth|dob|"
    r"participant_id|subject_id|device_id|latitude|longitude|gps|geolocation|"
    r"precise_location|ip_address)(_|$)", re.I,
)
_ALLOWED_CLASSIFICATIONS = {
    "public", "internal", "confidential", "personal_data", "sensitive_data", "unknown"
}


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _text(value: Any, field: str, maximum: int = 240) -> str:
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > maximum:
        raise ValueError(f"{field} must be non-empty text of at most {maximum} characters")
    return value.strip()


def _identifier(value: Any, field: str) -> str:
    value = _text(value, field)
    if not _ID.fullmatch(value):
        raise ValueError(f"{field} must be a conservative identifier")
    return value


def _bounded_list(value: Any, field: str, maximum: int) -> list:
    if not isinstance(value, list) or len(value) > maximum:
        raise ValueError(f"{field} must be a list of at most {maximum} items")
    return value


def _sensitive_field_name(value: str) -> bool:
    # Normalize common camelCase and punctuation before applying name-only rules.
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", normalized).strip("_")
    return bool(_SENSITIVE_NAME.search(normalized))


def _parse_date(value: Any, field: str) -> date:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be an ISO date")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO date") from exc
    if parsed.isoformat() != value:
        raise ValueError(f"{field} must use YYYY-MM-DD format")
    return parsed


def assess_license_use(policy: dict, requested_use: str) -> dict:
    """Check a human-reviewed, explicit license-use decision; do not interpret law."""
    if not isinstance(policy, dict):
        raise ValueError("policy must be an object")
    license_id = _text(policy.get("license_id"), "license_id", 160)
    status = policy.get("review_status")
    if not isinstance(status, str) or status not in {"approved", "pending", "rejected", "not_reviewed"}:
        raise ValueError("review_status must be approved, pending, rejected or not_reviewed")
    permitted = _bounded_list(policy.get("permitted_uses", []), "permitted_uses", MAX_POLICY_ITEMS)
    prohibited = _bounded_list(policy.get("prohibited_uses", []), "prohibited_uses", MAX_POLICY_ITEMS)
    if any(not isinstance(item, str) or not item.strip() for item in permitted + prohibited):
        raise ValueError("use declarations must be non-empty strings")
    permitted_keys = [item.strip().casefold() for item in permitted]
    prohibited_keys = [item.strip().casefold() for item in prohibited]
    if len(set(permitted_keys)) != len(permitted_keys) or len(set(prohibited_keys)) != len(prohibited_keys):
        raise ValueError("use declarations must not contain duplicates")
    requested = _text(requested_use, "requested_use", 120)
    reviewer = policy.get("reviewer_ref", "")
    reviewed_at = policy.get("reviewed_at", "")
    timestamp_valid = False
    if isinstance(reviewed_at, str) and reviewed_at.strip():
        try:
            parsed_reviewed_at = datetime.fromisoformat(reviewed_at.strip().replace("Z", "+00:00"))
            timestamp_valid = parsed_reviewed_at.tzinfo is not None and parsed_reviewed_at.utcoffset() is not None
        except ValueError:
            timestamp_valid = False
    review_complete = bool(
        status == "approved" and isinstance(reviewer, str) and reviewer.strip()
        and timestamp_valid
    )
    requested_key = requested.casefold()
    allowed = bool(
        review_complete and requested_key in permitted_keys and requested_key not in prohibited_keys
    )
    reasons = []
    if status != "approved":
        reasons.append("human_license_review_not_approved")
    if status == "approved" and not review_complete:
        reasons.append("reviewer_and_review_timestamp_required")
    if requested_key not in permitted_keys:
        reasons.append("requested_use_not_explicitly_permitted")
    if requested_key in prohibited_keys:
        reasons.append("requested_use_explicitly_prohibited")
    return {
        "license_id": license_id,
        "requested_use": requested,
        "policy_gate_passed": allowed,
        "review_status": status,
        "reviewer_ref_present": bool(isinstance(reviewer, str) and reviewer.strip()),
        "reasons": sorted(set(reasons)),
        "legal_interpretation_performed": False,
        "legal_advice": False,
        "human_review_required": True,
    }


def assess_consent_scope(consent: dict, requested_purpose: str, *, sharing_requested: bool = False) -> dict:
    """Check declared consent/purpose scope without accepting participant identifiers."""
    if not isinstance(consent, dict):
        raise ValueError("consent must be an object")
    status = consent.get("status")
    if not isinstance(status, str) or status not in {"documented", "not_required", "pending", "withdrawn", "not_recorded"}:
        raise ValueError("unsupported consent status")
    purpose = _text(requested_purpose, "requested_purpose", 120)
    purposes = _bounded_list(consent.get("permitted_purposes", []), "permitted_purposes", MAX_POLICY_ITEMS)
    if any(not isinstance(item, str) or not item.strip() for item in purposes):
        raise ValueError("permitted_purposes must contain non-empty strings")
    purpose_keys = [item.strip().casefold() for item in purposes]
    if len(set(purpose_keys)) != len(purpose_keys):
        raise ValueError("permitted_purposes must be unique")
    if not isinstance(sharing_requested, bool):
        raise ValueError("sharing_requested must be boolean")
    sharing_authorized = consent.get("sharing_authorized", False)
    if not isinstance(sharing_authorized, bool):
        raise ValueError("sharing_authorized must be boolean")
    reason_ref = consent.get("not_required_reason_ref", "")
    reviewer_ref = consent.get("reviewer_ref", "")
    evidence_ref = consent.get("consent_evidence_ref", "")
    reviewer_present = isinstance(reviewer_ref, str) and bool(reviewer_ref.strip())
    documented_supported = status == "documented" and bool(
        isinstance(evidence_ref, str) and evidence_ref.strip() and reviewer_present
    )
    not_required_supported = status == "not_required" and bool(
        isinstance(reason_ref, str) and reason_ref.strip() and reviewer_present
    )
    purpose_ok = purpose.casefold() in purpose_keys
    status_ok = documented_supported or not_required_supported
    sharing_ok = not sharing_requested or sharing_authorized
    passed = status_ok and purpose_ok and sharing_ok
    reasons = []
    if status == "withdrawn":
        reasons.append("consent_withdrawn")
    elif status in {"pending", "not_recorded"}:
        reasons.append("consent_not_confirmed")
    elif status == "documented" and not documented_supported:
        reasons.append("documented_consent_needs_evidence_and_reviewer_refs")
    elif status == "not_required" and not not_required_supported:
        reasons.append("not_required_decision_needs_reason_and_reviewer")
    if not purpose_ok:
        reasons.append("purpose_not_in_declared_scope")
    if sharing_requested and not sharing_authorized:
        reasons.append("sharing_not_authorized")
    return {
        "requested_purpose": purpose,
        "policy_gate_passed": passed,
        "consent_status": status,
        "sharing_requested": sharing_requested,
        "reasons": sorted(set(reasons)),
        "participant_identifiers_collected": False,
        "ethics_or_legal_approval_granted": False,
        "human_review_required": True,
    }


def audit_field_release_policy(fields: list[dict]) -> dict:
    """Audit field-name declarations and release dispositions; values are never read."""
    fields = _bounded_list(fields, "fields", MAX_FIELDS)
    seen = set()
    findings = []
    blockers = []
    for item in fields:
        if not isinstance(item, dict):
            raise ValueError("each field declaration must be an object")
        name = _text(item.get("name"), "field name", 200)
        key = name.casefold()
        if key in seen:
            raise ValueError(f"duplicate field declaration: {name}")
        seen.add(key)
        classification = item.get("classification", "unknown")
        action = item.get("release_action", "review")
        if not isinstance(classification, str) or classification not in _ALLOWED_CLASSIFICATIONS:
            raise ValueError(f"unsupported classification for {name}")
        if not isinstance(action, str) or action not in {"include", "exclude", "coarsen", "aggregate", "review"}:
            raise ValueError(f"unsupported release_action for {name}")
        review_ref = item.get("review_ref", "")
        declared_sensitive = classification in {"internal", "confidential", "personal_data", "sensitive_data"} or _sensitive_field_name(name)
        reasons = []
        if classification == "unknown":
            reasons.append("classification_unknown")
        if declared_sensitive and action in {"include", "review"}:
            reasons.append("sensitive_field_not_minimized")
        if declared_sensitive and action in {"exclude", "coarsen", "aggregate"}:
            transformation_status = item.get("transformation_status")
            transformation_ref = item.get("transformation_ref", "")
            if transformation_status != "completed" or not (isinstance(transformation_ref, str) and transformation_ref.strip()):
                reasons.append("completed_transformation_reference_required")
            if action in {"coarsen", "aggregate"} and not (isinstance(review_ref, str) and review_ref.strip()):
                reasons.append("transformation_review_reference_required")
        if reasons:
            blockers.append({"field": name, "reasons": reasons})
        findings.append({
            "field": name,
            "classification": classification,
            "release_action": action,
            "sensitive_name_pattern_matched": _sensitive_field_name(name),
            "review_ref_present": bool(isinstance(review_ref, str) and review_ref.strip()),
            "reasons": reasons,
        })
    return {
        "field_count": len(fields),
        "release_blockers": blockers,
        "release_ready": not blockers,
        "policy_gate_passed": not blockers,
        "field_values_inspected": False,
        "automatic_redaction_performed": False,
        "limitations": "Field-name and declared-policy screening only; it cannot detect identifiers hidden in free text or data values.",
    }


def screen_aggregate_disclosure(cells: list[dict], minimum_group_size: int = 5) -> dict:
    """Apply primary and complementary suppression to supplied aggregate counts."""
    cells = _bounded_list(cells, "cells", MAX_CELLS)
    if isinstance(minimum_group_size, bool) or not isinstance(minimum_group_size, int) or not 2 <= minimum_group_size <= 1000:
        raise ValueError("minimum_group_size must be an integer from 2 to 1000")
    normalized = []
    seen = set()
    for cell in cells:
        if not isinstance(cell, dict):
            raise ValueError("each aggregate cell must be an object")
        cell_id = _identifier(cell.get("cell_id"), "cell_id")
        group_id = _identifier(cell.get("group_id"), "group_id")
        count = cell.get("count")
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise ValueError("aggregate counts must be non-negative integers")
        if cell_id in seen:
            raise ValueError("cell_id values must be unique")
        seen.add(cell_id)
        normalized.append({"cell_id": cell_id, "group_id": group_id, "count": count})
    suppressed = {cell["cell_id"] for cell in normalized if cell["count"] < minimum_group_size}
    reasons = {cell["cell_id"]: "below_minimum_group_size" for cell in normalized if cell["count"] < minimum_group_size}
    grouped: dict[str, list[dict]] = {}
    for cell in normalized:
        grouped.setdefault(cell["group_id"], []).append(cell)
    for group in grouped.values():
        hidden = [cell for cell in group if cell["cell_id"] in suppressed]
        visible = [cell for cell in group if cell["cell_id"] not in suppressed]
        if len(hidden) == 1 and visible:
            complement = min(visible, key=lambda item: (item["count"], item["cell_id"]))
            suppressed.add(complement["cell_id"])
            reasons[complement["cell_id"]] = "complementary_suppression_to_reduce_differencing"
    output = []
    for cell in sorted(normalized, key=lambda item: (item["group_id"], item["cell_id"])):
        hidden = cell["cell_id"] in suppressed
        output.append({
            "cell_id": cell["cell_id"],
            "group_id": cell["group_id"],
            "count": None if hidden else cell["count"],
            "suppressed": hidden,
            "reason": reasons.get(cell["cell_id"], ""),
        })
    return {
        "cell_count": len(output),
        "suppressed_cell_count": len(suppressed),
        "minimum_group_size": minimum_group_size,
        "cells": output,
        "policy_gate_passed": True,
        "disclosure_risk_eliminated": False,
        "limitations": "Small-cell and single-suppression differencing controls only; auxiliary data and repeated releases can still disclose information.",
    }


def compare_dataset_schemas(previous: dict, current: dict) -> dict:
    """Compare field contracts and classify additive versus potentially breaking changes."""
    if not isinstance(previous, dict) or not isinstance(current, dict):
        raise ValueError("both schemas must be objects mapping field names to declarations")
    if len(previous) > MAX_FIELDS or len(current) > MAX_FIELDS:
        raise ValueError("schema exceeds the field limit")
    def normalize(schema: dict) -> dict:
        result = {}
        for raw_name, declaration in schema.items():
            name = _text(raw_name, "schema field name", 200)
            if not isinstance(declaration, dict):
                raise ValueError(f"schema declaration for {name} must be an object")
            kind = _text(declaration.get("type"), f"{name}.type", 80).casefold()
            nullable = declaration.get("nullable", True)
            required = declaration.get("required", False)
            if not isinstance(nullable, bool) or not isinstance(required, bool):
                raise ValueError(f"{name}.nullable and {name}.required must be booleans")
            result[name] = {"type": kind, "nullable": nullable, "required": required}
        return result
    old, new = normalize(previous), normalize(current)
    added, removed, changed = [], [], []
    for name in sorted(set(new) - set(old)):
        item = {"field": name, "current": new[name]}
        if new[name]["required"] or not new[name]["nullable"]:
            reasons = []
            if new[name]["required"]:
                reasons.append("new_required_field")
            if not new[name]["nullable"]:
                reasons.append("new_non_nullable_field")
            item["reasons"] = reasons
            changed.append(item)
        else:
            added.append(item)
    for name in sorted(set(old) - set(new)):
        removed.append({"field": name, "previous": old[name]})
    for name in sorted(set(old) & set(new)):
        before, after = old[name], new[name]
        reasons = []
        if before["type"] != after["type"]:
            reasons.append("type_changed")
        if before["nullable"] and not after["nullable"]:
            reasons.append("nullable_tightened")
        if not before["required"] and after["required"]:
            reasons.append("required_tightened")
        if reasons:
            changed.append({"field": name, "previous": before, "current": after, "reasons": reasons})
    breaking = bool(removed or changed)
    return {
        "added_optional_fields": added,
        "removed_fields": removed,
        "breaking_field_changes": changed,
        "breaking_change_count": len(removed) + len(changed),
        "compatible_additive_change": bool(added) and not breaking,
        "schema_compatible": not breaking,
        "policy_gate_passed": not breaking,
        "previous_field_count": len(old),
        "current_field_count": len(new),
    }


def audit_lineage_graph(nodes: list[dict], edges: list[dict]) -> dict:
    """Check a bounded directed dataset/transformation graph for missing nodes and cycles."""
    nodes = _bounded_list(nodes, "nodes", MAX_GRAPH_NODES)
    edges = _bounded_list(edges, "edges", MAX_GRAPH_EDGES)
    identifiers = []
    for node in nodes:
        if not isinstance(node, dict):
            raise ValueError("each lineage node must be an object")
        identifiers.append(_identifier(node.get("id"), "node id"))
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("lineage node identifiers must be unique")
    known = set(identifiers)
    outgoing = {item: set() for item in known}
    incoming = {item: 0 for item in known}
    missing, self_links = [], []
    seen_edges = set()
    for edge in edges:
        if not isinstance(edge, dict):
            raise ValueError("each lineage edge must be an object")
        source = _identifier(edge.get("from"), "edge.from")
        target = _identifier(edge.get("to"), "edge.to")
        pair = (source, target)
        if pair in seen_edges:
            raise ValueError("duplicate lineage edges are not allowed")
        seen_edges.add(pair)
        if source not in known or target not in known:
            missing.append({"from": source, "to": target})
            continue
        if source == target:
            self_links.append(source)
            continue
        if target not in outgoing[source]:
            outgoing[source].add(target)
            incoming[target] += 1
    has_incoming = {target for targets in outgoing.values() for target in targets}
    queue = [item for item, degree in incoming.items() if degree == 0]
    heapq.heapify(queue)
    topo = []
    while queue:
        current = heapq.heappop(queue)
        topo.append(current)
        for target in outgoing[current]:
            incoming[target] -= 1
            if incoming[target] == 0:
                heapq.heappush(queue, target)
    unresolved = sorted(item for item, degree in incoming.items() if degree > 0)
    isolated = sorted(item for item in known if not outgoing[item] and item not in has_incoming)
    valid = not missing and not self_links and not unresolved
    return {
        "node_count": len(nodes), "edge_count": len(edges),
        "missing_endpoint_edges": missing, "self_link_nodes": sorted(self_links),
        "nodes_not_topologically_resolved": unresolved, "isolated_nodes": isolated,
        "topological_order": topo,
        "valid": valid, "policy_gate_passed": valid,
        "graph_is_complete": not missing,
    }


def audit_group_time_splits(
    splits: dict[str, list[dict]], *, group_field: str, time_field: str,
    split_order: list[str] | None = None, max_records: int = MAX_SPLIT_ROWS,
) -> dict:
    """Detect group overlap and chronological leakage in declared data partitions."""
    if not isinstance(splits, dict) or len(splits) < 2:
        raise ValueError("at least two named splits are required")
    if not isinstance(max_records, int) or isinstance(max_records, bool) or not 1 <= max_records <= MAX_SPLIT_ROWS:
        raise ValueError("max_records must be between 1 and the configured maximum")
    group_key = _text(group_field, "group_field", 120)
    time_key = _text(time_field, "time_field", 120)
    names = []
    for raw_name in splits:
        normalized_name = _text(raw_name, "split name", 80)
        if normalized_name != raw_name:
            raise ValueError("split names must not contain leading or trailing whitespace")
        names.append(normalized_name)
    names.sort()
    order = split_order if split_order is not None else names
    if (not isinstance(order, list) or any(not isinstance(item, str) for item in order)
            or len(order) != len(set(order)) or set(order) != set(names)):
        raise ValueError("split_order must contain every split name exactly once")
    group_to_splits: dict[str, set[str]] = {}
    ranges = {}
    total = 0
    for split_name in order:
        rows = splits[split_name]
        if not isinstance(rows, list):
            raise ValueError("each split must be a list of records")
        total += len(rows)
        if total > max_records:
            raise ValueError("split records exceed the configured limit")
        timestamps = []
        for row in rows:
            if not isinstance(row, dict) or group_key not in row or time_key not in row:
                raise ValueError("every split row must contain group and time fields")
            raw_group = row[group_key]
            if isinstance(raw_group, bool) or not isinstance(raw_group, (str, int)):
                raise ValueError(f"{group_key} values must be non-empty strings or integers")
            group = _text(str(raw_group), group_key, 240)
            raw_time = _text(row[time_key], time_key, 80)
            try:
                parsed = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
            except ValueError as exc:
                raise ValueError(f"{time_key} values must be ISO-8601 timestamps") from exc
            if parsed.tzinfo is None or parsed.utcoffset() is None:
                raise ValueError("timestamps must include an explicit timezone")
            timestamps.append(parsed.astimezone(timezone.utc))
            group_to_splits.setdefault(group, set()).add(split_name)
        if timestamps:
            low, high = min(timestamps), max(timestamps)
            ranges[split_name] = {"minimum": low.isoformat(), "maximum": high.isoformat(), "record_count": len(rows)}
        else:
            ranges[split_name] = {"minimum": None, "maximum": None, "record_count": 0}
    overlap_patterns: dict[tuple[str, ...], int] = {}
    for partitions in group_to_splits.values():
        if len(partitions) > 1:
            pattern = tuple(sorted(partitions))
            overlap_patterns[pattern] = overlap_patterns.get(pattern, 0) + 1
    overlaps = [
        {"splits": list(pattern), "group_count": count}
        for pattern, count in sorted(overlap_patterns.items())
    ]
    violations = []
    previous_name = None
    for split_name in order:
        current = ranges[split_name]
        if previous_name and ranges[previous_name]["maximum"] and current["minimum"]:
            previous_max = datetime.fromisoformat(ranges[previous_name]["maximum"])
            current_min = datetime.fromisoformat(current["minimum"])
            if previous_max >= current_min:
                violations.append({"earlier_split": previous_name, "later_split": split_name,
                                   "earlier_maximum": previous_max.isoformat(), "later_minimum": current_min.isoformat()})
        if current["maximum"]:
            previous_name = split_name
    passed = not overlaps and not violations
    return {
        "split_order": order, "record_count": total, "time_ranges": ranges,
        "group_overlap_count": sum(overlap_patterns.values()),
        "group_overlap_pattern_count": len(overlaps), "group_overlaps": overlaps,
        "time_order_violations": violations,
        "group_leakage_detected": bool(overlaps),
        "temporal_leakage_detected": bool(violations),
        "policy_gate_passed": passed,
        "scope": "declared group and timestamp checks; semantic, near-duplicate and unobserved leakage are not assessed",
    }


def plan_retention_reviews(records: list[dict], as_of: str) -> dict:
    """Calculate review dates without deleting, archiving or altering any dataset."""
    records = _bounded_list(records, "records", MAX_RETENTION_RECORDS)
    today = _parse_date(as_of, "as_of")
    seen = set()
    output = []
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("each retention record must be an object")
        dataset_id = _identifier(record.get("dataset_id"), "dataset_id")
        if dataset_id in seen:
            raise ValueError("dataset_id values must be unique")
        seen.add(dataset_id)
        start = _parse_date(record.get("retention_start"), "retention_start")
        days = record.get("retention_days")
        if isinstance(days, bool) or not isinstance(days, int) or not 1 <= days <= 36500:
            raise ValueError("retention_days must be an integer from 1 to 36500")
        hold = record.get("legal_or_policy_hold", False)
        if not isinstance(hold, bool):
            raise ValueError("legal_or_policy_hold must be boolean")
        basis = _text(record.get("policy_ref"), "policy_ref", 240)
        due = start + timedelta(days=days)
        state = "on_hold" if hold else "review_due" if due <= today else "not_due"
        output.append({
            "dataset_id": dataset_id, "review_due_on": due.isoformat(),
            "state": state, "policy_ref": basis,
            "days_until_review": (due - today).days,
        })
    output.sort(key=lambda item: (item["state"] != "review_due", item["review_due_on"], item["dataset_id"]))
    overdue = sum(item["state"] == "review_due" for item in output)
    return {
        "as_of": today.isoformat(), "records": output,
        "review_due_count": overdue, "on_hold_count": sum(item["state"] == "on_hold" for item in output),
        "policy_gate_passed": overdue == 0,
        "data_deleted": False, "retention_policy_changed": False,
        "human_review_required": True,
    }


def build_release_readiness(reports: dict) -> dict:
    """Combine named governance reports into a review queue, never an approval."""
    required = ("license", "consent", "field_privacy", "disclosure", "schema", "lineage", "split_integrity", "retention")
    if not isinstance(reports, dict):
        raise ValueError("reports must be an object")
    missing = [name for name in required if name not in reports]
    blockers = []
    for name in required:
        if name not in reports:
            blockers.append({"check": name, "reason": "required_report_missing"})
            continue
        report = reports[name]
        if not isinstance(report, dict) or not isinstance(report.get("policy_gate_passed"), bool):
            blockers.append({"check": name, "reason": "report_missing_boolean_policy_gate_passed"})
        elif report["policy_gate_passed"] is False:
            blockers.append({"check": name, "reason": "policy_gate_not_passed"})
    return {
        "required_checks": list(required),
        "missing_checks": missing,
        "blockers": blockers,
        "ready_for_human_release_review": not blockers,
        "release_authorized": False,
        "scientific_validity_established": False,
        "legal_or_ethics_approval_granted": False,
        "human_review_required": True,
    }


def build_release_manifest(
    *, dataset_id: str, dataset_version: int, schema_digest: str,
    artifact_digests: dict, source_refs: list[str], review_refs: list[str],
    readiness_report: dict, software_version: str,
) -> dict:
    """Create a deterministic metadata-only release manifest and SHA-256 digest."""
    dataset = _identifier(dataset_id, "dataset_id")
    if isinstance(dataset_version, bool) or not isinstance(dataset_version, int) or dataset_version < 1:
        raise ValueError("dataset_version must be a positive integer")
    if not isinstance(schema_digest, str) or not re.fullmatch(r"[0-9a-f]{64}", schema_digest):
        raise ValueError("schema_digest must be a lowercase SHA-256 digest")
    if not isinstance(artifact_digests, dict) or len(artifact_digests) > 500:
        raise ValueError("artifact_digests must be an object of at most 500 entries")
    normalized_artifacts = {}
    for name, digest in artifact_digests.items():
        key = _identifier(name, "artifact name")
        if key in normalized_artifacts:
            raise ValueError("artifact names must be unique after normalization")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError(f"artifact {key} must have a lowercase SHA-256 digest")
        normalized_artifacts[key] = digest
    sources = _bounded_list(source_refs, "source_refs", 1000)
    reviews = _bounded_list(review_refs, "review_refs", 1000)
    if any(not isinstance(item, str) or not _ID.fullmatch(item.strip()) for item in sources + reviews):
        raise ValueError("source_refs and review_refs must contain conservative identifiers")
    sources = [item.strip() for item in sources]
    reviews = [item.strip() for item in reviews]
    if len(set(sources)) != len(sources) or len(set(reviews)) != len(reviews):
        raise ValueError("source_refs and review_refs must be unique")
    if not isinstance(readiness_report, dict) or not isinstance(readiness_report.get("ready_for_human_release_review"), bool):
        raise ValueError("readiness_report must contain a boolean ready_for_human_release_review")
    software = _text(software_version, "software_version", 120)
    try:
        readiness_bytes = _canonical(readiness_report).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ValueError("readiness_report must contain finite JSON-compatible values") from exc
    if len(readiness_bytes) > 64_000:
        raise ValueError("readiness_report exceeds 64000 bytes")
    readiness_digest = sha256(readiness_bytes).hexdigest()
    payload = {
        "manifest_schema_version": 1,
        "dataset_id": dataset,
        "dataset_version": dataset_version,
        "schema_digest": schema_digest,
        "artifact_digests": dict(sorted(normalized_artifacts.items())),
        "source_refs": sorted(sources),
        "review_refs": sorted(reviews),
        "readiness_report_digest": readiness_digest,
        "ready_for_human_release_review": readiness_report["ready_for_human_release_review"],
        "software_version": software,
        "raw_dataset_content_included": False,
        "release_authorized": False,
    }
    canonical = _canonical(payload).encode("utf-8")
    if len(canonical) > MAX_MANIFEST_BYTES:
        raise ValueError(f"manifest exceeds {MAX_MANIFEST_BYTES} bytes")
    return {**payload, "manifest_sha256": sha256(canonical).hexdigest()}


def verify_release_manifest(manifest: dict) -> dict:
    """Verify manifest integrity; a matching hash does not authenticate its author."""
    if not isinstance(manifest, dict):
        raise ValueError("manifest must be an object")
    recorded = manifest.get("manifest_sha256")
    payload = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    try:
        canonical = _canonical(payload).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ValueError("manifest must contain finite JSON-compatible values") from exc
    if len(canonical) > MAX_MANIFEST_BYTES:
        raise ValueError(f"manifest exceeds {MAX_MANIFEST_BYTES} bytes")
    expected = sha256(canonical).hexdigest()
    valid = isinstance(recorded, str) and re.fullmatch(r"[0-9a-f]{64}", recorded) is not None and recorded == expected
    return {
        "valid": valid,
        "recorded_sha256": recorded,
        "expected_sha256": expected,
        "tampered_or_incomplete": not valid,
        "author_authenticated": False,
    }

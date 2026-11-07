"""Bounded, provenance-aware diffing between scientific-memory snapshots.

Absence in a later snapshot is reported as a snapshot difference, not deletion.
No record, review state or scientific claim is modified.
"""
from __future__ import annotations
from hashlib import sha256
import json

MAX_RECORDS = 500
_PROVENANCE_FIELDS = ("source_ids", "experiment_ids", "graph_node_ids", "evidence_refs", "review_refs", "provenance_groups")
_TRACKED_FIELDS = ("version_id", "statement", "topic", "summary", "status", "review_state", "validated", "contested", *_PROVENANCE_FIELDS)

def _canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)

def _snapshot(snapshot: dict, label: str) -> tuple[str, dict[str, dict]]:
    if not isinstance(snapshot, dict):
        raise ValueError(f"{label} snapshot must be an object")
    snapshot_id = snapshot.get("snapshot_id")
    if not isinstance(snapshot_id, str) or not snapshot_id.strip() or len(snapshot_id) > 160:
        raise ValueError(f"{label} snapshot_id must contain 1 to 160 characters")
    records = snapshot.get("records")
    if not isinstance(records, list) or len(records) > MAX_RECORDS:
        raise ValueError(f"{label} records must be a list of at most {MAX_RECORDS} items")
    indexed = {}
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"{label} record {index} must be an object")
        memory_id = record.get("memory_id")
        if not isinstance(memory_id, str) or not memory_id.strip() or len(memory_id) > 240:
            raise ValueError(f"{label} records require stable memory_id values")
        if memory_id in indexed:
            raise ValueError(f"{label} snapshot contains duplicate memory_id: {memory_id}")
        for field in _PROVENANCE_FIELDS:
            values = record.get(field, [])
            if values is not None and (not isinstance(values, list) or any(not isinstance(value, str) or not value.strip() for value in values)):
                raise ValueError(f"{label} record {memory_id}: {field} must be a list of non-empty strings")
        try:
            _canonical(record)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{label} record {memory_id} must be finite JSON-compatible data") from exc
        indexed[memory_id] = record
    return snapshot_id.strip(), indexed

def compare_memory_revisions(previous: dict, current: dict) -> dict:
    """Compare immutable snapshots by stable memory ID and report exact field deltas."""
    previous_id, before = _snapshot(previous, "previous")
    current_id, after = _snapshot(current, "current")
    previous_ids, current_ids = set(before), set(after)
    added_ids, absent_ids = sorted(current_ids - previous_ids), sorted(previous_ids - current_ids)
    changed, unchanged = [], 0
    for memory_id in sorted(previous_ids & current_ids):
        left, right = before[memory_id], after[memory_id]
        fields = [field for field in _TRACKED_FIELDS if left.get(field) != right.get(field)]
        if not fields:
            unchanged += 1
            continue
        provenance_delta = {}
        for field in _PROVENANCE_FIELDS:
            old_values, new_values = set(left.get(field) or []), set(right.get(field) or [])
            if old_values != new_values:
                provenance_delta[field] = {"added": sorted(new_values - old_values), "removed": sorted(old_values - new_values)}
        changed.append({
            "memory_id": memory_id, "changed_fields": fields,
            "claim_text_changed": any(field in fields for field in ("statement", "summary", "topic")),
            "review_state_changed": any(field in fields for field in ("status", "review_state", "validated", "contested")),
            "provenance_changed": bool(provenance_delta), "provenance_delta": provenance_delta,
            "previous_record_sha256": sha256(_canonical(left).encode("utf-8")).hexdigest(),
            "current_record_sha256": sha256(_canonical(right).encode("utf-8")).hexdigest(),
        })
    return {
        "previous_snapshot_id": previous_id, "current_snapshot_id": current_id,
        "previous_record_count": len(before), "current_record_count": len(after),
        "added_memory_ids": added_ids, "absent_from_current_snapshot_ids": absent_ids,
        "changed_records": changed, "changed_count": len(changed), "unchanged_count": unchanged,
        "snapshot_added_count": len(added_ids), "snapshot_absent_count": len(absent_ids),
        "tracked_fields": list(_TRACKED_FIELDS), "bounded": True,
        "absent_records_are_not_deleted_by_this_tool": True,
        "records_or_review_states_modified": False, "scientific_validity_or_truth_adjudicated": False,
    }

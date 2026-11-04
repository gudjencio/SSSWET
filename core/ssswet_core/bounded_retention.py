"""Bounded retention helpers with explicit provenance and omission audits."""
from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass

@dataclass(frozen=True)
class RetentionPolicy:
    max_items: int = 10000
    keep_latest_per_key: bool = True
    protected_statuses: tuple[str, ...] = ("candidate", "contested", "under_review")

def compact_records(records: list[dict], *, key_field: str = "key",
                    policy: RetentionPolicy = RetentionPolicy()) -> list[dict]:
    if policy.max_items <= 0:
        raise ValueError("max_items must be positive")
    selected = records
    if policy.keep_latest_per_key:
        latest = {}
        for record in records:
            key = record.get(key_field)
            latest.pop(key, None)
            latest[key] = record
        selected = list(latest.values())
    return selected[-policy.max_items:]

def compact_records_with_audit(records: list[dict], *, key_field: str = "key",
                               policy: RetentionPolicy = RetentionPolicy()) -> dict:
    """Create a bounded projection while preserving per-key provenance lineage.

    This function never deletes or mutates its input records. Protected records
    may exceed the nominal cap; the report makes that capacity condition clear.
    """
    if not isinstance(records, list) or any(not isinstance(item, dict) for item in records):
        raise TypeError("records must be a list of mappings")
    if isinstance(policy.max_items, bool) or not isinstance(policy.max_items, int) or policy.max_items <= 0:
        raise ValueError("max_items must be positive")
    groups = {}
    for index, record in enumerate(records):
        key = record.get(key_field)
        group_key = ("key", key) if key is not None else ("index", index)
        groups.setdefault(group_key, []).append((index, record))
    prepared = []
    all_source_refs = set()
    for group_key, entries in groups.items():
        latest_index, latest_record = entries[-1]
        merged = deepcopy(latest_record)
        source_refs, status_history, record_ids = [], [], []
        protected = False
        for index, record in entries:
            for field in ("source_ids", "evidence_refs", "provenance_refs"):
                values = record.get(field, []) or []
                if isinstance(values, str):
                    values = [values]
                if isinstance(values, (list, tuple)):
                    source_refs.extend(value for value in values if isinstance(value, str) and value)
            source_reference = record.get("source_reference")
            if isinstance(source_reference, str) and source_reference:
                source_refs.append(source_reference)
            status = record.get("status")
            if isinstance(status, str) and status:
                status_history.append(status)
                if status in policy.protected_statuses:
                    protected = True
            if record.get("is_current") or record.get("contested_by_graph") or record.get("has_unresolved_questions"):
                protected = True
            record_ids.append(record.get("record_id") or record.get("memory_id") or record.get("version_id")
                              or record.get(key_field) or f"index:{index}")
        unique_sources = list(dict.fromkeys(source_refs))
        all_source_refs.update(unique_sources)
        merged["retention_source_ids"] = unique_sources
        merged["retention_status_history"] = list(dict.fromkeys(status_history))
        merged["retention_history_count"] = len(entries)
        merged["retention_protected"] = protected
        merged["retention_record_ids"] = record_ids
        prepared.append({"last_index": latest_index, "record": merged, "protected": protected, "group_key": group_key})
    protected_items = [item for item in prepared if item["protected"]]
    optional_items = [item for item in prepared if not item["protected"]]
    capacity_exceeded = len(protected_items) > policy.max_items
    slots = max(0, policy.max_items - len(protected_items))
    selected = protected_items + sorted(optional_items, key=lambda item: item["last_index"], reverse=True)[:slots]
    selected.sort(key=lambda item: item["last_index"])
    selected_records = [item["record"] for item in selected]
    retained_sources = {source for item in selected_records for source in item.get("retention_source_ids", [])}
    omitted = [item for item in prepared if item not in selected]
    omitted_ids = [identifier for item in omitted for identifier in item["record"].get("retention_record_ids", [])]
    before_count, after_count = len(all_source_refs), len(retained_sources)
    return {
        "records": selected_records, "input_record_count": len(records),
        "retained_group_count": len(selected_records), "omitted_group_count": len(omitted),
        "protected_group_count": len(protected_items), "capacity_exceeded": capacity_exceeded,
        "omitted_record_ids": omitted_ids, "provenance_reference_count_before": before_count,
        "provenance_reference_count_retained": after_count,
        "provenance_retention_ratio": round(after_count / before_count, 4) if before_count else 1.0,
        "input_records_mutated": False, "source_records_deleted": False,
    }

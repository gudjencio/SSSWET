"""Bounded scientific-memory compaction with conservative provenance retention."""
from __future__ import annotations


_MERGED_LIST_FIELDS = (
    "source_ids", "experiment_ids", "graph_node_ids", "evidence_refs",
    "provenance_groups", "review_refs",
)


def compact(records: list[dict], *, max_records: int = 1000) -> dict:
    if not isinstance(records, list):
        raise ValueError("records must be a list")
    if isinstance(max_records, bool) or not isinstance(max_records, int) or max_records < 1:
        raise ValueError("max_records must be positive")
    groups: dict[str, list[dict]] = {}
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("every memory record must be a dictionary")
        key = " ".join(str(record.get("statement", "")).casefold().split())
        if not key:
            continue
        groups.setdefault(key, []).append(record)

    chosen = []
    provenance_values_merged = 0
    for group in groups.values():
        selected = dict(sorted(
            group,
            key=lambda r: (
                bool(r.get("validated", False)),
                str(r.get("updated_at", "")),
                str(r.get("memory_id", "")),
            ),
            reverse=True,
        )[0])
        merged_ids = []
        for field in _MERGED_LIST_FIELDS:
            values = []
            for record in group:
                candidate = record.get(field, [])
                if candidate is None:
                    continue
                if not isinstance(candidate, list):
                    raise ValueError(f"{field} must be a list when supplied")
                for value in candidate:
                    if not isinstance(value, str) or not value.strip():
                        raise ValueError(f"{field} values must be non-empty strings")
                    if value not in values:
                        values.append(value)
            if values:
                selected[field] = values
                provenance_values_merged += len(values)
        for record in group:
            identifier = record.get("memory_id")
            if isinstance(identifier, str) and identifier and identifier not in merged_ids:
                merged_ids.append(identifier)
        selected["merged_memory_ids"] = merged_ids
        selected["merged_duplicate_count"] = len(group)
        selected["provenance_merged"] = True
        selected["review_states"] = sorted({
            str(record.get("status")) for record in group if record.get("status")
        })
        chosen.append(selected)

    chosen.sort(key=lambda r: (str(r.get("updated_at", "")), str(r.get("memory_id", ""))), reverse=True)
    retained = chosen[:max_records]
    return {
        "records": retained,
        "input_count": len(records),
        "unique_statements": len(chosen),
        "retained_count": len(retained),
        "dropped_count": max(0, len(chosen) - len(retained)),
        "provenance_values_merged": provenance_values_merged,
        "unbounded_growth": False,
    }

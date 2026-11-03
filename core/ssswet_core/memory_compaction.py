"""Bounded scientific-memory compaction that preserves review state and provenance."""
from __future__ import annotations


def compact(records: list[dict], *, max_records: int = 1000) -> dict:
    if isinstance(max_records, bool) or not isinstance(max_records, int) or max_records < 1:
        raise ValueError("max_records must be positive")
    groups: dict[str, list[dict]] = {}
    for record in records:
        key = " ".join(str(record.get("statement", "")).casefold().split())
        if not key:
            continue
        groups.setdefault(key, []).append(record)
    chosen = []
    for group in groups.values():
        chosen.append(sorted(group, key=lambda r: (bool(r.get("validated", False)), str(r.get("updated_at", "")), str(r.get("memory_id", ""))), reverse=True)[0])
    chosen.sort(key=lambda r: (str(r.get("updated_at", "")), str(r.get("memory_id", ""))), reverse=True)
    retained = chosen[:max_records]
    return {"records": retained, "input_count": len(records), "unique_statements": len(chosen), "retained_count": len(retained), "dropped_count": max(0, len(chosen) - len(retained)), "unbounded_growth": False}

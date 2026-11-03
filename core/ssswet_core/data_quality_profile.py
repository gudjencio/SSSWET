"""Deterministic quality profile for tabular research records."""
from __future__ import annotations


def profile(records: list[dict], *, id_field: str = "id", required_fields: tuple[str, ...] = ()) -> dict:
    total = len(records)
    missing = {field: 0 for field in required_fields}
    ids = []
    for record in records:
        ids.append(record.get(id_field))
        for field in required_fields:
            if record.get(field) in (None, ""):
                missing[field] += 1
    duplicate_ids = len(ids) - len({item for item in ids if item is not None})
    completeness = 1.0 if not total or not required_fields else 1 - sum(missing.values()) / (total * len(required_fields))
    return {"records": total, "missing_by_field": missing, "duplicate_ids": duplicate_ids, "completeness": max(0.0, completeness)}

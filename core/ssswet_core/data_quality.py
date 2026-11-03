"""Deterministic data-quality checks for research records."""
from __future__ import annotations


def profile(records: list[dict], required: tuple[str, ...]) -> dict:
    total = len(records)
    missing = {field: 0 for field in required}
    duplicate_ids = 0
    seen = set()
    for record in records:
        for field in required:
            if record.get(field) in (None, "", []):
                missing[field] += 1
        rid = record.get("id")
        if rid is not None:
            if rid in seen:
                duplicate_ids += 1
            seen.add(rid)
    complete = total - sum(1 for r in records if any(r.get(f) in (None, "", []) for f in required))
    return {"records": total, "complete_records": complete, "missing": missing, "duplicate_ids": duplicate_ids, "completeness_ratio": complete / total if total else 1.0}

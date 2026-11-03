"""Detect identifier overlap between declared dataset splits."""
from __future__ import annotations

def inspect(splits: dict[str, list[dict]], id_field: str = "id", max_records: int = 1_000_000) -> dict:
    if not isinstance(splits, dict) or len(splits) < 2:
        raise ValueError("at least two named splits are required")
    if not isinstance(id_field, str) or not id_field.strip():
        raise ValueError("id_field is required")
    seen, total = {}, 0
    for split_name in sorted(splits):
        records = splits[split_name]
        if not isinstance(split_name, str) or not split_name or not isinstance(records, list):
            raise ValueError("split names and record lists must be valid")
        total += len(records)
        if total > max_records:
            raise ValueError("split records exceed the configured limit")
        local = set()
        for record in records:
            if not isinstance(record, dict) or id_field not in record:
                raise ValueError(f"every record must contain {id_field}")
            value = record[id_field]
            if not isinstance(value, (str, int)) or isinstance(value, bool) or str(value).strip() == "":
                raise ValueError("split identifiers must be non-empty strings or integers")
            normalized = str(value).strip()
            if normalized in local:
                raise ValueError(f"duplicate identifier within split {split_name}")
            local.add(normalized)
            seen.setdefault(normalized, []).append(split_name)
    overlaps = [{"id": key, "splits": names} for key, names in sorted(seen.items()) if len(names) > 1]
    return {"split_count": len(splits), "record_count": total, "overlap_count": len(overlaps), "overlaps": overlaps, "leakage_detected": bool(overlaps), "scope": "identifier overlap only; semantic or near-duplicate leakage is not assessed"}

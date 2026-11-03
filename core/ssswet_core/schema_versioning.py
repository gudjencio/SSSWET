"""Small schema-version guard for persisted research records."""
from __future__ import annotations


def check(record: dict, expected: int, required: tuple[str, ...] = ()) -> dict:
    version = record.get("schema_version")
    missing = [key for key in required if key not in record]
    compatible = version == expected and not missing
    return {"compatible": compatible, "version": version, "expected_version": expected, "missing": missing}

"""Validated, auditable SHA-256 provenance chains."""
from __future__ import annotations
import hashlib
import json
import re
from dataclasses import dataclass

_SHA256 = re.compile(r"^[0-9a-f]{64}$")

@dataclass(frozen=True)
class ProvenanceRecord:
    source_id: str
    source_type: str
    reference: str
    content_digest: str
    parent_digest: str | None = None

    def __post_init__(self) -> None:
        for name in ("source_id", "source_type", "reference"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} is required")
        if not isinstance(self.content_digest, str) or not _SHA256.fullmatch(self.content_digest):
            raise ValueError("content_digest must be a lowercase SHA-256 hex digest")
        if self.parent_digest is not None and not isinstance(self.parent_digest, str):
            raise ValueError("parent_digest must be null or text")

def content_digest(content: str) -> str:
    if not isinstance(content, str):
        raise TypeError("content must be text")
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def provenance_digest(record: ProvenanceRecord) -> str:
    payload = json.dumps(record.__dict__, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return content_digest(payload)

def verify_chain(records: list[ProvenanceRecord]) -> dict:
    """Check genesis, parent links and source uniqueness without judging source truth."""
    if not isinstance(records, list):
        raise TypeError("records must be a list")
    previous = None
    seen_sources: set[str] = set()
    issues: list[dict] = []
    for index, record in enumerate(records):
        if not isinstance(record, ProvenanceRecord):
            issues.append({"index": index, "code": "invalid_record_type"})
            continue
        if index == 0:
            if record.parent_digest is not None:
                issues.append({"index": index, "code": "genesis_parent_must_be_null", "source_id": record.source_id})
        elif record.parent_digest != previous:
            issues.append({
                "index": index, "code": "parent_digest_mismatch", "source_id": record.source_id,
                "expected_parent_digest": previous, "actual_parent_digest": record.parent_digest,
            })
        if record.source_id in seen_sources:
            issues.append({"index": index, "code": "duplicate_source_id", "source_id": record.source_id})
        seen_sources.add(record.source_id)
        previous = provenance_digest(record)
    break_indices = sorted({issue["index"] for issue in issues})
    return {
        "valid": not issues, "record_count": len(records), "break_indices": break_indices,
        "issues": issues,
        "duplicate_source_ids": sorted({issue["source_id"] for issue in issues if issue["code"] == "duplicate_source_id"}),
        "scientific_validity_established": False,
    }

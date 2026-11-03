import hashlib
import json
from dataclasses import dataclass


@dataclass(frozen=True)
class ProvenanceRecord:
    source_id: str
    source_type: str
    reference: str
    content_digest: str
    parent_digest: str | None = None


def content_digest(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def provenance_digest(record: ProvenanceRecord) -> str:
    payload = json.dumps(record.__dict__, sort_keys=True, separators=(",", ":"))
    return content_digest(payload)


def verify_chain(records: list[ProvenanceRecord]) -> dict:
    previous = None
    breaks = []
    for index, record in enumerate(records):
        if record.parent_digest != previous and index:
            breaks.append(index)
        previous = provenance_digest(record)
    return {"valid": not breaks, "record_count": len(records), "break_indices": breaks}

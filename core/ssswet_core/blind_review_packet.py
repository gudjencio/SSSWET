"""Deterministic reviewer packet redaction with a separate unblinding key.

The packet preserves evidence identifiers and methods. It does not guarantee
anonymity: source text and unrecognized metadata may still identify contributors.
"""
from __future__ import annotations

from hashlib import sha256
import json


MAX_DOCUMENTS = 100
MAX_PACKET_BYTES = 1_000_000
MAX_DOCUMENT_TEXT = 20_000
DEFAULT_REDACT_FIELDS = (
    "author", "author_name", "author_id", "reviewer", "reviewer_id",
    "campaign_id", "organization", "institution", "affiliation",
    "submitter", "owner",
)


def build_blind_packet(
    case_id: str, documents: list[dict], *, salt: str,
    redact_fields: tuple[str, ...] = DEFAULT_REDACT_FIELDS,
) -> dict:
    if not isinstance(case_id, str) or not case_id.strip() or len(case_id) > 200:
        raise ValueError("case_id is required and limited to 200 characters")
    if not isinstance(salt, str) or len(salt) < 16:
        raise ValueError("salt must contain at least 16 characters")
    if not isinstance(documents, list) or len(documents) > MAX_DOCUMENTS:
        raise ValueError(f"documents must be a list of at most {MAX_DOCUMENTS}")
    if not isinstance(redact_fields, tuple) or any(not isinstance(item, str) or not item.strip() for item in redact_fields):
        raise ValueError("redact_fields must be a tuple of field names")

    mapping = {}
    packet_documents = []
    warnings = []
    for index, document in enumerate(documents):
        if not isinstance(document, dict):
            raise ValueError("every document must be a dictionary")
        encoded = json.dumps(document, ensure_ascii=False, sort_keys=True, default=str)
        if len(encoded.encode("utf-8")) > MAX_DOCUMENT_TEXT:
            raise ValueError(f"document {index} exceeds the text-size limit")
        output = {}
        for key, value in sorted(document.items()):
            if key in redact_fields and value not in (None, ""):
                identity = str(value).strip()
                digest = sha256((salt + "\0" + key + "\0" + identity).encode("utf-8")).hexdigest()[:12]
                pseudonym = f"masked-{digest}"
                mapping.setdefault(key, {})[pseudonym] = identity
                output[key] = pseudonym
            else:
                output[key] = value
        unknown = sorted(
            key for key in document
            if any(token in key.casefold() for token in ("author", "person", "email", "name", "organization", "institution"))
            and key not in redact_fields
        )
        if unknown:
            warnings.append({"document_index": index, "unreviewed_identity_fields": unknown})
        packet_documents.append(output)

    packet = {"format": "ssswet-blind-review-v1", "case_id": case_id.strip(), "documents": packet_documents}
    packet_bytes = json.dumps(packet, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if len(packet_bytes) > MAX_PACKET_BYTES:
        raise ValueError("blind review packet exceeds the 1 MB limit")
    mapping_bytes = json.dumps(mapping, ensure_ascii=False, sort_keys=True).encode("utf-8")
    if len(mapping_bytes) > MAX_PACKET_BYTES:
        raise ValueError("separate unblinding key exceeds the 1 MB limit")
    return {
        "packet": packet,
        "packet_sha256": sha256(packet_bytes).hexdigest(),
        "unblinding_key": mapping,
        "warnings": warnings,
        "document_count": len(packet_documents),
        "packet_bytes": len(packet_bytes),
        "unblinding_key_bytes": len(mapping_bytes),
        "unblinding_key_separate_from_packet": True,
        "complete_anonymity_guaranteed": False,
        "source_identifiers_preserved": True,
    }

"""Deterministic evidence-packet quality gate for independent human review.

Validation checks record structure, traceability and reproducibility metadata.
Passing this gate never establishes scientific validity or authorizes action.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from typing import Any

REQUIRED = ("title", "summary", "source_ids", "method", "limitations")
MAX_PACKET_BYTES = 64_000
MAX_SOURCE_IDS = 200
MAX_SOURCE_RECORDS = 200
MAX_BATCH_SIZE = 500
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/#-]{0,239}$")


def _clean_text(value: Any, field: str, maximum: int) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = " ".join(value.split())
    return cleaned if cleaned and len(cleaned) <= maximum else None


def _canonical_fingerprint(packet: dict) -> str | None:
    """Hash the supplied packet deterministically without computed report fields."""
    try:
        encoded = json.dumps(
            packet, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError):
        return None
    if len(encoded) > MAX_PACKET_BYTES:
        return None
    return hashlib.sha256(encoded).hexdigest()


def validate_packet(packet: dict, *, source_records: list[dict] | None = None) -> dict:
    """Return actionable packet-quality findings; never adjudicate scientific claims."""
    if not isinstance(packet, dict):
        return {
            "valid_for_review": False, "missing": list(REQUIRED),
            "errors": ["packet_must_be_an_object"], "warnings": [],
            "duplicate_sources": False, "scientific_validity_established": False,
            "automatic_adjudication": False,
        }

    errors: list[str] = []
    warnings: list[str] = []
    missing = [key for key in REQUIRED if key not in packet or packet.get(key) in (None, "", [], {})]

    title = _clean_text(packet.get("title"), "title", 240)
    summary = _clean_text(packet.get("summary"), "summary", 8000)
    method = _clean_text(packet.get("method"), "method", 8000)
    limitations = packet.get("limitations")
    if isinstance(limitations, str):
        clean_limitations = _clean_text(limitations, "limitations", 8000)
        limitation_count = 1 if clean_limitations else 0
    elif isinstance(limitations, list):
        clean_limitations = [
            text for item in limitations
            if (text := _clean_text(item, "limitations", 2000)) is not None
        ]
        limitation_count = len(clean_limitations)
        if len(clean_limitations) != len(limitations):
            errors.append("limitations_items_must_be_non_empty_strings")
    else:
        clean_limitations = []
        limitation_count = 0
    for field, value in (("title", title), ("summary", summary), ("method", method)):
        if packet.get(field) not in (None, "") and value is None:
            errors.append(f"{field}_must_be_text_within_length_limit")
    if packet.get("limitations") not in (None, "", [], {}) and limitation_count == 0:
        errors.append("limitations_must_describe_at_least_one_limit")

    source_ids = packet.get("source_ids", [])
    duplicate_sources = False
    if not isinstance(source_ids, list):
        errors.append("source_ids_must_be_a_list")
        source_ids = []
    elif len(source_ids) > MAX_SOURCE_IDS:
        errors.append("source_ids_exceed_limit")
    else:
        normalized_ids = []
        for source_id in source_ids:
            if not isinstance(source_id, str) or not _IDENTIFIER.fullmatch(source_id.strip()):
                errors.append("source_ids_must_be_valid_non_empty_identifiers")
                continue
            normalized_ids.append(source_id.strip())
        duplicate_sources = len(normalized_ids) != len(set(normalized_ids))
        if duplicate_sources:
            errors.append("duplicate_source_ids")
        if len(normalized_ids) != len(source_ids):
            warnings.append("some_source_ids_were_not_usable")
        source_ids = normalized_ids

    if not source_ids and "source_ids" not in missing:
        errors.append("at_least_one_source_id_is_required")

    records = source_records if source_records is not None else packet.get("source_records")
    source_record_ids: set[str] = set()
    provenance_groups: set[str] = set()
    source_record_errors: list[str] = []
    if records is None:
        warnings.append("source_records_not_supplied_source_identity_not_independently_checked")
    elif not isinstance(records, list):
        errors.append("source_records_must_be_a_list")
    elif len(records) > MAX_SOURCE_RECORDS:
        errors.append("source_records_exceed_limit")
    else:
        for index, record in enumerate(records):
            if not isinstance(record, dict):
                source_record_errors.append(f"source_record_{index}_must_be_an_object")
                continue
            source_id = record.get("source_id")
            group = record.get("provenance_group")
            if not isinstance(source_id, str) or not _IDENTIFIER.fullmatch(source_id.strip()):
                source_record_errors.append(f"source_record_{index}_has_invalid_source_id")
                continue
            source_id = source_id.strip()
            if source_id in source_record_ids:
                source_record_errors.append(f"duplicate_source_record:{source_id}")
            source_record_ids.add(source_id)
            if isinstance(group, str) and group.strip():
                provenance_groups.add(group.strip())
        errors.extend(source_record_errors)
        unmatched = sorted(set(source_ids) - source_record_ids)
        if unmatched:
            errors.append("source_ids_without_matching_source_records")
        unreferenced = sorted(source_record_ids - set(source_ids))
        if unreferenced:
            warnings.append("unreferenced_source_records_present")

    protocol_id = packet.get("protocol_id")
    dataset_ids = packet.get("dataset_ids", [])
    run_ids = packet.get("run_ids", [])
    reproducibility = {
        "protocol_linked": isinstance(protocol_id, str) and bool(protocol_id.strip()),
        "datasets_linked": isinstance(dataset_ids, list) and bool(dataset_ids),
        "runs_linked": isinstance(run_ids, list) and bool(run_ids),
        "method_described": method is not None,
        "limitations_recorded": limitation_count > 0,
    }
    for field, value in (("dataset_ids", dataset_ids), ("run_ids", run_ids)):
        if not isinstance(value, list):
            errors.append(f"{field}_must_be_a_list")
            reproducibility["datasets_linked" if field == "dataset_ids" else "runs_linked"] = False
        elif len(value) > 200 or any(
            not isinstance(item, str) or not _IDENTIFIER.fullmatch(item.strip())
            for item in value
        ):
            errors.append(f"{field}_contains_invalid_identifiers_or_exceeds_limit")
            reproducibility["datasets_linked" if field == "dataset_ids" else "runs_linked"] = False
    if not reproducibility["protocol_linked"]:
        warnings.append("protocol_not_linked")
    if not reproducibility["datasets_linked"]:
        warnings.append("datasets_not_linked")
    if not reproducibility["runs_linked"]:
        warnings.append("runs_not_linked")

    fingerprint = _canonical_fingerprint(packet)
    if fingerprint is None:
        errors.append("packet_is_not_json_serializable_or_exceeds_64kb")
    byte_size = None
    try:
        byte_size = len(json.dumps(packet, ensure_ascii=False, allow_nan=False).encode("utf-8"))
    except (TypeError, ValueError):
        pass
    if byte_size is not None and byte_size > MAX_PACKET_BYTES:
        if "packet_is_not_json_serializable_or_exceeds_64kb" not in errors:
            errors.append("packet_exceeds_64kb")

    review_checklist = [
        {"item": "source_traceability", "ready": bool(source_ids) and not source_record_errors and (records is None or set(source_ids) <= source_record_ids)},
        {"item": "method_transparency", "ready": reproducibility["method_described"]},
        {"item": "limitations", "ready": reproducibility["limitations_recorded"]},
        {"item": "reproducibility_links", "ready": all((reproducibility["protocol_linked"], reproducibility["datasets_linked"], reproducibility["runs_linked"]))},
    ]
    valid = not missing and not errors and not duplicate_sources
    return {
        "valid_for_review": valid,
        "missing": missing,
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
        "duplicate_sources": duplicate_sources,
        "source_count": len(source_ids),
        "source_record_count": len(source_record_ids),
        "independent_provenance_group_count": len(provenance_groups),
        "provenance_groups_are_metadata_not_proof_of_independence": True,
        "reproducibility": reproducibility,
        "review_checklist": review_checklist,
        "review_readiness_count": sum(item["ready"] for item in review_checklist),
        "review_readiness_total": len(review_checklist),
        "packet_bytes": byte_size,
        "packet_fingerprint_sha256": fingerprint,
        "fingerprint_scope": "exact supplied packet content; changes when any supplied field changes",
        "scientific_validity_established": False,
        "automatic_adjudication": False,
    }


def validate_packets(packets: list[dict], *, max_packets: int = MAX_BATCH_SIZE) -> dict:
    """Validate a bounded batch and report duplicate packet IDs and aggregate blockers."""
    if not isinstance(packets, list):
        raise ValueError("packets must be a list")
    if isinstance(max_packets, bool) or not isinstance(max_packets, int) or not 1 <= max_packets <= MAX_BATCH_SIZE:
        raise ValueError("max_packets must be between 1 and 500")
    if len(packets) > max_packets:
        raise ValueError("packet batch exceeds configured limit")
    reports = [validate_packet(packet) for packet in packets]
    ids = [
        packet.get("packet_id") for packet in packets
        if isinstance(packet, dict) and isinstance(packet.get("packet_id"), str) and packet.get("packet_id").strip()
    ]
    duplicate_ids = sorted(key for key, count in Counter(ids).items() if count > 1)
    return {
        "reports": reports,
        "packet_count": len(reports),
        "valid_for_review_count": sum(report["valid_for_review"] for report in reports),
        "blocked_count": sum(not report["valid_for_review"] for report in reports),
        "duplicate_packet_ids": duplicate_ids,
        "batch_valid_for_review": all(report["valid_for_review"] for report in reports) and not duplicate_ids,
        "bounded_batch": True,
        "scientific_validity_established": False,
        "automatic_adjudication": False,
    }

"""Validate evidence-packet structure and reference resolution before review."""
from __future__ import annotations
REQUIRED = ("title", "summary", "source_ids", "method", "limitations")
TEXT_FIELDS = ("title", "summary", "method", "limitations")

def validate_packet(packet: dict, *, known_source_ids: set[str] | None = None) -> dict:
    if not isinstance(packet, dict):
        raise TypeError("packet must be a mapping")
    missing = [key for key in REQUIRED if key not in packet or packet.get(key) is None or packet.get(key) == "" or packet.get(key) == []]
    blockers: list[str] = []
    warnings: list[str] = []
    for field in TEXT_FIELDS:
        if field in packet and not isinstance(packet[field], str):
            blockers.append(f"{field}:must_be_text")
        elif field in packet and not packet[field].strip() and field not in missing:
            missing.append(field)
    sources = packet.get("source_ids", [])
    duplicate_sources = False
    unresolved_sources: list[str] = []
    if not isinstance(sources, list):
        blockers.append("source_ids:must_be_a_list")
        if "source_ids:list" not in missing:
            missing.append("source_ids:list")
        sources = []
    else:
        invalid_values = [value for value in sources if not isinstance(value, str) or not value.strip()]
        if invalid_values:
            blockers.append("source_ids:contains_invalid_identifier")
        valid_sources = [value for value in sources if isinstance(value, str) and value.strip()]
        duplicate_sources = len(valid_sources) != len(set(valid_sources))
        if duplicate_sources:
            blockers.append("source_ids:contains_duplicates")
        if not valid_sources and "source_ids" not in missing:
            missing.append("source_ids")
        if known_source_ids is not None:
            unresolved_sources = sorted(set(valid_sources) - set(known_source_ids))
            if unresolved_sources:
                blockers.append("source_ids:unresolved_references")
    if isinstance(sources, list) and len([value for value in sources if isinstance(value, str) and value.strip()]) == 1:
        warnings.append("Only one source is listed; independent corroboration is not demonstrated.")
    groups = packet.get("source_independence_groups")
    if groups is not None:
        if not isinstance(groups, list) or any(not isinstance(item, str) or not item.strip() for item in groups):
            blockers.append("source_independence_groups:invalid")
        elif len(set(groups)) < 2:
            warnings.append("Fewer than two declared source-independence groups are present.")
    return {
        "valid_for_review": not missing and not blockers, "missing": missing,
        "duplicate_sources": duplicate_sources, "review_blockers": blockers, "warnings": warnings,
        "unresolved_source_ids": unresolved_sources,
        "source_link_status": "not_checked" if known_source_ids is None else ("unresolved" if unresolved_sources else "resolved"),
        "scientific_validity_established": False,
    }

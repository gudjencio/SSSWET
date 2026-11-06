"""Detect identifier, group, exact-content and declared temporal split leakage."""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import re


def _normalise_content(value: str) -> str:
    return " ".join(value.casefold().split())


def _parse_timestamp(value: object, split_name: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"timestamp_field must be a non-empty ISO-8601 string in {split_name}")
    raw = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError as exc:
        raise ValueError(f"invalid ISO-8601 timestamp in {split_name}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def inspect(
    splits: dict[str, list[dict]],
    id_field: str = "id",
    max_records: int = 1_000_000,
    *,
    group_field: str | None = None,
    timestamp_field: str | None = None,
    temporal_order: list[str] | tuple[str, ...] | None = None,
    content_field: str | None = None,
) -> dict:
    """Audit declared split boundaries; semantic near-duplicate leakage is out of scope."""
    if not isinstance(splits, dict) or len(splits) < 2:
        raise ValueError("at least two named splits are required")
    if not isinstance(id_field, str) or not id_field.strip():
        raise ValueError("id_field is required")
    if isinstance(max_records, bool) or not isinstance(max_records, int) or max_records < 1:
        raise ValueError("max_records must be a positive integer")
    for optional in (group_field, timestamp_field, content_field):
        if optional is not None and (not isinstance(optional, str) or not optional.strip()):
            raise ValueError("optional field names must be non-empty strings")

    seen_ids: dict[str, list[str]] = {}
    seen_groups: dict[str, list[str]] = {}
    seen_content: dict[str, list[str]] = {}
    ranges: dict[str, tuple[datetime, datetime]] = {}
    total = 0

    for split_name in sorted(splits):
        records = splits[split_name]
        if not isinstance(split_name, str) or not split_name or not isinstance(records, list):
            raise ValueError("split names and record lists must be valid")
        total += len(records)
        if total > max_records:
            raise ValueError("split records exceed the configured limit")
        local_ids = set()
        times = []
        for record in records:
            if not isinstance(record, dict) or id_field not in record:
                raise ValueError(f"every record must contain {id_field}")
            value = record[id_field]
            if not isinstance(value, (str, int)) or isinstance(value, bool) or str(value).strip() == "":
                raise ValueError("split identifiers must be non-empty strings or integers")
            normalized = str(value).strip()
            if normalized in local_ids:
                raise ValueError(f"duplicate identifier within split {split_name}")
            local_ids.add(normalized)
            seen_ids.setdefault(normalized, []).append(split_name)

            if group_field:
                if group_field not in record:
                    raise ValueError(f"every record must contain {group_field}")
                group = record[group_field]
                if not isinstance(group, (str, int)) or isinstance(group, bool) or str(group).strip() == "":
                    raise ValueError("group identifiers must be non-empty strings or integers")
                seen_groups.setdefault(str(group).strip(), []).append(split_name)

            if content_field:
                if content_field not in record or not isinstance(record[content_field], str):
                    raise ValueError(f"every record must contain string field {content_field}")
                normalized_content = _normalise_content(record[content_field])
                if normalized_content:
                    digest = sha256(normalized_content.encode("utf-8")).hexdigest()
                    seen_content.setdefault(digest, []).append(split_name)

            if timestamp_field:
                if timestamp_field not in record:
                    raise ValueError(f"every record must contain {timestamp_field}")
                times.append(_parse_timestamp(record[timestamp_field], split_name))
        if times:
            ranges[split_name] = (min(times), max(times))

    def overlaps(index: dict[str, list[str]]) -> list[dict]:
        return [
            {"value": key, "splits": sorted(set(names))}
            for key, names in sorted(index.items())
            if len(set(names)) > 1
        ]

    identifier_overlaps = overlaps(seen_ids)
    group_overlaps = overlaps(seen_groups) if group_field else []
    content_overlaps = overlaps(seen_content) if content_field else []

    temporal_violations = []
    if temporal_order is not None:
        if not isinstance(temporal_order, (list, tuple)) or len(temporal_order) < 2:
            raise ValueError("temporal_order must contain at least two split names")
        order = list(temporal_order)
        if len(set(order)) != len(order) or any(name not in splits for name in order):
            raise ValueError("temporal_order must contain unique existing split names")
        if not timestamp_field:
            raise ValueError("timestamp_field is required when temporal_order is supplied")
        for earlier, later in zip(order, order[1:]):
            if earlier not in ranges or later not in ranges:
                continue
            earlier_end = ranges[earlier][1]
            later_start = ranges[later][0]
            if earlier_end > later_start:
                temporal_violations.append({
                    "earlier_split": earlier,
                    "later_split": later,
                    "earlier_max": earlier_end.isoformat(),
                    "later_min": later_start.isoformat(),
                })

    leakage = bool(identifier_overlaps or group_overlaps or content_overlaps or temporal_violations)
    return {
        "split_count": len(splits),
        "record_count": total,
        "overlap_count": len(identifier_overlaps),
        "overlaps": identifier_overlaps,
        "identifier_overlap_count": len(identifier_overlaps),
        "group_overlap_count": len(group_overlaps),
        "group_overlaps": group_overlaps,
        "exact_content_overlap_count": len(content_overlaps),
        "exact_content_overlaps": content_overlaps,
        "temporal_order_violation_count": len(temporal_violations),
        "temporal_order_violations": temporal_violations,
        "leakage_detected": leakage,
        "scope": "identifier, declared group, normalized exact-content and optional temporal-order overlap; semantic or near-duplicate leakage is not assessed",
    }

"""Explicit publication-age and capture-order diagnostics for research evidence."""
from __future__ import annotations
from datetime import timedelta
from .assurance_common import aware_datetime, identifier

MAX_RECORDS = 1000


def audit_temporal_window(records: list[dict], *, now: str, maximum_age_days: float, future_tolerance_minutes: int = 5) -> dict:
    if not isinstance(records, list) or len(records) > MAX_RECORDS:
        raise ValueError(f"records must contain at most {MAX_RECORDS} items")
    if isinstance(maximum_age_days, bool) or not isinstance(maximum_age_days, (int, float)) or maximum_age_days < 0 or maximum_age_days > 36500:
        raise ValueError("maximum_age_days must be between 0 and 36500")
    if isinstance(future_tolerance_minutes, bool) or not isinstance(future_tolerance_minutes, int) or not 0 <= future_tolerance_minutes <= 1440:
        raise ValueError("future_tolerance_minutes must be between 0 and 1440")
    instant = aware_datetime(now, "now")
    rows, seen = [], set()
    for item in records:
        if not isinstance(item, dict):
            raise ValueError("each record must be an object")
        source_id = identifier(item.get("source_id"), "source_id")
        if source_id in seen:
            raise ValueError("source_id values must be unique")
        seen.add(source_id)
        published_raw = item.get("published_at")
        captured_raw = item.get("captured_at")
        published = aware_datetime(published_raw, "published_at") if published_raw else None
        captured = aware_datetime(captured_raw, "captured_at") if captured_raw else None
        flags = []
        age_days = None
        if published is None:
            status = "unknown_publication_time"
            flags.append("publication_timestamp_missing")
        else:
            delta = instant - published
            age_days = delta.total_seconds() / 86400
            if published > instant + timedelta(minutes=future_tolerance_minutes):
                status = "future_dated"
                flags.append("publication_timestamp_in_future")
            elif age_days > maximum_age_days:
                status = "older_than_window"
                flags.append("outside_requested_age_window")
            else:
                status = "within_window"
        if captured is None:
            flags.append("capture_timestamp_missing")
        elif published is not None and captured + timedelta(minutes=1) < published:
            flags.append("capture_precedes_publication")
        rows.append({"source_id": source_id, "status": status, "age_days": round(age_days, 6) if age_days is not None else None, "published_at": published.isoformat() if published else None, "captured_at": captured.isoformat() if captured else None, "flags": flags, "record_retained": True})
    counts = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    return {"record_count": len(rows), "maximum_age_days": float(maximum_age_days), "status_counts": dict(sorted(counts.items())), "records": sorted(rows, key=lambda row: row["source_id"]), "recency_is_reliability": False, "records_discarded": 0}

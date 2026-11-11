"""Policy-based evidence applicability checks with no implicit scientific expiry."""
from __future__ import annotations

from datetime import date, datetime, time, timezone

MAX_RECORDS = 5000


def _parse(value, field, *, allow_date=True):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty ISO date or timestamp")
    raw = value.strip()
    try:
        if allow_date and len(raw) == 10:
            return datetime.combine(date.fromisoformat(raw), time.min, tzinfo=timezone.utc)
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be a valid ISO date or timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{field} timestamp must include a timezone")
    return parsed.astimezone(timezone.utc)


def assess_record(record: dict, *, as_of: str) -> dict:
    if not isinstance(record, dict):
        raise ValueError("record must be an object")
    now = _parse(as_of, "as_of", allow_date=False)
    source_id = record.get("source_id")
    if not isinstance(source_id, str) or not source_id.strip():
        raise ValueError("source_id is required")
    observed = _parse(record["observed_at"], "observed_at") if record.get("observed_at") else None
    start = _parse(record["valid_from"], "valid_from") if record.get("valid_from") else None
    end = _parse(record["valid_until"], "valid_until") if record.get("valid_until") else None
    interval = record.get("review_after_days")
    if interval is not None and (
        isinstance(interval, bool) or not isinstance(interval, int) or not 1 <= interval <= 36500
    ):
        raise ValueError("review_after_days must be an integer from 1 to 36500")
    if start and end and start > end:
        raise ValueError("valid_from must not be later than valid_until")
    if observed and observed > now:
        status, reason = "future_dated_review", "observed_at is later than the requested assessment time"
    elif start and now < start:
        status, reason = "not_yet_valid", "assessment time precedes the declared validity window"
    elif end and now > end:
        status, reason = "outside_declared_window", "assessment time follows the declared validity window"
    elif observed is None:
        status, reason = "undated", "no observation or publication date was supplied"
    elif interval is not None and (now - observed).total_seconds() > interval * 86400:
        status, reason = "review_due", "the explicitly declared review interval has elapsed"
    elif interval is None and end is None:
        status, reason = "no_expiry_policy", "no explicit review interval or validity end was supplied"
    else:
        status, reason = "within_declared_window", "record falls within its supplied applicability policy"
    return {
        "source_id": source_id.strip(), "status": status, "reason": reason,
        "assessed_at": now.isoformat(), "observed_at": observed.isoformat() if observed else None,
        "valid_from": start.isoformat() if start else None,
        "valid_until": end.isoformat() if end else None,
        "review_after_days": interval, "source_claim_modified": False,
        "automatic_expiry": False, "scientific_validity_established": False,
    }


def assess_records(records: list[dict], *, as_of: str) -> dict:
    if not isinstance(records, list) or len(records) > MAX_RECORDS:
        raise ValueError(f"records must be a list of at most {MAX_RECORDS} items")
    reports = [assess_record(item, as_of=as_of) for item in records]
    counts = {}
    for report in reports:
        counts[report["status"]] = counts.get(report["status"], 0) + 1
    return {
        "reports": reports, "record_count": len(reports),
        "status_counts": dict(sorted(counts.items())),
        "automatic_source_exclusion": False, "scientific_validity_established": False,
    }

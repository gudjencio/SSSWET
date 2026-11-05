"""Deterministic evidence-age assessments that never auto-exclude sources."""
from __future__ import annotations

from datetime import date, datetime, timezone
from math import exp, isfinite


DEFAULT_HALF_LIVES = {
    "preprint": 180.0,
    "guideline": 365.0,
    "dataset": 730.0,
    "software": 180.0,
    "measurement": 90.0,
    "default": 365.0,
}


def _positive_finite(value: float, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a finite number")
    number = float(value)
    if not isfinite(number) or number <= 0:
        raise ValueError(f"{field} must be positive and finite")
    return number


def score(age_days: float, half_life_days: float = 30.0) -> float:
    if isinstance(age_days, bool) or not isinstance(age_days, (int, float)):
        raise ValueError("age_days must be a finite non-negative number")
    age = float(age_days)
    if not isfinite(age) or age < 0:
        raise ValueError("age_days must be a finite non-negative number")
    half_life = _positive_finite(half_life_days, "half_life_days")
    return exp(-0.6931471805599453 * age / half_life)


def _parse_datetime(value: str | date | datetime) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, date):
        parsed = datetime(value.year, value.month, value.day, tzinfo=timezone.utc)
    elif isinstance(value, str) and value.strip():
        raw = value.strip().replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(raw)
        except ValueError:
            try:
                parsed_date = date.fromisoformat(raw)
                parsed = datetime(parsed_date.year, parsed_date.month, parsed_date.day, tzinfo=timezone.utc)
            except ValueError as exc:
                raise ValueError("evidence date must be ISO-8601") from exc
    else:
        raise ValueError("evidence date is required")
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def assess(record: dict, *, as_of: str | date | datetime,
           half_life_days: float | None = None) -> dict:
    """Classify evidence freshness while preserving unknown and future dates."""
    if not isinstance(record, dict):
        raise ValueError("record must be a dictionary")
    source_type = str(record.get("source_type") or "default").strip().casefold()
    half_life = _positive_finite(
        half_life_days if half_life_days is not None else DEFAULT_HALF_LIVES.get(source_type, DEFAULT_HALF_LIVES["default"]),
        "half_life_days",
    )
    date_field = next(
        (field for field in ("observed_at", "published_at", "updated_at", "created_at")
         if record.get(field) not in (None, "")),
        None,
    )
    base = {
        "source_id": str(record.get("id") or record.get("source_id") or ""),
        "source_type": source_type,
        "half_life_days": half_life,
        "date_field": date_field,
        "auto_excluded": False,
        "scientific_validity_established": False,
    }
    if date_field is None:
        return {**base, "age_days": None, "freshness_score": None,
                "status": "unknown_date", "review_required": True}
    observed = _parse_datetime(record[date_field])
    reference = _parse_datetime(as_of)
    age_days = (reference - observed).total_seconds() / 86400.0
    if age_days < 0:
        return {**base, "age_days": age_days, "freshness_score": None,
                "status": "future_dated", "review_required": True}
    freshness = score(age_days, half_life)
    status = "fresh" if age_days <= half_life else ("aging" if age_days <= 2 * half_life else "stale")
    return {**base, "age_days": age_days, "freshness_score": freshness,
            "status": status, "review_required": status == "stale"}

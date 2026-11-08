"""Audit metrology calibration records without asserting instrument certification."""
from __future__ import annotations

from datetime import datetime, timezone
from math import isfinite
import re

MAX_RECORDS = 500
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _date(value: object, label: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be an ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{label} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{label} must include a timezone")
    return parsed.astimezone(timezone.utc)


def assess_calibration(record: dict, *, at: str, max_uncertainty: float | None = None) -> dict:
    if not isinstance(record, dict):
        raise ValueError("record must be an object")
    instrument = record.get("instrument_id")
    calibration_id = record.get("calibration_id")
    if not isinstance(instrument, str) or not instrument.strip() or len(instrument) > 200:
        raise ValueError("instrument_id is required")
    if not isinstance(calibration_id, str) or not calibration_id.strip() or len(calibration_id) > 200:
        raise ValueError("calibration_id is required")
    start, end, instant = _date(record.get("valid_from"), "valid_from"), _date(record.get("valid_until"), "valid_until"), _date(at, "at")
    if end < start:
        raise ValueError("valid_until must not precede valid_from")
    digest = record.get("certificate_sha256")
    if not isinstance(digest, str) or not _SHA256.fullmatch(digest.lower()):
        raise ValueError("certificate_sha256 must be a 64-character hexadecimal digest")
    provider = record.get("calibration_provider")
    if not isinstance(provider, str) or not provider.strip() or len(provider) > 200:
        raise ValueError("calibration_provider is required")
    traceability = record.get("traceability_refs", [])
    if not isinstance(traceability, list) or len(traceability) > 50 or any(not isinstance(ref, str) or not ref.strip() or len(ref) > 300 for ref in traceability):
        raise ValueError("traceability_refs must contain at most 50 non-empty identifiers")
    uncertainty = record.get("expanded_uncertainty")
    if isinstance(uncertainty, bool) or not isinstance(uncertainty, (int, float)) or not isfinite(uncertainty) or uncertainty < 0:
        raise ValueError("expanded_uncertainty must be a non-negative number")
    unit = record.get("uncertainty_unit")
    if not isinstance(unit, str) or not unit.strip() or len(unit) > 40:
        raise ValueError("uncertainty_unit is required")
    review_state = record.get("review_state", "pending")
    if review_state not in {"reviewed", "pending", "rejected"}:
        raise ValueError("review_state must be reviewed, pending or rejected")
    reviewer = record.get("reviewer")
    reviewed_at = record.get("reviewed_at")
    if review_state in {"reviewed", "rejected"}:
        if not isinstance(reviewer, str) or not reviewer.strip() or len(reviewer) > 200:
            raise ValueError("reviewed or rejected calibration records require a reviewer")
        reviewed_at = _date(reviewed_at, "reviewed_at").isoformat()
    elif reviewer is not None and (not isinstance(reviewer, str) or len(reviewer) > 200):
        raise ValueError("reviewer must be a string of at most 200 characters")
    reasons = []
    if not start <= instant <= end:
        reasons.append("outside_validity_window")
    if review_state != "reviewed":
        reasons.append(f"review_state_{review_state}")
    if not traceability:
        reasons.append("traceability_references_missing")
    if max_uncertainty is not None:
        if isinstance(max_uncertainty, bool) or not isinstance(max_uncertainty, (int, float)) or not isfinite(max_uncertainty) or max_uncertainty < 0:
            raise ValueError("max_uncertainty must be a non-negative number")
        if uncertainty > max_uncertainty:
            reasons.append("uncertainty_above_requested_limit")
    return {
        "instrument_id": instrument,
        "calibration_id": calibration_id,
        "metadata_complete_for_review": not reasons,
        "reasons": reasons,
        "certificate_sha256": digest.lower(),
        "calibration_provider": provider,
        "valid_from": start.isoformat(),
        "valid_until": end.isoformat(),
        "expanded_uncertainty": float(uncertainty),
        "uncertainty_unit": unit,
        "traceability_refs": list(traceability),
        "review_state": review_state,
        "reviewer": reviewer,
        "reviewed_at": reviewed_at,
        "certificate_content_verified": False,
        "instrument_certification_claimed": False,
    }


def audit_registry(records: list[dict], *, at: str) -> dict:
    if not isinstance(records, list) or len(records) > MAX_RECORDS:
        raise ValueError(f"records must be a list of at most {MAX_RECORDS} items")
    seen = set()
    results = []
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("each calibration record must be an object")
        instrument = record.get("instrument_id")
        if instrument in seen:
            raise ValueError("each instrument_id may appear only once in a registry audit")
        seen.add(instrument)
        results.append(assess_calibration(record, at=at))
    return {
        "record_count": len(results),
        "metadata_complete_count": sum(item["metadata_complete_for_review"] for item in results),
        "requires_attention": [item for item in results if not item["metadata_complete_for_review"]],
        "results": results,
        "review_is_not_certification": True,
    }

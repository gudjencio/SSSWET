"""Field-level calibration summaries from explicit human source audits."""
from __future__ import annotations

from collections import defaultdict
from math import isfinite
from typing import Any

MAX_AUDITS = 20_000
MAX_GROUPS = 5_000


def _identifier(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > 160:
        raise ValueError(f"{field} must contain 1 to 160 characters")
    return value.strip()


def _wilson(correct: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    proportion = correct / total
    denominator = 1 + z * z / total
    center = (proportion + z * z / (2 * total)) / denominator
    margin = z * ((proportion * (1 - proportion) / total + z * z / (4 * total * total)) ** 0.5) / denominator
    return max(0.0, center - margin), min(1.0, center + margin)


def summarize_source_audits(records: list[dict[str, Any]], *, minimum_sample: int = 5) -> dict[str, Any]:
    """Report observed audit agreement by source/domain/field, not source trust."""
    if not isinstance(records, list) or len(records) > MAX_AUDITS:
        raise ValueError(f"records must be a list of at most {MAX_AUDITS} audits")
    if isinstance(minimum_sample, bool) or not isinstance(minimum_sample, int) or not 1 <= minimum_sample <= 1_000:
        raise ValueError("minimum_sample must be between 1 and 1000")
    groups = defaultdict(list)
    audit_ids = set()
    for item in records:
        if not isinstance(item, dict):
            raise ValueError("every audit must be an object")
        audit_id = _identifier(item.get("audit_id"), "audit_id")
        if audit_id in audit_ids:
            raise ValueError("audit_id values must be unique")
        audit_ids.add(audit_id)
        source = _identifier(item.get("source_id"), "source_id")
        domain = _identifier(item.get("domain"), "domain")
        field = _identifier(item.get("field"), "field")
        correct = item.get("observed_correct")
        if not isinstance(correct, bool):
            raise ValueError("observed_correct must be an explicit boolean audit outcome")
        groups[(source, domain, field)].append(correct)
    if len(groups) > MAX_GROUPS:
        raise ValueError(f"group count exceeds {MAX_GROUPS}")

    summaries = []
    for (source, domain, field), outcomes in sorted(groups.items()):
        total, correct_count = len(outcomes), sum(outcomes)
        enough = total >= minimum_sample
        interval = _wilson(correct_count, total) if enough else None
        summaries.append({
            "source_id": source, "domain": domain, "field": field,
            "audited_count": total, "observed_correct_count": correct_count,
            "observed_agreement_rate": correct_count / total if enough else None,
            "wilson_95_interval": list(interval) if interval else None,
            "status": "sample_sufficient_for_descriptive_interval" if enough else "insufficient_sample",
        })
    return {
        "groups": summaries, "audit_count": len(records), "group_count": len(summaries),
        "minimum_sample": minimum_sample,
        "method": "Wilson score interval for explicit human-audited binary outcomes",
        "composite_trust_score": None,
        "popularity_used_as_evidence": False,
        "scientific_validity_established": False,
    }

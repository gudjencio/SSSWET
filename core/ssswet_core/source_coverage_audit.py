"""Post-ingestion source coverage and concentration diagnostics with caller-defined quotas."""
from __future__ import annotations

from collections import Counter
import math
from urllib.parse import urlsplit
from .assurance_common import identifier, text

SCHEMA_VERSION = 1
MAX_RECORDS = 5000
MAX_TARGETS = 100
MAX_RECOMMENDATIONS = 100
DIMENSIONS = {"platform", "language", "domain", "region", "topic"}
UNKNOWN = "__unknown__"


def _normalize(dimension: str, value: str | None) -> str:
    if value is None:
        return UNKNOWN
    if not isinstance(value, str):
        raise ValueError(f"{dimension} must be text when supplied")
    if not value.strip():
        return UNKNOWN
    raw = text(value, dimension, 300).casefold()
    if dimension == "language":
        return raw.replace("_", "-").split("-")[0]
    if dimension == "domain":
        candidate = raw if "://" in raw else "//" + raw
        host = urlsplit(candidate).hostname or raw
        return host.rstrip(".").removeprefix("www.")
    return raw


def audit_source_coverage(records: list[dict], *, target_quotas: list[dict] | None = None, max_recommendations: int = 50) -> dict:
    if not isinstance(records, list) or len(records) > MAX_RECORDS:
        raise ValueError(f"records must contain at most {MAX_RECORDS} items")
    if isinstance(max_recommendations, bool) or not isinstance(max_recommendations, int) or not 1 <= max_recommendations <= MAX_RECOMMENDATIONS:
        raise ValueError(f"max_recommendations must be between 1 and {MAX_RECOMMENDATIONS}")
    quotas = [] if target_quotas is None else target_quotas
    if not isinstance(quotas, list) or len(quotas) > MAX_TARGETS:
        raise ValueError(f"target_quotas must contain at most {MAX_TARGETS} items")
    seen = set()
    counts = {dimension: Counter() for dimension in DIMENSIONS}
    for item in records:
        if not isinstance(item, dict):
            raise ValueError("each source record must be an object")
        source_id = identifier(item.get("source_id"), "source_id")
        if source_id in seen:
            raise ValueError("source_id values must be unique")
        seen.add(source_id)
        for dimension in DIMENSIONS:
            value = _normalize(dimension, item.get(dimension))
            counts[dimension][value] += 1
    summaries = {}
    for dimension in sorted(DIMENSIONS):
        distribution = counts[dimension]
        n = len(records)
        shares = [count / n for count in distribution.values()] if n else []
        hhi = sum(share * share for share in shares) if shares else None
        entropy = -sum(share * math.log(share) for share in shares if share > 0) if shares else None
        normalized_entropy = entropy / math.log(len(shares)) if len(shares) > 1 else (0.0 if shares else None)
        summaries[dimension] = {
            "group_count": len(distribution),
            "unknown_count": distribution.get(UNKNOWN, 0),
            "hhi_concentration": round(hhi, 6) if hhi is not None else None,
            "normalized_shannon_entropy": round(normalized_entropy, 6) if normalized_entropy is not None else None,
            "distribution": [{"value": value, "count": count, "share": round(count / n, 6) if n else None} for value, count in sorted(distribution.items())],
        }
    target_gaps, seen_targets = [], set()
    for target in quotas:
        if not isinstance(target, dict) or set(target) != {"dimension", "value", "minimum_count"}:
            raise ValueError("each target quota must contain dimension, value and minimum_count only")
        dimension = target["dimension"]
        if not isinstance(dimension, str) or dimension not in DIMENSIONS:
            raise ValueError("target quota has an unsupported dimension")
        value = _normalize(dimension, target["value"])
        minimum = target["minimum_count"]
        if isinstance(minimum, bool) or not isinstance(minimum, int) or not 0 <= minimum <= MAX_RECORDS:
            raise ValueError("minimum_count must be between 0 and the record limit")
        key = (dimension, value)
        if key in seen_targets:
            raise ValueError("target quota dimension/value pairs must be unique")
        seen_targets.add(key)
        observed = counts[dimension].get(value, 0)
        target_gaps.append({"dimension": dimension, "value": value, "observed_count": observed, "minimum_count": minimum, "deficit": max(0, minimum - observed), "coverage_ratio": round(min(1.0, observed / minimum), 6) if minimum else 1.0})
    target_gaps.sort(key=lambda row: (-row["deficit"], row["dimension"], row["value"]))
    recommendations = [row for row in target_gaps if row["deficit"] > 0][:max_recommendations]
    return {
        "schema_version": SCHEMA_VERSION,
        "source_count": len(records),
        "dimension_summaries": summaries,
        "target_gaps": target_gaps,
        "sampling_recommendations": recommendations,
        "recommendations_are_cross_dimension_quota_slots_not_unique_record_counts": True,
        "source_quality_inferred": False,
        "scientific_independence_established": False,
        "sources_deleted_or_filtered": False,
        "crawler_or_collection_authorized": False,
    }

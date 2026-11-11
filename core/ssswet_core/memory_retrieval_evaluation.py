"""Deterministic retrieval evaluation for relevance, provenance and contradiction recall."""
from __future__ import annotations

from math import ceil, isfinite
from statistics import median

MAX_QUERIES = 500
MAX_RESULTS = 500


def _ratio(numerator, denominator):
    return numerator / denominator if denominator else 0.0


def _percentile(values, fraction):
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, ceil(len(ordered) * fraction) - 1))
    return ordered[index]


def evaluate_retrieval(queries: list[dict], *, top_k: int = 10,
                       provenance_groups: dict[str, str] | None = None,
                       storage_bytes: int | None = None) -> dict:
    if not isinstance(queries, list) or len(queries) > MAX_QUERIES:
        raise ValueError(f"queries must be a list of at most {MAX_QUERIES}")
    if not isinstance(top_k, int) or isinstance(top_k, bool) or not 1 <= top_k <= MAX_RESULTS:
        raise ValueError(f"top_k must be between 1 and {MAX_RESULTS}")
    groups = provenance_groups or {}
    if not isinstance(groups, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in groups.items()):
        raise ValueError("provenance_groups must map string IDs to string group IDs")
    if storage_bytes is not None and (
        isinstance(storage_bytes, bool) or not isinstance(storage_bytes, int) or storage_bytes < 0
    ):
        raise ValueError("storage_bytes must be a non-negative integer or null")

    reports, latencies = [], []
    for index, query in enumerate(queries):
        if not isinstance(query, dict):
            raise ValueError(f"query {index} must be an object")
        relevant = query.get("relevant_ids")
        retrieved = query.get("retrieved_ids")
        if not isinstance(relevant, list) or not isinstance(retrieved, list):
            raise ValueError("relevant_ids and retrieved_ids must be lists")
        if len(relevant) > MAX_RESULTS or len(retrieved) > MAX_RESULTS:
            raise ValueError("relevance and retrieval lists exceed the configured limit")
        if any(not isinstance(item, str) or not item for item in relevant + retrieved):
            raise ValueError("retrieval identifiers must be non-empty strings")
        if len(retrieved) != len(set(retrieved)):
            raise ValueError("retrieved_ids must not contain duplicates")
        if len(relevant) != len(set(relevant)):
            raise ValueError("relevant_ids must not contain duplicates")
        latency = query.get("latency_ms")
        if latency is not None and (
            isinstance(latency, bool) or not isinstance(latency, (int, float))
            or not isfinite(float(latency)) or latency < 0
        ):
            raise ValueError("latency_ms must be finite and non-negative")
        if latency is not None:
            latencies.append(float(latency))
        selected = retrieved[:top_k]
        hits = set(selected) & set(relevant)
        relevant_groups = {groups[item] for item in relevant if item in groups}
        retrieved_groups = {groups[item] for item in selected if item in groups}
        contradictory = query.get("contradictory_ids", [])
        if not isinstance(contradictory, list) or any(not isinstance(item, str) for item in contradictory):
            raise ValueError("contradictory_ids must be a list of strings")
        known_contradictory = set(contradictory) & set(relevant)
        reports.append({
            "query_id": str(query.get("query_id", index)),
            "retrieved_count_at_k": len(selected), "relevant_count": len(relevant),
            "hits_at_k": len(hits), "precision_at_k": _ratio(len(hits), top_k),
            "recall_at_k": _ratio(len(hits), len(relevant)),
            "reciprocal_rank": next((1 / rank for rank, item in enumerate(selected, 1) if item in set(relevant)), 0.0),
            "provenance_group_recall_at_k": _ratio(len(relevant_groups & retrieved_groups), len(relevant_groups)) if relevant_groups else None,
            "contradiction_retention_at_k": _ratio(len(known_contradictory & set(selected)), len(known_contradictory)) if known_contradictory else None,
            "latency_ms": float(latency) if latency is not None else None,
        })
    metric_names = ("precision_at_k", "recall_at_k", "reciprocal_rank")
    aggregate = {
        name: sum(item[name] for item in reports) / len(reports) if reports else None
        for name in metric_names
    }
    for name in ("provenance_group_recall_at_k", "contradiction_retention_at_k"):
        values = [item[name] for item in reports if item[name] is not None]
        aggregate[name] = sum(values) / len(values) if values else None
    return {
        "query_count": len(reports), "top_k": top_k, "per_query": reports,
        "aggregate": aggregate,
        "latency_ms": {
            "sample_count": len(latencies),
            "median": median(latencies) if latencies else None,
            "p95": _percentile(latencies, 0.95),
            "percentile_method": "nearest_rank",
        },
        "storage_bytes": storage_bytes,
        "deterministic_for_identical_inputs": True,
        "retrieval_quality_is_not_model_intelligence": True,
        "scientific_validity_established": False,
    }

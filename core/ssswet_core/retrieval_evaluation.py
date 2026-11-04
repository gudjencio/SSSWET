"""Deterministic ranking metrics for evaluating research-memory retrieval."""
from __future__ import annotations
import math
from collections.abc import Callable, Iterable, Mapping, Sequence
from statistics import median
from time import perf_counter

def evaluate_retrieval(rankings: Mapping[str, Sequence[str]],
                       relevance: Mapping[str, set[str] | list[str] | tuple[str, ...]], *, k: int = 5) -> dict:
    """Return MRR@k, precision@k, recall@k and nDCG@k for labelled queries."""
    if isinstance(k, bool) or not isinstance(k, int) or k < 1:
        raise ValueError("k must be a positive integer")
    if not isinstance(rankings, Mapping) or not isinstance(relevance, Mapping):
        raise TypeError("rankings and relevance must be mappings")
    query_ids = sorted(set(rankings) | set(relevance))
    per_query = []
    for query_id in query_ids:
        expected_values = relevance.get(query_id, ())
        if isinstance(expected_values, (str, bytes)) or not isinstance(expected_values, Iterable):
            raise TypeError(f"relevance for {query_id} must be a collection of identifiers")
        expected = set()
        for item in expected_values:
            if not isinstance(item, str) or not item:
                raise ValueError("relevant item identifiers must be non-empty strings")
            expected.add(item)
        ranked_values = rankings.get(query_id, ())
        if isinstance(ranked_values, (str, bytes)) or not isinstance(ranked_values, Sequence):
            raise TypeError(f"ranking for {query_id} must be a sequence")
        ranked = []
        seen = set()
        for item in ranked_values:
            if not isinstance(item, str) or not item:
                raise ValueError("ranked item identifiers must be non-empty strings")
            if item not in seen:
                ranked.append(item)
                seen.add(item)
        top = ranked[:k]
        hits = [index for index, item in enumerate(top, start=1) if item in expected]
        reciprocal_rank = 1.0 / hits[0] if hits else 0.0
        recall = len(hits) / len(expected) if expected else 0.0
        precision = len(hits) / k
        dcg = sum(1.0 / math.log2(rank + 1) for rank, item in enumerate(top, start=1) if item in expected)
        ideal_hits = min(len(expected), k)
        ideal_dcg = sum(1.0 / math.log2(rank + 1) for rank in range(1, ideal_hits + 1))
        ndcg = dcg / ideal_dcg if ideal_dcg else 0.0
        per_query.append({
            "query_id": query_id, "relevant_count": len(expected), "returned_count": len(top),
            "hits_at_k": len(hits), "mrr_at_k": reciprocal_rank, "precision_at_k": precision,
            "recall_at_k": recall, "ndcg_at_k": ndcg,
        })
    evaluated = [item for item in per_query if item["relevant_count"]]
    denominator = len(evaluated) or 1
    return {
        "k": k, "query_count": len(query_ids), "evaluated_query_count": len(evaluated),
        "mrr_at_k": round(sum(item["mrr_at_k"] for item in evaluated) / denominator, 6),
        "mean_precision_at_k": round(sum(item["precision_at_k"] for item in evaluated) / denominator, 6),
        "mean_recall_at_k": round(sum(item["recall_at_k"] for item in evaluated) / denominator, 6),
        "mean_ndcg_at_k": round(sum(item["ndcg_at_k"] for item in evaluated) / denominator, 6),
        "per_query": per_query, "metrics_are_retrieval_quality_not_scientific_validity": True,
    }

def compare_retrieval_evaluations(before: dict, after: dict) -> dict:
    """Compare two metric reports using identical cut-offs and query counts."""
    if before.get("k") != after.get("k"):
        raise ValueError("retrieval reports must use the same k")
    if before.get("evaluated_query_count") != after.get("evaluated_query_count"):
        raise ValueError("retrieval reports must cover the same number of labelled queries")
    before_ids = sorted(item["query_id"] for item in before.get("per_query", []))
    after_ids = sorted(item["query_id"] for item in after.get("per_query", []))
    if before_ids != after_ids:
        raise ValueError("retrieval reports must cover the same labelled query IDs")
    metrics = ("mrr_at_k", "mean_precision_at_k", "mean_recall_at_k", "mean_ndcg_at_k")
    deltas = {name: round(float(after.get(name, 0.0)) - float(before.get(name, 0.0)), 6) for name in metrics}
    return {
        "before": {name: before.get(name, 0.0) for name in metrics},
        "after": {name: after.get(name, 0.0) for name in metrics},
        "deltas": deltas, "non_regression_on_recall": deltas["mean_recall_at_k"] >= 0,
        "comparison_is_scientific_validation": False,
    }


def benchmark_retrieval(search_callable: Callable, *args, repeats: int = 5, **kwargs) -> dict:
    """Measure repeated search latency without imposing a machine-specific threshold."""
    if not callable(search_callable):
        raise TypeError("search_callable must be callable")
    if isinstance(repeats, bool) or not isinstance(repeats, int) or not 1 <= repeats <= 100:
        raise ValueError("repeats must be between 1 and 100")
    durations = []
    result_count = 0
    for _ in range(repeats):
        started = perf_counter()
        results = search_callable(*args, **kwargs)
        durations.append((perf_counter() - started) * 1000.0)
        result_count = len(results) if hasattr(results, "__len__") else 0
    ordered = sorted(durations)
    p95_index = min(len(ordered) - 1, math.ceil(0.95 * len(ordered)) - 1)
    return {
        "repeats": repeats,
        "result_count": result_count,
        "median_ms": round(median(ordered), 4),
        "p95_ms": round(ordered[p95_index], 4),
        "minimum_ms": round(ordered[0], 4),
        "maximum_ms": round(ordered[-1], 4),
        "timing_is_environment_dependent": True,
    }

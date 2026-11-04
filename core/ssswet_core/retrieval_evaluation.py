"""Deterministic ranking metrics for evaluating research-memory retrieval."""
from __future__ import annotations
import math
from collections.abc import Mapping, Sequence

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
        expected = set(relevance.get(query_id, ()))
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
    metrics = ("mrr_at_k", "mean_precision_at_k", "mean_recall_at_k", "mean_ndcg_at_k")
    deltas = {name: round(float(after.get(name, 0.0)) - float(before.get(name, 0.0)), 6) for name in metrics}
    return {
        "before": {name: before.get(name, 0.0) for name in metrics},
        "after": {name: after.get(name, 0.0) for name in metrics},
        "deltas": deltas, "non_regression_on_recall": deltas["mean_recall_at_k"] >= 0,
        "comparison_is_scientific_validation": False,
    }

"""Bounded, provenance-preserving scientific-memory retrieval and evaluation.

Ranking is a navigation aid, not a truth or quality score. Source references are
returned unchanged and contested records are never silently filtered out.
"""
from __future__ import annotations
from collections import Counter
from math import log
from statistics import median
from time import perf_counter_ns
import re

MAX_RECORDS = 500
MAX_RESULTS = 100
MAX_EVALUATION_CASES = 200
FIELD_WEIGHTS = {"statement": 4.0, "topic": 2.5, "summary": 1.5, "tags": 1.25}
_TOKEN = re.compile(r"[\w']{2,}", re.UNICODE)
_PROVENANCE_FIELDS = ("source_ids", "experiment_ids", "graph_node_ids", "evidence_refs", "review_refs")

def _tokens(value: str) -> list[str]:
    return [token.casefold() for token in _TOKEN.findall(value)]

def _identifier(record: dict, index: int) -> str:
    for field in ("version_id", "memory_id", "id"):
        value = record.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise ValueError(f"record {index} must include version_id, memory_id or id")

def rank_memories(records: list[dict], query: str, *, limit: int = 20) -> dict:
    """Rank at most 500 records deterministically and retain all declared refs."""
    if not isinstance(records, list) or len(records) > MAX_RECORDS:
        raise ValueError(f"records must be a list of at most {MAX_RECORDS} items")
    if not isinstance(query, str) or not query.strip() or len(query) > 1000:
        raise ValueError("query must contain 1 to 1000 characters")
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= MAX_RESULTS:
        raise ValueError(f"limit must be between 1 and {MAX_RESULTS}")
    terms = _tokens(query)
    if not terms:
        raise ValueError("query must contain at least one searchable token")
    prepared, identifiers, document_frequency = [], set(), Counter()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError("every memory record must be an object")
        identifier = _identifier(record, index)
        if identifier in identifiers:
            raise ValueError(f"duplicate memory identifier: {identifier}")
        identifiers.add(identifier)
        fields, document_terms = {}, set()
        for field in FIELD_WEIGHTS:
            value = record.get(field, "")
            if field == "tags" and isinstance(value, list):
                value = " ".join(item for item in value if isinstance(item, str))
            if not isinstance(value, str):
                value = ""
            field_terms = _tokens(value)
            fields[field] = (value, field_terms)
            document_terms.update(field_terms)
        document_frequency.update(document_terms)
        prepared.append((identifier, record, fields))
    total = max(1, len(prepared))
    ranked, normalized_query = [], " ".join(query.casefold().split())
    for identifier, record, fields in prepared:
        score, matched_fields = 0.0, []
        for field, weight in FIELD_WEIGHTS.items():
            value, field_terms = fields[field]
            if not field_terms:
                continue
            counts, field_score = Counter(field_terms), 0.0
            for term in set(terms):
                frequency = counts.get(term, 0)
                if frequency:
                    inverse_frequency = log(1.0 + (total - document_frequency[term] + 0.5) / (document_frequency[term] + 0.5))
                    field_score += inverse_frequency * (1.0 + log(frequency))
            if field_score:
                score += weight * field_score / (1.0 + 0.15 * log(1 + len(field_terms)))
                matched_fields.append(field)
            if normalized_query and normalized_query in " ".join(value.casefold().split()):
                score += weight * 1.5
        if score <= 0:
            continue
        provenance = {}
        for field in _PROVENANCE_FIELDS:
            values = record.get(field, [])
            if values is None:
                values = []
            if not isinstance(values, (list, tuple)) or any(not isinstance(item, str) or not item.strip() for item in values):
                raise ValueError(f"{field} must contain non-empty strings")
            provenance[field] = list(dict.fromkeys(values))
        ranked.append({
            "memory_id": identifier, "topic": record.get("topic", ""),
            "statement": record.get("statement", ""),
            "status": record.get("status", record.get("review_state", "unreviewed")),
            "score": round(score, 8), "matched_fields": matched_fields,
            "provenance": provenance,
            "contested": bool(record.get("contested", False) or record.get("contested_by_graph", False)),
        })
    ranked.sort(key=lambda item: (-item["score"], item["memory_id"]))
    return {
        "query": query, "results": ranked[:limit], "records_examined": len(prepared),
        "records_matched": len(ranked), "bounded": True,
        "deterministic_tie_break": "memory_id ascending",
        "contested_records_suppressed": False, "scientific_validity_established": False,
    }

def evaluate_retrieval(cases: list[dict], *, k: int = 10) -> dict:
    """Calculate macro precision/recall/F1, MRR and binary nDCG@k."""
    if not isinstance(cases, list) or not 1 <= len(cases) <= MAX_EVALUATION_CASES:
        raise ValueError(f"cases must contain 1 to {MAX_EVALUATION_CASES} items")
    if isinstance(k, bool) or not isinstance(k, int) or not 1 <= k <= MAX_RESULTS:
        raise ValueError("k must be between 1 and 100")
    metrics, seen = [], set()
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("each evaluation case must be an object")
        case_id, relevant, retrieved = case.get("case_id"), case.get("relevant_ids"), case.get("retrieved_ids")
        if not isinstance(case_id, str) or not case_id.strip() or case_id in seen:
            raise ValueError("case_id values must be unique non-empty strings")
        seen.add(case_id)
        if not isinstance(relevant, list) or not relevant or any(not isinstance(x, str) or not x for x in relevant):
            raise ValueError("relevant_ids must be a non-empty list of strings")
        if len(set(relevant)) != len(relevant):
            raise ValueError("relevant_ids must not contain duplicates")
        if not isinstance(retrieved, list) or any(not isinstance(x, str) or not x for x in retrieved):
            raise ValueError("retrieved_ids must be a list of strings")
        if len(set(retrieved)) != len(retrieved):
            raise ValueError("retrieved_ids must not contain duplicates")
        expected, top = set(relevant), retrieved[:k]
        hits = sum(item in expected for item in top)
        precision, recall = hits / k, hits / len(expected)
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        reciprocal_rank = next((1.0 / index for index, item in enumerate(top, 1) if item in expected), 0.0)
        dcg = sum(1.0 / log(index + 1, 2) for index, item in enumerate(top, 1) if item in expected)
        ideal_hits = min(len(expected), k)
        idcg = sum(1.0 / log(index + 1, 2) for index in range(1, ideal_hits + 1))
        metrics.append({"case_id": case_id, "precision_at_k": precision, "recall_at_k": recall,
                        "f1_at_k": f1, "reciprocal_rank": reciprocal_rank,
                        "ndcg_at_k": dcg / idcg if idcg else 0.0})
    keys = ("precision_at_k", "recall_at_k", "f1_at_k", "reciprocal_rank", "ndcg_at_k")
    aggregate = {key: round(sum(item[key] for item in metrics) / len(metrics), 6) for key in keys}
    return {"k": k, "case_count": len(metrics), "macro_metrics": aggregate, "cases": metrics,
            "synthetic_or_labelled_fixture_only": True, "intelligence_claim": False}

def benchmark_retrieval(records: list[dict], queries: list[str], *, repeats: int = 5, limit: int = 20) -> dict:
    if not isinstance(queries, list) or not 1 <= len(queries) <= 100:
        raise ValueError("queries must contain 1 to 100 strings")
    if isinstance(repeats, bool) or not isinstance(repeats, int) or not 1 <= repeats <= 20:
        raise ValueError("repeats must be between 1 and 20")
    durations, rankings_by_query = [], {query: [] for query in queries}
    for _ in range(repeats):
        for query in queries:
            started = perf_counter_ns()
            result = rank_memories(records, query, limit=limit)
            durations.append((perf_counter_ns() - started) / 1_000_000)
            rankings_by_query[query].append([item["memory_id"] for item in result["results"]])
    ordered = sorted(durations)
    p95_index = min(len(ordered) - 1, max(0, int(0.95 * len(ordered) + 0.999999) - 1))
    return {
        "record_count": len(records), "query_count": len(queries), "repeats": repeats,
        "median_latency_ms": round(median(ordered), 4), "p95_latency_ms": round(ordered[p95_index], 4),
        "stable_rankings": all(all(ranking == rankings[0] for ranking in rankings) for rankings in rankings_by_query.values()),
        "network_and_database_latency_included": False, "benchmark_is_environment_specific": True,
    }

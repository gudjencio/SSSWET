"""Bounded, explainable scientific-memory retrieval and review utilities.

These helpers organize research records; they do not verify scientific claims.
All operations are read-only and retain explicit source, experiment and graph links.
"""
from __future__ import annotations

import hashlib
import heapq
import hmac
import json
import math
import re
import time
from statistics import median
from typing import Iterable

MAX_MEMORY_RECORDS = 500
MAX_SEARCH_RESULTS = 100
_TOKEN_RE = re.compile(r"[\w']{2,}", re.UNICODE)


def _tokens(value: object) -> set[str]:
    return {item.casefold() for item in _TOKEN_RE.findall(str(value or ""))}


def _validate_records(records: list[dict], maximum: int = MAX_MEMORY_RECORDS) -> None:
    if not isinstance(records, list):
        raise ValueError("records must be a list")
    if len(records) > maximum:
        raise ValueError(f"records exceeds the {maximum}-record limit")
    if any(not isinstance(item, dict) for item in records):
        raise ValueError("every record must be an object")


def _current_version_ids(records: list[dict]) -> set[str]:
    if any("is_current" in item for item in records):
        return {
            str(item.get("version_id", ""))
            for item in records if item.get("is_current") is True
        }
    latest: dict[str, tuple[tuple, str]] = {}
    for item in records:
        key = str(item.get("memory_key", ""))
        version_id = str(item.get("version_id", ""))
        order = (
            int(item.get("version_number", 0) or 0),
            str(item.get("created_at", "")),
            version_id,
        )
        if key and (key not in latest or order > latest[key][0]):
            latest[key] = (order, version_id)
    return {value[1] for value in latest.values()}


def search_scientific_memory(
    records: list[dict],
    query: str,
    *,
    limit: int = 20,
    include_history: bool = False,
) -> dict:
    """Rank at most 500 records using transparent topic/statement/campaign weights."""
    _validate_records(records)
    if not isinstance(query, str) or not query.strip() or len(query) > 500:
        raise ValueError("query must contain 1 to 500 characters")
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= MAX_SEARCH_RESULTS:
        raise ValueError("limit must be between 1 and 100")
    if not isinstance(include_history, bool):
        raise ValueError("include_history must be a boolean")
    terms = _tokens(query)
    if not terms:
        raise ValueError("query must contain at least one searchable term")

    current_ids = _current_version_ids(records)
    phrase = " ".join(query.casefold().split())
    denominator = 5.5 * len(terms) + 1.5
    ranked = []
    for record in records:
        version_id = str(record.get("version_id", ""))
        is_current = version_id in current_ids
        if not include_history and not is_current:
            continue
        topic = str(record.get("topic", ""))
        statement = str(record.get("statement", ""))
        campaign = str(record.get("campaign_id", ""))
        topic_hits = terms & _tokens(topic)
        statement_hits = terms & _tokens(statement)
        campaign_hits = terms & _tokens(campaign)
        matched = topic_hits | statement_hits | campaign_hits
        if not matched:
            continue
        phrase_topic = bool(phrase and phrase in " ".join(topic.casefold().split()))
        phrase_statement = bool(phrase and phrase in " ".join(statement.casefold().split()))
        phrase_bonus = 1.5 if phrase_topic or phrase_statement else 0.0
        weighted = 3.0 * len(topic_hits) + 2.0 * len(statement_hits) + 0.5 * len(campaign_hits)
        score = min(1.0, (weighted + phrase_bonus) / denominator)
        item = dict(record)
        item.update({
            "matched_terms": sorted(matched),
            "retrieval_score": round(score, 6),
            "score_components": {
                "topic_matches": len(topic_hits),
                "statement_matches": len(statement_hits),
                "campaign_matches": len(campaign_hits),
                "exact_phrase_bonus": phrase_bonus,
            },
            "retrieval_method": "weighted_fielded_lexical_v1",
            "is_current": is_current,
            "ranking_score_is_probability": False,
            "scientific_validity_established": False,
        })
        ranked.append(item)

    ranked.sort(key=lambda item: (
        -item["retrieval_score"],
        -int(bool(item.get("is_current"))),
        str(item.get("created_at", "")),
        str(item.get("version_id", "")),
    ))
    return {
        "query": query,
        "results": ranked[:limit],
        "result_count": min(len(ranked), limit),
        "total_matches": len(ranked),
        "retrieval_method": "weighted_fielded_lexical_v1",
        "include_history": include_history,
        "ranking_score_is_probability": False,
        "contested_records_are_retained": True,
        "scientific_validity_established": False,
    }


def evaluate_retrieval(ranked_ids: Iterable[str], relevant_ids: Iterable[str], *, k: int = 10) -> dict:
    """Calculate deterministic binary-relevance metrics for a ranked result list."""
    if isinstance(k, bool) or not isinstance(k, int) or not 1 <= k <= 100:
        raise ValueError("k must be between 1 and 100")
    ranked = list(dict.fromkeys(str(item) for item in ranked_ids))
    relevant = {str(item) for item in relevant_ids}
    if not relevant:
        raise ValueError("relevant_ids must not be empty")
    top = ranked[:k]
    hits = [item for item in top if item in relevant]
    reciprocal_rank = next((1.0 / (index + 1) for index, item in enumerate(top) if item in relevant), 0.0)
    dcg = sum(1.0 / math.log2(index + 2) for index, item in enumerate(top) if item in relevant)
    ideal_count = min(len(relevant), k)
    ideal_dcg = sum(1.0 / math.log2(index + 2) for index in range(ideal_count))
    precision = len(hits) / k
    recall = len(hits) / len(relevant)
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "k": k,
        "precision_at_k": round(precision, 6),
        "recall_at_k": round(recall, 6),
        "f1_at_k": round(f1, 6),
        "mrr": round(reciprocal_rank, 6),
        "ndcg_at_k": round(dcg / ideal_dcg if ideal_dcg else 0.0, 6),
        "relevant_count": len(relevant),
        "retrieved_count": len(top),
        "relevant_hits": len(hits),
    }


def compare_retrieval_cases(cases: list[dict], *, k: int = 10) -> dict:
    """Compare candidate and baseline rankings over a small, labelled benchmark."""
    if not isinstance(cases, list) or not cases or len(cases) > 100:
        raise ValueError("cases must contain between 1 and 100 benchmark cases")
    candidate, baseline = [], []
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("each benchmark case must be an object")
        relevant = case.get("relevant_ids", [])
        candidate.append(evaluate_retrieval(case.get("candidate_ids", []), relevant, k=k))
        baseline.append(evaluate_retrieval(case.get("baseline_ids", []), relevant, k=k))

    def average(items: list[dict], key: str) -> float:
        return round(sum(item[key] for item in items) / len(items), 6)

    metrics = ("precision_at_k", "recall_at_k", "f1_at_k", "mrr", "ndcg_at_k")
    candidate_avg = {key: average(candidate, key) for key in metrics}
    baseline_avg = {key: average(baseline, key) for key in metrics}
    return {
        "case_count": len(cases),
        "k": k,
        "candidate": candidate_avg,
        "baseline": baseline_avg,
        "delta": {key: round(candidate_avg[key] - baseline_avg[key], 6) for key in metrics},
        "benchmark_is_synthetic_unless_sources_are_supplied": True,
        "scientific_validity_established": False,
    }


def benchmark_memory_retrieval(
    records: list[dict],
    queries: list[str],
    *,
    repeats: int = 3,
    limit: int = 20,
) -> dict:
    """Measure bounded in-process retrieval latency; results are not a quality score."""
    _validate_records(records)
    if not isinstance(queries, list) or not 1 <= len(queries) <= 20:
        raise ValueError("queries must contain between 1 and 20 items")
    if isinstance(repeats, bool) or not isinstance(repeats, int) or not 1 <= repeats <= 10:
        raise ValueError("repeats must be between 1 and 10")
    samples = []
    for query in queries:
        for _ in range(repeats):
            started = time.perf_counter()
            search_scientific_memory(records, query, limit=limit)
            samples.append((time.perf_counter() - started) * 1000)
    ordered = sorted(samples)
    p95_index = min(len(ordered) - 1, math.ceil(0.95 * len(ordered)) - 1)
    return {
        "record_count": len(records),
        "query_count": len(queries),
        "repeats": repeats,
        "sample_count": len(samples),
        "median_latency_ms": round(median(samples), 3),
        "p95_latency_ms": round(ordered[p95_index], 3),
        "measurement_scope": "in-process ranking only; excludes database reads and network latency",
    }


def build_agent_context_packet(
    records: list[dict],
    query: str,
    *,
    token_budget: int = 1200,
    max_items: int = 12,
    include_history: bool = False,
) -> dict:
    """Build a bounded, provenance-preserving context packet without asserting truth."""
    if isinstance(token_budget, bool) or not isinstance(token_budget, int) or not 1 <= token_budget <= 8000:
        raise ValueError("token_budget must be between 1 and 8000")
    if isinstance(max_items, bool) or not isinstance(max_items, int) or not 1 <= max_items <= 50:
        raise ValueError("max_items must be between 1 and 50")
    search = search_scientific_memory(
        records, query, limit=max_items, include_history=include_history
    )
    selected = []
    used = 0
    omitted = 0
    for item in search["results"]:
        context_item = {
            key: item.get(key)
            for key in (
                "version_id", "memory_key", "version_number", "topic", "statement",
                "status", "created_at", "source_ids", "experiment_ids",
                "graph_node_ids", "provenance_group", "is_current",
                "contested_by_graph", "contested_graph_node_ids", "missing_links",
                "has_missing_links", "matched_terms", "retrieval_score",
            )
            if key in item
        }
        cost = max(1, math.ceil(len(json.dumps(context_item, ensure_ascii=False, sort_keys=True)) / 4))
        if used + cost > token_budget:
            omitted += 1
            continue
        selected.append(context_item)
        used += cost
    omitted += max(0, search["total_matches"] - len(search["results"]))
    return {
        "query": query,
        "records": selected,
        "record_count": len(selected),
        "omitted_count": omitted,
        "token_budget": token_budget,
        "estimated_tokens": used,
        "budget_utilization": round(used / token_budget, 6),
        "token_estimate_method": "UTF-8 JSON character count divided by four; approximate, not model-tokenized",
        "provenance_retained": True,
        "contested_records_suppressed": False,
        "context_note": "Retrieved research records are not automatically verified facts. Check source methods, dates, units, limitations and review status before relying on them.",
        "scientific_validity_established": False,
    }


def audit_memory_integrity(
    records: list[dict],
    source_records: list[dict],
    experiment_records: list[dict],
    graph: dict,
) -> dict:
    """Audit resolvability and declared provenance without inferring independence."""
    _validate_records(records)
    if len(source_records) > 5000 or len(experiment_records) > 5000:
        raise ValueError("source and experiment inputs must not exceed 5000 records")
    source_map = {str(item.get("source_id")): item for item in source_records if item.get("source_id")}
    experiment_ids = {str(item.get("experiment_id")) for item in experiment_records if item.get("experiment_id")}
    graph_nodes = graph.get("nodes", []) if isinstance(graph, dict) else []
    graph_ids = {str(item.get("node_id")) for item in graph_nodes if item.get("node_id")}
    audited = []
    totals = {"source_ids": 0, "experiment_ids": 0, "graph_node_ids": 0}
    missing_versions = 0
    for record in records:
        source_ids = sorted(set(map(str, record.get("source_ids", []))))
        experiment_refs = sorted(set(map(str, record.get("experiment_ids", []))))
        graph_refs = sorted(set(map(str, record.get("graph_node_ids", []))))
        missing = {
            "source_ids": [value for value in source_ids if value not in source_map],
            "experiment_ids": [value for value in experiment_refs if value not in experiment_ids],
            "graph_node_ids": [value for value in graph_refs if value not in graph_ids],
        }
        for key in totals:
            totals[key] += len(missing[key])
        if any(missing.values()):
            missing_versions += 1
        linked_sources = [source_map[value] for value in source_ids if value in source_map]
        groups = sorted({str(item.get("provenance_group", "")).strip() for item in linked_sources if str(item.get("provenance_group", "")).strip()})
        ungrouped = sorted(item["source_id"] for item in linked_sources if not str(item.get("provenance_group", "")).strip())
        audited.append({
            "version_id": record.get("version_id", ""),
            "memory_key": record.get("memory_key", ""),
            "missing_links": missing,
            "has_missing_links": any(missing.values()),
            "linked_source_count": len(linked_sources),
            "declared_provenance_group_count": len(groups),
            "declared_provenance_groups": groups,
            "sources_without_provenance_group": ungrouped,
            "independence_established": False,
        })
    return {
        "records_audited": len(audited),
        "versions_with_missing_links": missing_versions,
        "missing_link_counts": totals,
        "records": audited,
        "independence_established": False,
        "scientific_validity_established": False,
        "interpretation": "A resolved identifier confirms only that a local record exists. Declared provenance groups are review signals; absent overlap does not establish source independence.",
    }


def find_duplicate_memory_candidates(
    records: list[dict],
    *,
    threshold: float = 0.82,
    limit: int = 100,
) -> dict:
    """Find exact and near-duplicate current statements; never merge or delete records."""
    _validate_records(records)
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)) or not 0.5 <= threshold <= 1.0:
        raise ValueError("threshold must be between 0.5 and 1.0")
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 200:
        raise ValueError("limit must be between 1 and 200")
    current_ids = _current_version_ids(records)
    current = [item for item in records if str(item.get("version_id", "")) in current_ids]
    prepared = []
    for item in current:
        tokens = _tokens(item.get("statement", ""))
        normalized = " ".join(_TOKEN_RE.findall(str(item.get("statement", "")).casefold()))
        if tokens:
            prepared.append((item, tokens, normalized))
    candidates = []
    candidate_count = 0
    pair_index = 0
    for index, (left, left_tokens, left_normalized) in enumerate(prepared):
        for right, right_tokens, right_normalized in prepared[index + 1:]:
            if left.get("memory_key") == right.get("memory_key"):
                continue
            union = left_tokens | right_tokens
            similarity = len(left_tokens & right_tokens) / len(union) if union else 0.0
            exact = left_normalized == right_normalized
            if not exact and similarity < threshold:
                continue
            left_sources = set(map(str, left.get("source_ids", [])))
            right_sources = set(map(str, right.get("source_ids", [])))
            candidate_count += 1
            candidate = {
                "version_ids": [left.get("version_id", ""), right.get("version_id", "")],
                "memory_keys": [left.get("memory_key", ""), right.get("memory_key", "")],
                "similarity": round(similarity, 6),
                "exact_normalized_match": exact,
                "shared_terms": sorted(left_tokens & right_tokens),
                "shared_source_ids": sorted(left_sources & right_sources),
                "different_source_sets": left_sources != right_sources,
                "provenance_groups": sorted({
                    str(value).strip()
                    for value in (left.get("provenance_group", ""), right.get("provenance_group", ""))
                    if str(value).strip()
                }),
                "review_only": True,
                "automatic_merge": False,
                "automatic_deletion": False,
            }
            priority = (int(exact), similarity, -pair_index)
            pair_index += 1
            entry = (priority, candidate)
            if len(candidates) < limit:
                heapq.heappush(candidates, entry)
            elif priority > candidates[0][0]:
                heapq.heapreplace(candidates, entry)
    retained = [item[1] for item in candidates]
    retained.sort(key=lambda item: (
        -int(item["exact_normalized_match"]),
        -item["similarity"],
        tuple(map(str, item["version_ids"])),
    ))
    return {
        "candidates": retained,
        "candidate_count": candidate_count,
        "current_record_count": len(current),
        "pairwise_comparison_cap": 500,
        "threshold": float(threshold),
        "automatic_merge": False,
        "automatic_deletion": False,
        "scientific_validity_established": False,
    }


def build_memory_conflict_review(records: list[dict], graph: dict, *, limit: int = 100) -> dict:
    """Create human-review cases for current memories linked to contradiction edges."""
    _validate_records(records)
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 200:
        raise ValueError("limit must be between 1 and 200")
    if not isinstance(graph, dict):
        raise ValueError("graph must be an object")
    nodes = {
        str(item.get("node_id")): item
        for item in graph.get("nodes", [])
        if item.get("node_id")
    }
    current_ids = _current_version_ids(records)
    cases = []
    case_count = 0
    sequence = 0
    for record in records:
        if str(record.get("version_id", "")) not in current_ids:
            continue
        linked = set(map(str, record.get("graph_node_ids", [])))
        if not linked:
            continue
        for edge in graph.get("edges", []):
            if edge.get("relation") != "contradicts":
                continue
            source_id, target_id = str(edge.get("source_id", "")), str(edge.get("target_id", ""))
            linked_id = source_id if source_id in linked else target_id if target_id in linked else ""
            if not linked_id:
                continue
            other_id = target_id if linked_id == source_id else source_id
            case_count += 1
            case = {
                "version_id": record.get("version_id", ""),
                "memory_key": record.get("memory_key", ""),
                "topic": record.get("topic", ""),
                "statement": record.get("statement", ""),
                "memory_status": record.get("status", "candidate"),
                "linked_node_id": linked_id,
                "linked_node_label": nodes.get(linked_id, {}).get("label", ""),
                "contradicting_node_id": other_id,
                "contradicting_node_label": nodes.get(other_id, {}).get("label", ""),
                "contradicting_node_exists": other_id in nodes,
                "edge_note": edge.get("note", edge.get("rationale", "")),
                "edge_confidence": edge.get("confidence", 0.0),
                "edge_created_at": edge.get("created_at", ""),
                "memory_created_at": record.get("created_at", ""),
                "review_checklist": [
                    "Compare source provenance and possible shared datasets",
                    "Check units, conditions, methods and measurement dates",
                    "Review uncertainty, limitations and missing data",
                    "Request independent domain review where appropriate",
                ],
                "automatic_status_change": False,
                "automatic_adjudication": False,
            }
            priority = (
                str(case["edge_created_at"] or case["memory_created_at"]),
                str(case["memory_created_at"]),
                str(case["version_id"]),
                sequence,
            )
            sequence += 1
            entry = (priority, case)
            if len(cases) < limit:
                heapq.heappush(cases, entry)
            elif priority > cases[0][0]:
                heapq.heapreplace(cases, entry)
    retained = [item[1] for item in cases]
    retained.sort(key=lambda item: (
        str(item["edge_created_at"] or item["memory_created_at"]),
        str(item["memory_created_at"]),
        str(item["version_id"]),
    ), reverse=True)
    return {
        "cases": retained,
        "case_count": case_count,
        "review_required": bool(cases),
        "automatic_status_change": False,
        "automatic_adjudication": False,
        "scientific_validity_established": False,
    }


def create_memory_snapshot(records: list[dict], *, complete: bool = True) -> dict:
    """Create a deterministic, integrity-checkable snapshot; no import is performed."""
    _validate_records(records)
    if not isinstance(complete, bool):
        raise ValueError("complete must be a boolean")
    normalized = json.loads(json.dumps(records, ensure_ascii=False, sort_keys=True, allow_nan=False))
    normalized.sort(key=lambda item: (
        str(item.get("memory_key", "")),
        int(item.get("version_number", 0) or 0),
        str(item.get("version_id", "")),
    ))
    payload = {
        "format": "ssswet-scientific-memory-snapshot-v1",
        "schema_version": 1,
        "record_count": len(normalized),
        "complete": complete,
        "truncated_possible": not complete,
        "records": normalized,
        "authenticity_established": False,
        "scientific_validity_established": False,
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    payload["digest_algorithm"] = "sha256"
    payload["digest"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return payload


def verify_memory_snapshot(snapshot: dict) -> dict:
    """Verify snapshot structure and checksum; a digest does not authenticate its author."""
    if not isinstance(snapshot, dict):
        raise ValueError("snapshot must be an object")
    required = ("format", "schema_version", "record_count", "complete", "truncated_possible", "records", "authenticity_established", "scientific_validity_established", "digest_algorithm", "digest")
    if any(key not in snapshot for key in required):
        raise ValueError("snapshot is missing required fields")
    if snapshot["format"] != "ssswet-scientific-memory-snapshot-v1" or snapshot["schema_version"] != 1:
        raise ValueError("unsupported snapshot format or schema version")
    if snapshot["digest_algorithm"] != "sha256":
        raise ValueError("unsupported snapshot digest algorithm")
    if not isinstance(snapshot["records"], list) or len(snapshot["records"]) > MAX_MEMORY_RECORDS:
        raise ValueError("snapshot records are invalid or exceed the record limit")
    if snapshot["record_count"] != len(snapshot["records"]):
        raise ValueError("snapshot record_count does not match records")
    payload = {key: value for key, value in snapshot.items() if key not in {"digest_algorithm", "digest"}}
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    expected = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    valid = hmac.compare_digest(str(snapshot["digest"]), expected)
    return {
        "valid": valid,
        "record_count": len(snapshot["records"]),
        "digest_algorithm": "sha256",
        "authenticity_established": False,
        "scientific_validity_established": False,
    }

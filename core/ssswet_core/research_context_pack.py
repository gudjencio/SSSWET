"""Bounded, provenance-preserving context packs for research agents.

The pack is a retrieval aid, not a model-intelligence or scientific-truth score.
It keeps linked contradictions visible and never changes memory or verification state.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

from .scientific_memory import ScientificMemoryService

MAX_MEMORIES = 50
MAX_CONTEXT_CHARS = 50_000
MAX_GRAPH_RECORDS = 2_000
MAX_SOURCES = 200


def _canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _size(value: dict[str, Any]) -> int:
    return len(_canonical(value))


def build_research_context(
    store: Any,
    query: str,
    *,
    limit: int = 20,
    max_chars: int = 16_000,
) -> dict[str, Any]:
    """Build a deterministic context pack with explicit omissions and provenance."""
    if not isinstance(query, str) or not query.strip() or len(query.strip()) > 500:
        raise ValueError("query must contain 1 to 500 characters")
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= MAX_MEMORIES:
        raise ValueError(f"limit must be an integer between 1 and {MAX_MEMORIES}")
    if isinstance(max_chars, bool) or not isinstance(max_chars, int) or not 2_000 <= max_chars <= MAX_CONTEXT_CHARS:
        raise ValueError(f"max_chars must be between 2000 and {MAX_CONTEXT_CHARS}")

    overview = ScientificMemoryService(store).overview(query=query.strip(), limit=500)
    graph = store.knowledge_graph(limit=MAX_GRAPH_RECORDS)
    nodes = {
        item.get("node_id"): item
        for item in graph.get("nodes", [])
        if isinstance(item, dict) and item.get("node_id")
    }
    edges = [
        item for item in graph.get("edges", [])
        if isinstance(item, dict) and item.get("relation") == "contradicts"
    ]
    edges.sort(key=lambda item: (
        str(item.get("created_at", "")),
        str(item.get("source_id", "")),
        str(item.get("target_id", "")),
    ))

    payload: dict[str, Any] = {
        "schema_version": 1,
        "query": query.strip(),
        "retrieval_method": overview.get("retrieval_method", "lexical_overlap"),
        "memories": [],
        "contradictions": [],
        "sources": [],
        "omitted_memory_count": 0,
        "omitted_contradiction_count": 0,
        "omitted_source_count": 0,
        "truncated": False,
        "budget_chars": max_chars,
        "scientific_validity_established": False,
        "automatic_adjudication": False,
        "retrieval_quality_is_not_model_intelligence": True,
    }

    selected = overview.get("versions", [])[:limit]
    effective_budget = max_chars - 160  # reserve space for final counters and digest
    selected_node_ids: set[str] = set()
    selected_source_ids: list[str] = []
    for item in selected:
        memory = {
            "version_id": item.get("version_id", ""),
            "memory_key": item.get("memory_key", ""),
            "version_number": item.get("version_number"),
            "topic": str(item.get("topic", ""))[:240],
            "statement": str(item.get("statement", ""))[:1_200],
            "status": item.get("status", "candidate"),
            "created_at": item.get("created_at", ""),
            "source_ids": list(item.get("source_ids", []))[:20],
            "graph_node_ids": list(item.get("graph_node_ids", []))[:20],
            "missing_links": item.get("missing_links", {}),
            "contested_by_graph": bool(item.get("contested_by_graph")),
            "is_current": bool(item.get("is_current")),
            "scientific_validity_established": False,
        }
        candidate = {**payload, "memories": payload["memories"] + [memory]}
        if _size(candidate) > effective_budget:
            payload["omitted_memory_count"] += len(selected) - len(payload["memories"])
            payload["truncated"] = True
            break
        payload["memories"].append(memory)
        selected_node_ids.update(memory["graph_node_ids"])
        selected_source_ids.extend(memory["source_ids"])

    payload["omitted_memory_count"] = max(0, int(overview.get("total_versions", len(overview.get("versions", [])))) - len(payload["memories"]))

    contradiction_candidates = []
    for edge in edges:
        left, right = edge.get("source_id"), edge.get("target_id")
        if left in selected_node_ids or right in selected_node_ids:
            contradiction_candidates.append({
                "source_id": left,
                "source_label": nodes.get(left, {}).get("label", ""),
                "target_id": right,
                "target_label": nodes.get(right, {}).get("label", ""),
                "note": str(edge.get("note", ""))[:500],
                "recorded_confidence": edge.get("confidence", 0.0),
                "created_at": edge.get("created_at", ""),
                "relation": "contradicts",
                "interpretation": "recorded_disagreement_for_human_review",
            })
    for index, contradiction in enumerate(contradiction_candidates):
        candidate = {**payload, "contradictions": payload["contradictions"] + [contradiction]}
        if _size(candidate) > max_chars:
            payload["omitted_contradiction_count"] = len(contradiction_candidates) - index
            payload["truncated"] = True
            break
        payload["contradictions"].append(contradiction)

    unique_source_ids = list(dict.fromkeys(selected_source_ids))[:MAX_SOURCES]
    for index, source_id in enumerate(unique_source_ids):
        source = store.get_source(source_id)
        if source is None:
            source_record = {"source_id": source_id, "missing_record": True}
        else:
            source_record = {
                "source_id": source_id,
                "title": str(source.get("title", ""))[:300],
                "doi": str(source.get("doi", ""))[:200],
                "url": str(source.get("url", ""))[:500],
                "source_type": str(source.get("source_type", ""))[:80],
                "provenance_group": str(source.get("provenance_group", ""))[:200],
                "recorded_metadata_only": True,
            }
        candidate = {**payload, "sources": payload["sources"] + [source_record]}
        if _size(candidate) > max_chars:
            payload["omitted_source_count"] = len(unique_source_ids) - index
            payload["truncated"] = True
            break
        payload["sources"].append(source_record)

    payload["omitted_source_count"] += max(0, len(selected_source_ids) - len(unique_source_ids))
    unsigned = dict(payload)
    payload["context_sha256"] = hashlib.sha256(_canonical(unsigned).encode("utf-8")).hexdigest()
    payload["used_chars"] = 0
    for _ in range(3):
        measured = len(_canonical(payload))
        if measured == payload["used_chars"]:
            break
        payload["used_chars"] = measured
    if len(_canonical(payload)) > max_chars:
        raise RuntimeError("context budget accounting exceeded max_chars")
    return payload

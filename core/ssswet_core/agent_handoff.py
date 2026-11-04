"""Bounded, provenance-preserving research handoff packets for agent workflows."""
from __future__ import annotations
import json
from collections.abc import Iterable
from .collective_memory import search_collective_memory

def _clean_text(value: str, field: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty text")
    cleaned = value.strip()
    if len(cleaned) > maximum:
        raise ValueError(f"{field} exceeds {maximum} characters")
    return cleaned

def _clean_list(values: Iterable[str], field: str, *, maximum_items: int, maximum_length: int) -> list[str]:
    if isinstance(values, (str, bytes)):
        raise TypeError(f"{field} must be a sequence of strings")
    result = []
    for value in values:
        cleaned = _clean_text(value, field, maximum_length)
        if cleaned not in result:
            result.append(cleaned)
        if len(result) > maximum_items:
            raise ValueError(f"{field} exceeds {maximum_items} entries")
    return result

def build_handoff_packet(task_id: str, objective: str, memories: Iterable[dict], *,
                         required_capabilities: Iterable[str] = (), open_questions: Iterable[str] = (),
                         constraints: Iterable[str] = (), max_memories: int = 8, max_chars: int = 12000) -> dict:
    """Build a deterministic context envelope; it never authorizes execution."""
    task_id = _clean_text(task_id, "task_id", 160)
    objective = _clean_text(objective, "objective", 2000)
    if isinstance(max_memories, bool) or not isinstance(max_memories, int) or not 1 <= max_memories <= 50:
        raise ValueError("max_memories must be between 1 and 50")
    if isinstance(max_chars, bool) or not isinstance(max_chars, int) or not 1000 <= max_chars <= 50000:
        raise ValueError("max_chars must be between 1000 and 50000")
    capabilities = _clean_list(required_capabilities, "required_capabilities", maximum_items=30, maximum_length=120)
    questions = _clean_list(open_questions, "open_questions", maximum_items=50, maximum_length=500)
    guardrails = _clean_list(constraints, "constraints", maximum_items=50, maximum_length=500)
    matches = search_collective_memory(memories, objective, limit=max_memories, include_rejected=True)
    packet = {
        "task_id": task_id, "objective": objective, "required_capabilities": capabilities,
        "open_questions": questions, "constraints": guardrails, "memories": [],
        "source_refs": [], "provenance_groups": [], "memory_records_considered": len(matches),
        "memory_records_omitted": 0, "retrieval_method": "field_weighted_bm25",
        "required_controls": ["human_review_required", "privacy_minimization_required",
                              "safety_ethics_and_legal_review_required"],
        "execution_started": False, "autonomous_execution_authorized": False,
        "scientific_validity_established": False,
    }
    if len(json.dumps(packet, ensure_ascii=False, sort_keys=True)) > max_chars:
        raise ValueError("task context exceeds max_chars before memories are added")
    omitted = 0
    for item in matches:
        sources = item.get("source_ids", []) or []
        if isinstance(sources, str):
            sources = [sources]
        if not isinstance(sources, (list, tuple, set)):
            raise TypeError("memory source_ids must be a collection")
        valid_sources = [source.strip() for source in sources if isinstance(source, str) and source.strip()]
        invalid_source_count = len(sources) - len(valid_sources)
        memory = {
            "memory_id": item.get("memory_id", ""), "topic": item.get("topic", ""),
            "statement": item.get("statement", ""), "status": item.get("status", "candidate"),
            "source_ids": valid_sources, "source_refs_incomplete": bool(invalid_source_count),
            "provenance_group": item.get("provenance_group", ""),
            "review_note": item.get("review_note", ""), "retrieval_score": item.get("retrieval_score", 0.0),
            "matched_terms": item.get("matched_terms", []),
        }
        candidate = dict(packet)
        candidate["memories"] = [*packet["memories"], memory]
        candidate["source_refs"] = sorted(set(packet["source_refs"]) | set(valid_sources))
        group = item.get("provenance_group", "")
        candidate["provenance_groups"] = sorted(set(packet["provenance_groups"]) | ({group} if group else set()))
        candidate["memory_records_omitted"] = omitted
        if len(json.dumps(candidate, ensure_ascii=False, sort_keys=True)) <= max_chars:
            packet = candidate
        else:
            omitted += 1
    packet["memory_records_omitted"] = omitted
    packet["context_characters"] = len(json.dumps(packet, ensure_ascii=False, sort_keys=True))
    if packet["context_characters"] > max_chars:
        raise ValueError("handoff packet could not fit within max_chars")
    return packet

"""Portable, bounded scientific-memory snapshots with provenance-preserving retrieval."""
from __future__ import annotations

import re
import unicodedata
import hashlib
from collections import defaultdict
from .assurance_common import aware_datetime, digest, identifier, sha256_hex, text

SCHEMA_VERSION = 1
MAX_MEMORIES = 1000
MAX_MEMORY_TEXT = 10000
MAX_TOTAL_TEXT = 1_000_000
MAX_REFS_PER_MEMORY = 20
MAX_RETRIEVAL = 50


def _tokens(value: str) -> list[str]:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    words = re.findall(r"[^\W_]+", normalized, flags=re.UNICODE)
    extra = []
    for word in words:
        if any("\u3040" <= ch <= "\u30ff" or "\u3400" <= ch <= "\u9fff" for ch in word):
            extra.extend(word[i:i + 2] for i in range(max(0, len(word) - 1)))
    return list(dict.fromkeys(words + extra))


def build_memory_snapshot(memories: list[dict]) -> dict:
    if not isinstance(memories, list) or len(memories) > MAX_MEMORIES:
        raise ValueError(f"memories must contain at most {MAX_MEMORIES} items")
    normalized, seen, total = [], set(), 0
    content_groups = defaultdict(list)
    for item in memories:
        if not isinstance(item, dict):
            raise ValueError("each memory must be an object")
        memory_id = identifier(item.get("memory_id"), "memory_id")
        if memory_id in seen:
            raise ValueError("memory_id values must be unique")
        seen.add(memory_id)
        body = text(item.get("text"), "memory.text", MAX_MEMORY_TEXT)
        total += len(body.encode("utf-8"))
        if total > MAX_TOTAL_TEXT:
            raise ValueError("total memory text exceeds snapshot budget")
        created = aware_datetime(item.get("created_at"), "memory.created_at").isoformat()
        review_state = item.get("review_state", "unreviewed")
        if review_state not in {"unreviewed", "review_required", "reviewed", "superseded", "withdrawn"}:
            raise ValueError("unsupported memory review_state")
        stance = item.get("stance", "unspecified")
        if stance not in {"supports", "contradicts", "neutral", "unspecified"}:
            raise ValueError("unsupported memory stance")
        refs = item.get("source_refs", [])
        if not isinstance(refs, list) or len(refs) > MAX_REFS_PER_MEMORY:
            raise ValueError(f"source_refs must contain at most {MAX_REFS_PER_MEMORY} items")
        clean_refs = []
        for ref in refs:
            if not isinstance(ref, dict) or set(ref) != {"source_id", "sha256"}:
                raise ValueError("source_refs must contain source_id and sha256 only")
            clean_refs.append({"source_id": identifier(ref["source_id"], "source_id"), "sha256": sha256_hex(ref["sha256"], "source sha256")})
        clean_refs.sort(key=lambda ref: (ref["source_id"], ref["sha256"]))
        tags = item.get("tags", [])
        if not isinstance(tags, list) or len(tags) > 30:
            raise ValueError("tags must contain at most 30 items")
        clean_tags = sorted(set(text(tag, "tag", 80).casefold() for tag in tags))
        body_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
        normalized.append({"memory_id": memory_id, "text": body, "text_sha256": body_hash, "created_at": created, "review_state": review_state, "stance": stance, "source_refs": clean_refs, "tags": clean_tags})
        content_groups[body_hash].append(memory_id)
    normalized.sort(key=lambda item: item["memory_id"])
    groups = [{"text_sha256": key, "memory_ids": sorted(ids), "deduplicated": False} for key, ids in sorted(content_groups.items()) if len(ids) > 1]
    payload = {"schema_version": SCHEMA_VERSION, "memory_count": len(normalized), "source_reference_count": sum(len(item["source_refs"]) for item in normalized), "memories": normalized, "exact_text_match_groups": groups, "memories_deleted_or_merged": False}
    return {**payload, "manifest_sha256": digest(payload)}


def verify_memory_snapshot(snapshot: dict) -> dict:
    if not isinstance(snapshot, dict) or snapshot.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported or malformed memory snapshot")
    payload = {key: value for key, value in snapshot.items() if key != "manifest_sha256"}
    if digest(payload) != sha256_hex(snapshot.get("manifest_sha256"), "manifest_sha256"):
        raise ValueError("memory snapshot digest mismatch")
    if snapshot.get("memory_count") != len(snapshot.get("memories", [])) or len(snapshot.get("memories", [])) > MAX_MEMORIES:
        raise ValueError("memory snapshot count mismatch or capacity exceeded")
    return {"valid": True, "memory_count": snapshot["memory_count"], "source_reference_count": snapshot["source_reference_count"], "contradictory_stances_retained": True, "manifest_sha256": snapshot["manifest_sha256"]}


def retrieve_memory(snapshot: dict, query: str, *, limit: int = 20, review_states: list[str] | None = None) -> dict:
    verify_memory_snapshot(snapshot)
    query_tokens = sorted(set(_tokens(text(query, "query", 2000))))
    if not query_tokens:
        raise ValueError("query must contain at least one searchable token")
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= MAX_RETRIEVAL:
        raise ValueError(f"limit must be between 1 and {MAX_RETRIEVAL}")
    allowed = None
    if review_states is not None:
        if not isinstance(review_states, list) or any(state not in {"unreviewed", "review_required", "reviewed", "superseded", "withdrawn"} for state in review_states):
            raise ValueError("review_states contains an unsupported state")
        allowed = set(review_states)
    rows = []
    for item in snapshot["memories"]:
        if allowed is not None and item["review_state"] not in allowed:
            continue
        present = set(_tokens(item["text"]))
        matched = [token for token in query_tokens if token in present]
        if matched:
            rows.append({"memory": item, "matched_tokens": matched, "score": len(matched) / len(query_tokens)})
    rows.sort(key=lambda row: (-row["score"], row["memory"]["memory_id"]))
    selected = rows[:limit]
    return {"query_token_count": len(query_tokens), "results": selected, "result_count": len(selected), "candidate_count": len(rows), "limit": limit, "ranking": "unique_token_recall_then_memory_id_v1", "semantic_relevance_established": False, "source_provenance_preserved": True}


def compare_memory_snapshots(previous: dict, current: dict) -> dict:
    verify_memory_snapshot(previous)
    verify_memory_snapshot(current)
    old = {item["memory_id"]: item for item in previous["memories"]}
    new = {item["memory_id"]: item for item in current["memories"]}
    added = sorted(new.keys() - old.keys())
    removed = sorted(old.keys() - new.keys())
    changed = sorted(key for key in old.keys() & new.keys() if old[key] != new[key])
    return {"added_memory_ids": added, "absent_from_current_snapshot_ids": removed, "changed_memory_ids": changed, "absence_is_not_retraction": True}

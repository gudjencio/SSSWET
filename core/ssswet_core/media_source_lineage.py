"""Explicit cross-platform repost lineage without inferring source independence."""
from __future__ import annotations
from collections import defaultdict
from .assurance_common import identifier, sha256_hex

MAX_RECORDS = 500
RELATIONS = {"repost", "translation", "quotation", "adaptation", "syndication"}


def analyze_source_lineage(records: list[dict]) -> dict:
    if not isinstance(records, list) or len(records) > MAX_RECORDS:
        raise ValueError(f"records must contain at most {MAX_RECORDS} items")
    by_id, hashes, edges = {}, defaultdict(list), []
    for item in records:
        if not isinstance(item, dict):
            raise ValueError("each source record must be an object")
        source_id = identifier(item.get("source_id"), "source_id")
        if source_id in by_id:
            raise ValueError("source_id values must be unique")
        platform = identifier(item.get("platform"), "platform", 40).lower()
        content_hash = sha256_hex(item.get("content_sha256"), "content_sha256") if item.get("content_sha256") else None
        parent = item.get("parent_source_id")
        relation = item.get("relation_type")
        if parent is None and relation is not None:
            raise ValueError("relation_type requires parent_source_id")
        if parent is not None:
            parent = identifier(parent, "parent_source_id")
            if relation not in RELATIONS:
                raise ValueError("relation_type must be an explicit supported relation")
            edges.append({"source_id": source_id, "parent_source_id": parent, "relation_type": relation, "declared_by_input": True})
        by_id[source_id] = {"source_id": source_id, "platform": platform, "content_sha256": content_hash, "parent_source_id": parent}
        if content_hash:
            hashes[content_hash].append(source_id)
    missing = sorted({edge["parent_source_id"] for edge in edges if edge["parent_source_id"] not in by_id})
    parent_map = {key: value["parent_source_id"] for key, value in by_id.items() if value["parent_source_id"]}
    state, cycles = {}, []
    for start in sorted(by_id):
        if start in state:
            continue
        path, positions, node = [], {}, start
        while node in by_id and node not in state and node not in positions and node in parent_map:
            positions[node] = len(path)
            path.append(node)
            node = parent_map[node]
        if node in positions:
            cycle = path[positions[node]:]
            cycles.append(sorted(cycle))
            for member in cycle:
                state[member] = None
        root = node if node in by_id and node not in positions else None
        for member in reversed(path):
            if member not in state:
                state[member] = root
            root = state[member]
        if start not in state:
            state[start] = start if start not in parent_map else None
    exact_groups = [{"content_sha256": key, "source_ids": sorted(ids), "origin_equivalence_inferred": False} for key, ids in sorted(hashes.items()) if len(ids) > 1]
    return {"source_count": len(records), "declared_lineage_edges": sorted(edges, key=lambda edge: (edge["source_id"], edge["parent_source_id"])), "missing_parent_source_ids": missing, "cycles": sorted(cycles), "root_by_source_id": {key: state.get(key) for key in sorted(by_id)}, "exact_text_match_groups": exact_groups, "sources_deleted_or_merged": False, "scientific_independence_established": False}

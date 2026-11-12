"""Bounded graph-neighbourhood retrieval with contradiction-first traversal."""
from __future__ import annotations

from collections import deque
from typing import Any

MAX_DEPTH = 3
MAX_NODES = 200
MAX_EDGES = 500


def build_neighborhood(
    graph: dict[str, Any],
    seed_ids: list[str],
    *,
    depth: int = 2,
    max_nodes: int = 100,
    max_edges: int = 200,
) -> dict[str, Any]:
    if not isinstance(graph, dict):
        raise ValueError("graph must be an object")
    if not isinstance(seed_ids, list) or not seed_ids or len(seed_ids) > MAX_NODES:
        raise ValueError(f"seed_ids must contain 1 to {MAX_NODES} identifiers")
    if any(not isinstance(item, str) or not item.strip() for item in seed_ids):
        raise ValueError("seed_ids must contain non-empty strings")
    if isinstance(depth, bool) or not isinstance(depth, int) or not 0 <= depth <= MAX_DEPTH:
        raise ValueError(f"depth must be an integer between 0 and {MAX_DEPTH}")
    if isinstance(max_nodes, bool) or not isinstance(max_nodes, int) or not 1 <= max_nodes <= MAX_NODES:
        raise ValueError(f"max_nodes must be between 1 and {MAX_NODES}")
    if isinstance(max_edges, bool) or not isinstance(max_edges, int) or not 1 <= max_edges <= MAX_EDGES:
        raise ValueError(f"max_edges must be between 1 and {MAX_EDGES}")

    raw_nodes = graph.get("nodes", [])
    raw_edges = graph.get("edges", [])
    if not isinstance(raw_nodes, list) or not isinstance(raw_edges, list):
        raise ValueError("graph nodes and edges must be lists")
    nodes = {
        item.get("node_id"): item
        for item in raw_nodes
        if isinstance(item, dict) and isinstance(item.get("node_id"), str)
    }
    edges = [
        item for item in raw_edges
        if isinstance(item, dict)
        and item.get("source_id") in nodes
        and item.get("target_id") in nodes
    ]

    def edge_key(edge):
        return (
            0 if edge.get("relation") == "contradicts" else 1,
            str(edge.get("relation", "")),
            str(edge.get("source_id", "")),
            str(edge.get("target_id", "")),
        )

    edges.sort(key=edge_key)
    adjacency: dict[str, list[tuple[str, dict]]] = {node_id: [] for node_id in nodes}
    for edge in edges:
        left, right = edge["source_id"], edge["target_id"]
        adjacency[left].append((right, edge))
        adjacency[right].append((left, edge))
    for values in adjacency.values():
        values.sort(key=lambda pair: edge_key(pair[1]) + (pair[0],))

    seeds = list(dict.fromkeys(item.strip() for item in seed_ids))
    missing = [item for item in seeds if item not in nodes]
    queue = deque((item, 0) for item in seeds if item in nodes)
    visited: set[str] = set()
    truncated = False
    while queue:
        node_id, current_depth = queue.popleft()
        if node_id in visited:
            continue
        if len(visited) >= max_nodes:
            truncated = True
            break
        visited.add(node_id)
        if current_depth >= depth:
            continue
        for neighbour, edge in adjacency.get(node_id, []):
            if neighbour in visited:
                continue
            if len(visited) + len(queue) >= max_nodes:
                truncated = True
                continue
            queue.append((neighbour, current_depth + 1))

    selected_nodes = [nodes[item] for item in sorted(visited)]
    selected_edges = [
        edge for edge in edges
        if edge["source_id"] in visited and edge["target_id"] in visited
    ]
    selected_edges.sort(key=edge_key)
    omitted_edges = max(0, len(selected_edges) - max_edges)
    selected_edges = selected_edges[:max_edges]
    contradiction_count = sum(1 for item in selected_edges if item.get("relation") == "contradicts")
    return {
        "seed_ids": seeds,
        "missing_seed_ids": missing,
        "depth": depth,
        "nodes": selected_nodes,
        "edges": selected_edges,
        "node_count": len(selected_nodes),
        "edge_count": len(selected_edges),
        "contradiction_edge_count": contradiction_count,
        "omitted_edge_count": omitted_edges,
        "truncated": truncated or bool(omitted_edges),
        "traversal_is_undirected": True,
        "contradictions_preserved_as_recorded": True,
        "scientific_validity_established": False,
        "automatic_adjudication": False,
    }

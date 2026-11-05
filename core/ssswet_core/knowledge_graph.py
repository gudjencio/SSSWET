"""Persistent explicit knowledge graph with bounded evidence-path tracing.

Edges record declared relationships; they are not proof that a claim is true.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone


NODE_TYPES = {
    "hypothesis", "finding", "source", "dataset", "experiment",
    "question", "method", "concept",
}
RELATIONS = {
    "supports", "contradicts", "derived_from", "tests", "uses_dataset",
    "related_to", "answers", "requires_verification",
}


@dataclass(frozen=True)
class KnowledgeNode:
    node_id: str
    node_type: str
    label: str
    description: str = ""
    verification_state: str = "unverified"
    metadata: dict | None = None
    created_at: str = ""


@dataclass(frozen=True)
class KnowledgeEdge:
    source_id: str
    target_id: str
    relation: str
    note: str = ""
    confidence: float = 0.0
    created_at: str = ""


def validate_node(node: KnowledgeNode) -> None:
    if not node.node_id.strip() or not node.label.strip():
        raise ValueError("node_id and label must not be empty")
    if node.node_type not in NODE_TYPES:
        raise ValueError(f"Unsupported node_type: {node.node_type}")
    if not 0.0 <= float(node.metadata.get("confidence", 0.0) if node.metadata else 0.0) <= 1.0:
        raise ValueError("metadata confidence must be between 0 and 1")


def validate_edge(edge: KnowledgeEdge) -> None:
    if not edge.source_id.strip() or not edge.target_id.strip():
        raise ValueError("edge endpoints must not be empty")
    if edge.source_id == edge.target_id:
        raise ValueError("self-referencing edges are not allowed")
    if edge.relation not in RELATIONS:
        raise ValueError(f"Unsupported relation: {edge.relation}")
    if not 0.0 <= float(edge.confidence) <= 1.0:
        raise ValueError("edge confidence must be between 0 and 1")


def trace_paths(
    nodes: list[dict],
    edges: list[dict],
    start_id: str,
    target_id: str,
    *,
    max_depth: int = 6,
    max_paths: int = 20,
    allowed_relations: set[str] | list[str] | tuple[str, ...] | None = None,
    direction: str = "outgoing",
) -> dict:
    """Return bounded simple paths between graph nodes with declared edge labels."""
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise ValueError("nodes and edges must be lists")
    if not isinstance(start_id, str) or not start_id.strip() or not isinstance(target_id, str) or not target_id.strip():
        raise ValueError("start_id and target_id are required")
    if isinstance(max_depth, bool) or not isinstance(max_depth, int) or not 1 <= max_depth <= 12:
        raise ValueError("max_depth must be between 1 and 12")
    if isinstance(max_paths, bool) or not isinstance(max_paths, int) or not 1 <= max_paths <= 100:
        raise ValueError("max_paths must be between 1 and 100")
    if direction not in {"outgoing", "incoming", "both"}:
        raise ValueError("direction must be outgoing, incoming or both")
    relations = set(allowed_relations) if allowed_relations is not None else set(RELATIONS)
    if not relations.issubset(RELATIONS):
        raise ValueError("allowed_relations contains an unsupported relation")

    node_map = {}
    for node in nodes:
        if not isinstance(node, dict) or not isinstance(node.get("node_id"), str) or not node["node_id"].strip():
            raise ValueError("every node requires a non-empty node_id")
        if node["node_id"] in node_map:
            raise ValueError("node identifiers must be unique")
        node_map[node["node_id"]] = node
    if start_id not in node_map or target_id not in node_map:
        raise ValueError("start_id and target_id must exist in nodes")

    adjacency: dict[str, list[tuple[str, dict, str]]] = {key: [] for key in node_map}
    for edge in edges:
        if not isinstance(edge, dict):
            raise ValueError("every edge must be a dictionary")
        source, target = edge.get("source_id"), edge.get("target_id")
        relation = edge.get("relation")
        if source not in node_map or target not in node_map:
            raise ValueError("every edge endpoint must exist in nodes")
        if relation not in RELATIONS:
            raise ValueError("edge contains an unsupported relation")
        if relation not in relations:
            continue
        if direction in {"outgoing", "both"}:
            adjacency[source].append((target, edge, "outgoing"))
        if direction in {"incoming", "both"}:
            adjacency[target].append((source, edge, "incoming"))
    for neighbours in adjacency.values():
        neighbours.sort(key=lambda item: (item[0], item[1].get("relation", ""), item[2]))

    queue = deque([(start_id, [start_id], [], [], 0)])
    paths = []
    visited = set()
    truncated = False
    while queue:
        current, node_path, relation_path, edge_path, depth = queue.popleft()
        visited.add(current)
        if current == target_id:
            paths.append({
                "node_ids": node_path,
                "relations": relation_path,
                "edges": edge_path,
                "node_labels": [node_map[item].get("label", item) for item in node_path],
            })
            if len(paths) >= max_paths:
                truncated = bool(queue)
                break
            continue
        if depth >= max_depth:
            continue
        for neighbour, edge, traversal in adjacency[current]:
            if neighbour in node_path:
                continue
            edge_summary = {
                "source_id": edge["source_id"],
                "target_id": edge["target_id"],
                "relation": edge["relation"],
                "traversal": traversal,
                "confidence": edge.get("confidence", 0.0),
            }
            queue.append((neighbour, node_path + [neighbour],
                          relation_path + [edge["relation"]],
                          edge_path + [edge_summary], depth + 1))

    return {
        "start_id": start_id,
        "target_id": target_id,
        "paths": paths,
        "path_count": len(paths),
        "visited_node_count": len(visited),
        "max_depth": max_depth,
        "max_paths": max_paths,
        "truncated": truncated,
        "scientific_validity_established": False,
    }

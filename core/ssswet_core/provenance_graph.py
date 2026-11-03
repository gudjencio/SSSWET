"""Small auditable provenance graph with deterministic traversal."""
from __future__ import annotations


def build(nodes: list[dict], edges: list[tuple[str, str]]) -> dict:
    ids = {node["id"] for node in nodes}
    valid_edges = sorted((a, b) for a, b in edges if a in ids and b in ids)
    incoming = {node_id: [] for node_id in ids}
    for source, target in valid_edges:
        incoming[target].append(source)
    roots = sorted(node_id for node_id, parents in incoming.items() if not parents)
    return {"nodes": sorted(nodes, key=lambda n: n["id"]), "edges": valid_edges, "roots": roots, "invalid_edge_count": len(edges) - len(valid_edges)}

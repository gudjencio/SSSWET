"""Bounded, deterministic snapshots and diffs for research knowledge graphs."""
from __future__ import annotations

import hashlib
import json

MAX_NODES = 10000
MAX_EDGES = 20000
MAX_BYTES = 5_000_000


def _canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def build_snapshot(graph: dict) -> dict:
    if not isinstance(graph, dict):
        raise ValueError("graph must be an object")
    nodes, edges = graph.get("nodes", []), graph.get("edges", [])
    if not isinstance(nodes, list) or len(nodes) > MAX_NODES:
        raise ValueError(f"nodes must be a list of at most {MAX_NODES}")
    if not isinstance(edges, list) or len(edges) > MAX_EDGES:
        raise ValueError(f"edges must be a list of at most {MAX_EDGES}")
    if any(not isinstance(item, dict) for item in nodes + edges):
        raise ValueError("all graph nodes and edges must be objects")
    node_ids = [item.get("node_id") for item in nodes]
    edge_ids = [item.get("edge_id") for item in edges]
    if any(not isinstance(value, str) or not value.strip() for value in node_ids + edge_ids):
        raise ValueError("every node and edge requires a non-empty identifier")
    if len(node_ids) != len(set(node_ids)) or len(edge_ids) != len(set(edge_ids)):
        raise ValueError("node and edge identifiers must be unique")
    payload = {
        "schema_version": 1,
        "nodes": sorted((dict(item) for item in nodes), key=lambda item: item["node_id"]),
        "edges": sorted((dict(item) for item in edges), key=lambda item: item["edge_id"]),
        "node_count": len(nodes), "edge_count": len(edges),
        "source_graph_mutated": False,
    }
    canonical = _canonical(payload)
    if len(canonical.encode("utf-8")) > MAX_BYTES:
        raise ValueError(f"snapshot exceeds {MAX_BYTES} bytes")
    return {**payload, "snapshot_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest()}


def verify_snapshot(snapshot: dict) -> dict:
    if not isinstance(snapshot, dict):
        raise ValueError("snapshot must be an object")
    recorded = snapshot.get("snapshot_sha256")
    payload = {key: value for key, value in snapshot.items() if key != "snapshot_sha256"}
    try:
        nodes, edges = payload.get("nodes"), payload.get("edges")
        structural = (
            payload.get("schema_version") == 1
            and isinstance(nodes, list) and len(nodes) <= MAX_NODES
            and isinstance(edges, list) and len(edges) <= MAX_EDGES
            and payload.get("node_count") == len(nodes)
            and payload.get("edge_count") == len(edges)
            and all(isinstance(item, dict) for item in nodes + edges)
        )
        if structural:
            node_ids = [item.get("node_id") for item in nodes]
            edge_ids = [item.get("edge_id") for item in edges]
            structural = (
                all(isinstance(value, str) and value.strip() for value in node_ids + edge_ids)
                and len(node_ids) == len(set(node_ids))
                and len(edge_ids) == len(set(edge_ids))
            )
        canonical = _canonical(payload)
        if len(canonical.encode("utf-8")) > MAX_BYTES:
            structural = False
        expected = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    except (TypeError, ValueError):
        structural, expected = False, None
    valid = bool(structural and isinstance(recorded, str) and recorded == expected)
    return {
        "valid": valid, "recorded_sha256": recorded, "expected_sha256": expected,
        "tampered_or_incomplete": not valid,
    }


def diff_snapshots(left: dict, right: dict) -> dict:
    for snapshot in (left, right):
        if not verify_snapshot(snapshot)["valid"]:
            raise ValueError("both snapshots must pass integrity verification")
    def compare(collection, key):
        before = {item[key]: item for item in left[collection]}
        after = {item[key]: item for item in right[collection]}
        added = sorted(set(after) - set(before))
        removed = sorted(set(before) - set(after))
        changed = sorted(identifier for identifier in set(before) & set(after) if before[identifier] != after[identifier])
        return {
            "added": [after[item] for item in added],
            "removed": [before[item] for item in removed],
            "changed": [{"before": before[item], "after": after[item]} for item in changed],
        }
    nodes, edges = compare("nodes", "node_id"), compare("edges", "edge_id")
    return {
        "nodes": nodes, "edges": edges,
        "node_delta": len(nodes["added"]) - len(nodes["removed"]),
        "edge_delta": len(edges["added"]) - len(edges["removed"]),
        "source_snapshots_mutated": False,
        "scientific_validity_established": False,
    }

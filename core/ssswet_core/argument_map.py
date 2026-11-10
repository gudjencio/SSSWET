"""Typed argument-map validation and bounded evidence-path tracing."""
from __future__ import annotations

from collections import defaultdict, deque


NODE_TYPES = {"claim", "evidence", "assumption", "limitation", "method"}
RELATIONS = {"supports", "challenges", "depends_on", "qualifies", "derived_from"}
MAX_NODES = 2000
MAX_EDGES = 10000
MAX_PATH_STATES = 50000


def validate_argument_map(nodes: list[dict], edges: list[dict]) -> dict:
    if not isinstance(nodes, list) or len(nodes) > MAX_NODES:
        raise ValueError(f"nodes must be a list of at most {MAX_NODES}")
    if not isinstance(edges, list) or len(edges) > MAX_EDGES:
        raise ValueError(f"edges must be a list of at most {MAX_EDGES}")
    by_id = {}
    for node in nodes:
        if not isinstance(node, dict):
            raise ValueError("each node must be a dictionary")
        node_id, node_type = node.get("node_id"), node.get("node_type")
        if not isinstance(node_id, str) or not node_id.strip() or node_id in by_id:
            raise ValueError("node IDs must be unique and non-empty")
        if node_type not in NODE_TYPES:
            raise ValueError(f"unsupported node type: {node_type}")
        by_id[node_id] = node
    adjacency = defaultdict(list)
    reverse = defaultdict(list)
    missing = []
    normalized_edges = []
    for edge in edges:
        if not isinstance(edge, dict):
            raise ValueError("each edge must be a dictionary")
        source, target, relation = edge.get("source_id"), edge.get("target_id"), edge.get("relation")
        if not isinstance(source, str) or not isinstance(target, str) or not source or not target:
            raise ValueError("edge endpoints are required")
        if source == target:
            raise ValueError("self-referencing argument edges are not allowed")
        if relation not in RELATIONS:
            raise ValueError(f"unsupported argument relation: {relation}")
        if source not in by_id or target not in by_id:
            missing.append({"source_id": source, "target_id": target, "relation": relation})
            continue
        normalized_edges.append({"source_id": source, "target_id": target, "relation": relation})
        adjacency[source].append((target, relation))
        reverse[target].append((source, relation))

    # Detect cycles in inferential dependency edges. A cycle is a review blocker.
    inferential = {"supports", "depends_on", "derived_from"}
    colour = {node_id: 0 for node_id in by_id}
    cycles = []
    for root in sorted(by_id):
        if colour[root]:
            continue
        stack = [(root, iter(sorted(
            target for target, relation in adjacency[root] if relation in inferential
        )))]
        colour[root] = 1
        path = [root]
        positions = {root: 0}
        while stack:
            node, children = stack[-1]
            try:
                child = next(children)
            except StopIteration:
                stack.pop()
                colour[node] = 2
                positions.pop(node, None)
                if path and path[-1] == node:
                    path.pop()
                continue
            if colour[child] == 0:
                colour[child] = 1
                positions[child] = len(path)
                path.append(child)
                stack.append((child, iter(sorted(
                    target for target, relation in adjacency[child] if relation in inferential
                ))))
            elif colour[child] == 1:
                cycle = path[positions.get(child, 0):] + [child]
                if cycle not in cycles:
                    cycles.append(cycle)

    evidence_nodes = sorted(node_id for node_id, item in by_id.items() if item["node_type"] == "evidence")
    claim_nodes = sorted(node_id for node_id, item in by_id.items() if item["node_type"] == "claim")
    reachable_claims = set()
    evidence_paths = []
    path_states = 0
    path_search_truncated = False
    for evidence_id in evidence_nodes:
        queue = deque([(evidence_id, [evidence_id])])
        visited = {evidence_id}
        while queue and len(evidence_paths) < 500 and path_states < MAX_PATH_STATES:
            path_states += 1
            current, path = queue.popleft()
            if current in claim_nodes:
                reachable_claims.add(current)
                evidence_paths.append(path)
                continue
            if len(path) >= 12:
                continue
            for target, relation in sorted(adjacency[current]):
                if relation not in {"supports", "derived_from", "depends_on"} or target in visited:
                    continue
                visited.add(target)
                queue.append((target, path + [target]))
        if queue or path_states >= MAX_PATH_STATES:
            path_search_truncated = True
            break
    unsupported_claims = sorted(set(claim_nodes) - reachable_claims)
    connected_nodes = {item for path in evidence_paths for item in path}
    orphan_evidence = sorted(set(evidence_nodes) - connected_nodes)
    return {
        "valid": not missing and not cycles,
        "node_count": len(nodes), "edge_count": len(normalized_edges),
        "missing_endpoint_edges": missing, "inferential_cycles": cycles,
        "claim_nodes_without_evidence_path": unsupported_claims,
        "orphan_evidence_nodes": orphan_evidence,
        "evidence_paths": evidence_paths[:500],
        "path_search_states": path_states,
        "path_search_truncated": path_search_truncated,
        "path_tracing_bounded": True,
        "claim_truth_established": False,
    }


def trace_argument_paths(
    nodes: list[dict], edges: list[dict], start_id: str, end_id: str, *,
    max_depth: int = 8, max_paths: int = 100,
) -> dict:
    if not 1 <= max_depth <= 20 or not 1 <= max_paths <= 500:
        raise ValueError("max_depth must be 1..20 and max_paths must be 1..500")
    checked = validate_argument_map(nodes, edges)
    if not checked["valid"]:
        raise ValueError("argument map must have valid endpoints and no inferential cycles")
    node_ids = {item["node_id"] for item in nodes}
    if start_id not in node_ids or end_id not in node_ids:
        raise ValueError("start_id and end_id must exist")
    adjacency = defaultdict(list)
    for edge in edges:
        adjacency[edge["source_id"]].append((edge["target_id"], edge["relation"]))
    paths = []
    queue = deque([(start_id, [start_id])])
    states_examined = 0
    while queue and len(paths) < max_paths and states_examined < MAX_PATH_STATES:
        states_examined += 1
        current, path = queue.popleft()
        if current == end_id:
            paths.append(path)
            continue
        if len(path) - 1 >= max_depth:
            continue
        for target, relation in sorted(adjacency[current]):
            if target not in path:
                queue.append((target, path + [target]))
    return {
        "start_id": start_id, "end_id": end_id, "paths": paths,
        "path_count": len(paths), "truncated": bool(queue) or states_examined >= MAX_PATH_STATES,
        "states_examined": states_examined,
        "maximum_depth": max_depth, "maximum_paths": max_paths,
        "interpretation": "Paths represent declared relationships, not proof.",
    }

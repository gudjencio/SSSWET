"""Deterministic provenance graph analysis with explicit integrity diagnostics."""
from __future__ import annotations
import heapq

MAX_NODES = 5000
MAX_EDGES = 10000


def _cyclic_nodes(identifiers: set[str], outgoing: dict[str, list[str]], incoming: dict[str, list[str]]) -> set[str]:
    """Iterative Kosaraju traversal avoids recursion-depth failures on long graphs."""
    visited, finish = set(), []
    for start in sorted(identifiers):
        if start in visited:
            continue
        visited.add(start)
        stack = [(start, iter(outgoing[start]))]
        while stack:
            node_id, children = stack[-1]
            try:
                child = next(children)
            except StopIteration:
                finish.append(node_id)
                stack.pop()
                continue
            if child not in visited:
                visited.add(child)
                stack.append((child, iter(outgoing[child])))
    assigned, cycles = set(), set()
    for start in reversed(finish):
        if start in assigned:
            continue
        component, stack = [], [start]
        assigned.add(start)
        while stack:
            node_id = stack.pop()
            component.append(node_id)
            for parent in incoming[node_id]:
                if parent not in assigned:
                    assigned.add(parent)
                    stack.append(parent)
        if len(component) > 1:
            cycles.update(component)
    return cycles


def build(nodes: list[dict], edges: list[tuple[str, str]]) -> dict:
    """Build a bounded graph view without silently accepting broken lineage."""
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise ValueError("nodes and edges must be lists")
    if len(nodes) > MAX_NODES or len(edges) > MAX_EDGES:
        raise ValueError(f"graph exceeds {MAX_NODES} nodes or {MAX_EDGES} edges")
    unique_nodes, display_nodes, duplicate_node_ids = {}, [], set()
    invalid_node_count = 0
    for node in nodes:
        if not isinstance(node, dict):
            invalid_node_count += 1
            continue
        node_id = node.get("id")
        if not isinstance(node_id, str) or not node_id.strip():
            invalid_node_count += 1
            continue
        node_id = node_id.strip()
        normalized = dict(node)
        normalized["id"] = node_id
        display_nodes.append(normalized)
        if node_id in unique_nodes:
            duplicate_node_ids.add(node_id)
        else:
            unique_nodes[node_id] = normalized
    identifiers = set(unique_nodes)
    valid_edges, invalid_edge_count, duplicate_edge_count = set(), 0, 0
    for edge in edges:
        if isinstance(edge, dict):
            source, target = edge.get("source", edge.get("from")), edge.get("target", edge.get("to"))
        elif isinstance(edge, (tuple, list)) and len(edge) == 2:
            source, target = edge
        else:
            invalid_edge_count += 1
            continue
        if not isinstance(source, str) or not isinstance(target, str) or source not in identifiers or target not in identifiers or source == target:
            invalid_edge_count += 1
            continue
        pair = (source, target)
        if pair in valid_edges:
            duplicate_edge_count += 1
        else:
            valid_edges.add(pair)
    ordered_edges = sorted(valid_edges)
    incoming = {node_id: [] for node_id in identifiers}
    outgoing = {node_id: [] for node_id in identifiers}
    undirected = {node_id: set() for node_id in identifiers}
    for source, target in ordered_edges:
        incoming[target].append(source)
        outgoing[source].append(target)
        undirected[source].add(target)
        undirected[target].add(source)
    roots = sorted(node_id for node_id, parents in incoming.items() if not parents)
    leaves = sorted(node_id for node_id, children in outgoing.items() if not children)
    indegree = {node_id: len(incoming[node_id]) for node_id in identifiers}
    ready = [node_id for node_id, degree in indegree.items() if degree == 0]
    heapq.heapify(ready)
    topological_order = []
    while ready:
        node_id = heapq.heappop(ready)
        topological_order.append(node_id)
        for child in outgoing[node_id]:
            indegree[child] -= 1
            if indegree[child] == 0:
                heapq.heappush(ready, child)
    cycle_node_ids = sorted(_cyclic_nodes(identifiers, outgoing, incoming))
    blocked_by_cycles = sorted(identifiers - set(topological_order) - set(cycle_node_ids))
    components, unseen = 0, set(identifiers)
    while unseen:
        components += 1
        stack = [min(unseen)]
        unseen.remove(stack[0])
        while stack:
            current = stack.pop()
            for neighbor in sorted(undirected[current]):
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    stack.append(neighbor)
    return {
        "nodes": sorted(display_nodes, key=lambda item: item["id"]),
        "edges": ordered_edges, "roots": roots,
        "invalid_edge_count": invalid_edge_count, "invalid_node_count": invalid_node_count,
        "duplicate_node_ids": sorted(duplicate_node_ids), "duplicate_edge_count": duplicate_edge_count,
        "leaves": leaves, "topological_order": topological_order if not cycle_node_ids else [],
        "cycle_node_ids": cycle_node_ids, "blocked_by_cycles": blocked_by_cycles,
        "is_acyclic": not cycle_node_ids, "component_count": components,
        "graph_integrity_complete": invalid_node_count == 0 and invalid_edge_count == 0 and not duplicate_node_ids and duplicate_edge_count == 0 and not cycle_node_ids,
        "scientific_validity_established": False,
    }

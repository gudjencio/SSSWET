"""Bounded edge-disjoint-path and bottleneck analysis for declared civil-rescue graphs."""
from __future__ import annotations
from collections import deque
from .assurance_common import identifier

MAX_SEGMENTS = 1000
SCHEMA_VERSION = 1


def analyze_route_redundancy(segments: list[dict], *, start_node: str, destination_node: str) -> dict:
    if not isinstance(segments, list) or len(segments) > MAX_SEGMENTS:
        raise ValueError(f"segments must contain at most {MAX_SEGMENTS} items")
    start = identifier(start_node, "start_node")
    destination = identifier(destination_node, "destination_node")
    if start == destination:
        raise ValueError("start_node and destination_node must differ")
    seen, nodes, open_edges, blocked, unknown = set(), {start, destination}, [], [], []
    for item in segments:
        if not isinstance(item, dict):
            raise ValueError("each segment must be an object")
        sid = identifier(item.get("segment_id"), "segment_id")
        if sid in seen:
            raise ValueError("segment_id values must be unique")
        seen.add(sid)
        u, v = identifier(item.get("from_node"), "from_node"), identifier(item.get("to_node"), "to_node")
        if u == v:
            raise ValueError("route segment endpoints must differ")
        nodes.update((u, v))
        status = item.get("status")
        row = {"segment_id": sid, "from_node": u, "to_node": v, "status": status}
        if status == "open":
            open_edges.append(row)
        elif status == "blocked":
            blocked.append(row)
        elif status == "unknown":
            unknown.append(row)
        else:
            raise ValueError("segment status must be open, blocked or unknown")
    graph = {}
    def add_edge(u, v, capacity):
        graph.setdefault(u, []).append([v, capacity, len(graph.get(v, []))])
        graph.setdefault(v, []).append([u, 0, len(graph[u]) - 1])
    infinity = len(open_edges) + 1
    for edge in sorted(open_edges, key=lambda row: row["segment_id"]):
        u, v, sid = edge["from_node"], edge["to_node"], edge["segment_id"]
        ein, eout = "edge-in:" + sid, "edge-out:" + sid
        add_edge("node:" + u, ein, infinity)
        add_edge("node:" + v, ein, infinity)
        add_edge(eout, "node:" + u, infinity)
        add_edge(eout, "node:" + v, infinity)
        add_edge(ein, eout, 1)
    source, sink = "node:" + start, "node:" + destination
    flow = 0
    while True:
        parent = {source: None}
        queue = deque([source])
        while queue and sink not in parent:
            current = queue.popleft()
            for index, edge in enumerate(graph.get(current, [])):
                nxt, capacity, _ = edge
                if capacity > 0 and nxt not in parent:
                    parent[nxt] = (current, index)
                    queue.append(nxt)
        if sink not in parent:
            break
        node, amount = sink, infinity
        while parent[node] is not None:
            prev, index = parent[node]
            amount = min(amount, graph[prev][index][1])
            node = prev
        node = sink
        while parent[node] is not None:
            prev, index = parent[node]
            edge = graph[prev][index]
            edge[1] -= amount
            graph[node][edge[2]][1] += amount
            node = prev
        flow += amount
    reachable, queue = {source}, deque([source])
    while queue:
        current = queue.popleft()
        for nxt, capacity, _ in graph.get(current, []):
            if capacity > 0 and nxt not in reachable:
                reachable.add(nxt)
                queue.append(nxt)
    cut = sorted(edge["segment_id"] for edge in open_edges if "edge-in:" + edge["segment_id"] in reachable and "edge-out:" + edge["segment_id"] not in reachable)
    status = "no_verified_path" if flow == 0 else "single_path_only" if flow == 1 else "multiple_edge_disjoint_paths"
    return {"schema_version": SCHEMA_VERSION, "start_node": start, "destination_node": destination, "node_count": len(nodes), "segment_count": len(segments), "open_segment_count": len(open_edges), "blocked_segment_ids": sorted(edge["segment_id"] for edge in blocked), "unknown_segment_ids": sorted(edge["segment_id"] for edge in unknown), "maximum_edge_disjoint_path_count": flow, "status": status, "minimum_cut_segment_ids": cut, "unknown_segments_treated_as_open": False, "segments_deleted": False, "route_generated": False, "dispatch_authorized": False, "accessibility_or_safety_certified": False}

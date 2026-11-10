"""Conservative source-dependency clustering from explicit lineage metadata.

Publisher or domain similarity alone never implies independence or dependence.
Only declared shared datasets, author/funder groups, or parent-source links
connect records.
"""
from __future__ import annotations

from collections import defaultdict


MAX_SOURCES = 2000
MAX_LINKS_PER_SOURCE = 100
_LINK_FIELDS = ("parent_source_ids", "dataset_ids", "author_group_ids", "funder_group_ids")


def analyze_source_lineage(sources: list[dict]) -> dict:
    if not isinstance(sources, list) or len(sources) > MAX_SOURCES:
        raise ValueError(f"sources must be a list of at most {MAX_SOURCES} records")
    by_id = {}
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError("every source must be a dictionary")
        source_id = source.get("source_id")
        if not isinstance(source_id, str) or not source_id.strip() or len(source_id) > 200:
            raise ValueError("every source needs a valid source_id")
        source_id = source_id.strip()
        if source_id in by_id:
            raise ValueError(f"duplicate source_id: {source_id}")
        clean = {"source_id": source_id}
        for field in _LINK_FIELDS:
            values = source.get(field, [])
            if not isinstance(values, list) or len(values) > MAX_LINKS_PER_SOURCE:
                raise ValueError(f"{field} must be a list of at most {MAX_LINKS_PER_SOURCE} values")
            if any(not isinstance(value, str) or not value.strip() for value in values):
                raise ValueError(f"{field} contains an empty or invalid value")
            clean[field] = sorted(set(value.strip() for value in values))
        by_id[source_id] = clean

    parent_graph = {key: set() for key in by_id}
    warnings = []
    for source_id, source in by_id.items():
        for parent in source["parent_source_ids"]:
            if parent == source_id:
                raise ValueError("a source cannot be its own parent")
            if parent not in by_id:
                warnings.append({"source_id": source_id, "missing_parent_source_id": parent})
            else:
                parent_graph[source_id].add(parent)

    # Iterative colour DFS avoids recursion limits on large, bounded inputs.
    colour = {key: 0 for key in by_id}
    cycles = []
    for root in sorted(by_id):
        if colour[root]:
            continue
        stack = [(root, iter(sorted(parent_graph[root])))]
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
                stack.append((child, iter(sorted(parent_graph[child]))))
            elif colour[child] == 1:
                start = positions.get(child, 0)
                cycle = path[start:] + [child]
                if cycle not in cycles:
                    cycles.append(cycle)

    if cycles:
        return {
            "valid": False, "source_count": len(by_id), "clusters": [],
            "cycle_paths": cycles, "warnings": warnings,
            "publisher_similarity_used": False,
        }

    parent = {key: key for key in by_id}

    def find(value):
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(left, right):
        a, b = find(left), find(right)
        if a != b:
            parent[max(a, b)] = min(a, b)

    shared = defaultdict(set)
    for source_id, source in by_id.items():
        for field in _LINK_FIELDS:
            for value in source[field]:
                shared[(field, value)].add(source_id)
    for (field, value), members in shared.items():
        ordered = sorted(members)
        for other in ordered[1:]:
            union(ordered[0], other)

    components = defaultdict(list)
    for source_id in sorted(by_id):
        components[find(source_id)].append(source_id)
    clusters = []
    source_to_cluster = {}
    for index, members in enumerate(sorted(components.values(), key=lambda group: group[0]), start=1):
        cluster_id = f"lineage-{index:04d}"
        bases = []
        member_set = set(members)
        for (field, value), linked in sorted(shared.items()):
            overlap = sorted(member_set & linked)
            if len(overlap) > 1:
                bases.append({"field": field, "value": value, "source_ids": overlap})
        clusters.append({
            "cluster_id": cluster_id, "source_ids": members,
            "declared_shared_lineage": bases,
            "independent_source_count": 1,
        })
        for member in members:
            source_to_cluster[member] = cluster_id

    return {
        "valid": True, "source_count": len(by_id), "clusters": clusters,
        "source_to_cluster": source_to_cluster,
        "dependency_cluster_count": len(clusters),
        "warnings": warnings, "cycle_paths": [],
        "publisher_similarity_used": False,
        "independence_certified": False,
    }

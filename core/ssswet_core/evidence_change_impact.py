"""Bounded dependency traversal for evidence and research-artifact changes."""
from __future__ import annotations

from collections import deque

MAX_ARTIFACTS = 10_000
MAX_DEPENDENCIES = 50_000
MAX_CHANGED_IDS = 500


def analyze_change_impact(artifacts: list[dict], changed_ids: list[str], *, max_affected: int = 5_000) -> dict:
    if not isinstance(artifacts, list) or len(artifacts) > MAX_ARTIFACTS:
        raise ValueError(f"artifacts must be a list of at most {MAX_ARTIFACTS}")
    if not isinstance(changed_ids, list) or len(changed_ids) > MAX_CHANGED_IDS:
        raise ValueError(f"changed_ids must be a list of at most {MAX_CHANGED_IDS}")
    if isinstance(max_affected, bool) or not isinstance(max_affected, int) or not 1 <= max_affected <= MAX_ARTIFACTS:
        raise ValueError("max_affected must be between 1 and 10000")
    nodes = {}
    reverse = {}
    missing_dependencies = []
    dependency_count = 0
    for item in artifacts:
        if not isinstance(item, dict):
            raise ValueError("every artifact must be an object")
        identifier = item.get("artifact_id")
        if not isinstance(identifier, str) or not identifier.strip() or len(identifier) > 240:
            raise ValueError("artifact_id must contain 1 to 240 characters")
        identifier = identifier.strip()
        if identifier in nodes:
            raise ValueError("artifact identifiers must be unique")
        deps = item.get("depends_on", [])
        if not isinstance(deps, list) or len(deps) > MAX_DEPENDENCIES:
            raise ValueError("depends_on must be a bounded list")
        normalized = []
        for dep in deps:
            if not isinstance(dep, str) or not dep.strip():
                raise ValueError("dependency identifiers must be non-empty strings")
            normalized.append(dep.strip())
        if len(normalized) != len(set(normalized)):
            raise ValueError("duplicate dependencies are not allowed")
        dependency_count += len(normalized)
        if dependency_count > MAX_DEPENDENCIES:
            raise ValueError(f"dependency count exceeds {MAX_DEPENDENCIES}")
        nodes[identifier] = {**item, "artifact_id": identifier, "depends_on": normalized}
    for identifier, item in nodes.items():
        for dep in item["depends_on"]:
            if dep not in nodes:
                missing_dependencies.append({"artifact_id": identifier, "missing_dependency_id": dep})
            else:
                reverse.setdefault(dep, set()).add(identifier)
    changed = []
    for identifier in changed_ids:
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError("changed identifiers must be non-empty strings")
        changed.append(identifier.strip())
    if len(changed) != len(set(changed)):
        raise ValueError("changed_ids must be unique")
    known_changed = sorted(set(changed) & set(nodes))
    missing_changed = sorted(set(changed) - set(nodes))
    distances = {}
    paths = {}
    queue = deque()
    for root in known_changed:
        queue.append((root, root, [root]))
    while queue:
        root, current, path = queue.popleft()
        for dependent in sorted(reverse.get(current, ())):
            if dependent == root:
                continue
            candidate_distance = len(path)
            prior = distances.get(dependent)
            if prior is None or candidate_distance < prior:
                distances[dependent] = candidate_distance
                paths[dependent] = path + [dependent]
                queue.append((root, dependent, path + [dependent]))
    ordered = sorted(distances, key=lambda key: (distances[key], key))
    truncated = len(ordered) > max_affected
    selected = ordered[:max_affected]

    indegree = {identifier: 0 for identifier in nodes}
    for identifier, item in nodes.items():
        indegree[identifier] = sum(1 for dep in item["depends_on"] if dep in nodes)
    ready = deque(sorted(identifier for identifier, degree in indegree.items() if degree == 0))
    visited = 0
    while ready:
        current = ready.popleft()
        visited += 1
        for dependent in reverse.get(current, ()):
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                ready.append(dependent)
    return {
        "directly_changed_ids": known_changed,
        "missing_changed_ids": missing_changed,
        "downstream_review_required": [
            {"artifact_id": identifier, "distance": distances[identifier], "shortest_dependency_path": paths[identifier]}
            for identifier in selected
        ],
        "affected_count": len(ordered),
        "returned_affected_count": len(selected),
        "truncated": truncated,
        "missing_dependencies": sorted(missing_dependencies, key=lambda item: (item["artifact_id"], item["missing_dependency_id"])),
        "dependency_cycle_detected": visited != len(nodes),
        "automatic_retraction": False,
        "automatic_deletion": False,
        "stored_verification_states_changed": False,
        "human_review_required": bool(known_changed or missing_changed or ordered),
    }

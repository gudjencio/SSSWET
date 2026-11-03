"""Stable topological ordering for bounded research-task dependency graphs."""
from __future__ import annotations
import heapq

def order(tasks: list[dict], max_tasks: int = 10_000) -> dict:
    if not isinstance(tasks, list) or not isinstance(max_tasks, int) or max_tasks < 1 or len(tasks) > max_tasks:
        raise ValueError("tasks must be a list within the positive max_tasks limit")
    identifiers = {}
    for task in tasks:
        if not isinstance(task, dict):
            raise ValueError("each task must be a dictionary")
        task_id, deps = task.get("id"), task.get("depends_on", [])
        if not isinstance(task_id, str) or not task_id.strip() or task_id in identifiers:
            raise ValueError("task IDs must be unique non-empty strings")
        if not isinstance(deps, list) or any(not isinstance(dep, str) or not dep for dep in deps):
            raise ValueError("depends_on must be a list of task IDs")
        if len(set(deps)) != len(deps) or task_id in deps:
            raise ValueError("dependencies must be unique and cannot include the task itself")
        identifiers[task_id] = set(deps)
    unknown = sorted({dep for deps in identifiers.values() for dep in deps if dep not in identifiers})
    if unknown:
        return {"valid": False, "unknown_dependencies": unknown, "order": [], "cycle_members": []}
    dependents = {task_id: [] for task_id in identifiers}
    indegree = {task_id: len(deps) for task_id, deps in identifiers.items()}
    for task_id, deps in identifiers.items():
        for dep in deps:
            dependents[dep].append(task_id)
    ready = [task_id for task_id, degree in indegree.items() if degree == 0]
    heapq.heapify(ready)
    result = []
    while ready:
        current = heapq.heappop(ready)
        result.append(current)
        for child in sorted(dependents[current]):
            indegree[child] -= 1
            if indegree[child] == 0:
                heapq.heappush(ready, child)
    cycles = sorted(task_id for task_id, degree in indegree.items() if degree > 0)
    return {"valid": not cycles, "unknown_dependencies": [], "order": result, "cycle_members": cycles, "task_count": len(tasks)}

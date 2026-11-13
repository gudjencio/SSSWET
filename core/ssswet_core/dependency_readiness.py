"""Bounded research-task DAG readiness and critical-path analysis."""
from __future__ import annotations

from math import isfinite
from typing import Any

MAX_TASKS = 500


def _duration(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a finite non-negative number")
    result = float(value)
    if not isfinite(result) or result < 0:
        raise ValueError(f"{field} must be a finite non-negative number")
    return result


def analyze_dependencies(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    """Return topological readiness diagnostics; never executes or approves work."""
    if not isinstance(tasks, list) or not 1 <= len(tasks) <= MAX_TASKS:
        raise ValueError(f"tasks must contain 1 to {MAX_TASKS} records")
    records = {}
    for item in tasks:
        if not isinstance(item, dict):
            raise ValueError("every task must be an object")
        task_id = item.get("task_id")
        if not isinstance(task_id, str) or not task_id.strip() or len(task_id) > 160:
            raise ValueError("task_id must contain 1 to 160 characters")
        task_id = task_id.strip()
        if task_id in records:
            raise ValueError("task IDs must be unique")
        dependencies = item.get("depends_on", [])
        if not isinstance(dependencies, list) or len(dependencies) > MAX_TASKS:
            raise ValueError("depends_on must be a bounded list")
        if any(not isinstance(dep, str) or not dep.strip() for dep in dependencies):
            raise ValueError("dependencies must be non-empty task IDs")
        dependencies = sorted(set(dep.strip() for dep in dependencies))
        if task_id in dependencies:
            raise ValueError("a task cannot depend on itself")
        gate = item.get("gate_status", "ready")
        if gate not in {"ready", "pending", "blocked"}:
            raise ValueError("gate_status must be ready, pending or blocked")
        records[task_id] = {
            "task_id": task_id, "duration_hours": _duration(item.get("duration_hours"), "duration_hours"),
            "depends_on": dependencies, "gate_status": gate,
        }

    missing = sorted({
        dep for item in records.values() for dep in item["depends_on"] if dep not in records
    })
    indegree = {key: sum(dep in records for dep in item["depends_on"]) for key, item in records.items()}
    dependents = {key: [] for key in records}
    for key, item in records.items():
        for dep in item["depends_on"]:
            if dep in records:
                dependents[dep].append(key)
    ready = sorted(key for key, degree in indegree.items() if degree == 0)
    order, earliest_finish, critical_parent = [], {}, {}
    while ready:
        current = ready.pop(0)
        order.append(current)
        start = max((earliest_finish.get(dep, 0.0) for dep in records[current]["depends_on"] if dep in records), default=0.0)
        earliest_finish[current] = start + records[current]["duration_hours"]
        parents = [dep for dep in records[current]["depends_on"] if dep in records]
        critical_parent[current] = max(parents, key=lambda dep: (earliest_finish.get(dep, 0.0), dep), default=None)
        for child in sorted(dependents[current]):
            indegree[child] -= 1
            if indegree[child] == 0:
                ready.append(child)
                ready.sort()
    cyclic = sorted(key for key, degree in indegree.items() if degree > 0)

    blocked_reasons = {}
    for task_id in order:
        item = records[task_id]
        reasons = []
        if item["gate_status"] != "ready":
            reasons.append("gate_" + item["gate_status"])
        for dep in item["depends_on"]:
            if dep not in records:
                reasons.append("missing_dependency:" + dep)
            elif dep in blocked_reasons:
                reasons.append("dependency_not_ready:" + dep)
        blocked_reasons[task_id] = sorted(reasons)

    critical_path = []
    if order and not cyclic:
        endpoint = max(order, key=lambda key: (earliest_finish[key], key))
        cursor = endpoint
        while cursor is not None:
            critical_path.append(cursor)
            cursor = critical_parent[cursor]
        critical_path.reverse()
    return {
        "topological_order": order,
        "missing_dependency_ids": missing,
        "cycle_task_ids": cyclic,
        "earliest_finish_hours": {key: earliest_finish[key] for key in order},
        "critical_path_task_ids": critical_path,
        "critical_path_duration_hours": max(earliest_finish.values(), default=0.0) if not cyclic else None,
        "tasks_blocked_from_ready_state": {
            key: reasons for key, reasons in sorted(blocked_reasons.items()) if reasons
        },
        "schedule_computable": not cyclic and not missing,
        "task_execution_started": False,
        "gate_approval_granted": False,
    }

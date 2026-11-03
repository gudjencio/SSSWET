from dataclasses import dataclass
from time import monotonic

from .models import Task, Agent


@dataclass(frozen=True)
class CoordinationResult:
    assignments: list[tuple[str, str]]
    elapsed_ms: float
    budget_ms: float
    completed_within_budget: bool


def coordinate_batch(tasks: list[Task], agents: list[Agent], *, budget_ms: float = 25.0) -> CoordinationResult:
    """Assign independent queued tasks to waiting agents with a bounded pass.

    This is scheduling support only: it does not execute model calls and does
    not weaken verification or safety gates. Priority is stable and deterministic.
    """
    if budget_ms <= 0:
        raise ValueError("budget_ms must be positive")
    start = monotonic()
    ordered = sorted(enumerate(tasks), key=lambda item: (-item[1].priority, item[0]))
    waiting = [a for a in agents if a.status.value == "waiting"]
    assignments: list[tuple[str, str]] = []
    for _, task in ordered:
        if monotonic() - start >= budget_ms / 1000:
            break
        if not waiting:
            break
        agent = waiting.pop(0)
        assignments.append((agent.id, task.id))
    elapsed = (monotonic() - start) * 1000
    return CoordinationResult(assignments, elapsed, budget_ms, elapsed <= budget_ms)

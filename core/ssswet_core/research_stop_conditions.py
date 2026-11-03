"""Bounded stopping rules for long-running research loops."""
from __future__ import annotations


def should_stop(*, iterations: int, max_iterations: int, failures: int = 0, max_failures: int = 3, unchanged_rounds: int = 0, max_unchanged_rounds: int = 5) -> dict:
    if min(iterations, max_iterations, failures, max_failures, unchanged_rounds, max_unchanged_rounds) < 0:
        raise ValueError("limits cannot be negative")
    reasons = []
    if iterations >= max_iterations: reasons.append("iteration_limit")
    if failures >= max_failures: reasons.append("failure_limit")
    if unchanged_rounds >= max_unchanged_rounds: reasons.append("no_progress_limit")
    return {"stop": bool(reasons), "reasons": reasons}

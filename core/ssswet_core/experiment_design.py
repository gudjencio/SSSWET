"""Deterministic bounded parameter grids for reproducible research planning."""
from __future__ import annotations


def grid(parameters: dict[str, list], max_runs: int = 1000) -> list[dict]:
    if max_runs < 1:
        raise ValueError("max_runs must be positive")
    keys = sorted(parameters)
    for key in keys:
        if not parameters[key]:
            return []
    runs = [{}]
    for key in keys:
        next_runs = []
        for run in runs:
            for value in parameters[key]:
                if len(next_runs) >= max_runs:
                    return next_runs
                candidate = dict(run)
                candidate[key] = value
                next_runs.append(candidate)
        runs = next_runs
    return runs

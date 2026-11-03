"""Small, dependency-free accounting helpers for verified research throughput."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ThroughputTarget:
    major_per_day: int = 1000
    fixes_per_hour: int = 100


def completion_ratio(completed: int, target: int) -> float:
    if target <= 0:
        raise ValueError("target must be positive")
    if completed < 0:
        raise ValueError("completed must not be negative")
    return min(completed / target, 1.0)


def shortfall(completed: int, target: int) -> int:
    if target <= 0:
        raise ValueError("target must be positive")
    if completed < 0:
        raise ValueError("completed must not be negative")
    return max(target - completed, 0)

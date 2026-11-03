"""P-value adjustment helpers; adjusted values do not establish scientific validity."""
from __future__ import annotations
import math

def adjust(p_values: list[float], method: str = "holm") -> list[float]:
    if method not in {"bonferroni", "holm", "bh"}:
        raise ValueError("method must be bonferroni, holm, or bh")
    if not isinstance(p_values, list) or not p_values or len(p_values) > 100_000:
        raise ValueError("p_values must be a non-empty list of at most 100000 values")
    for value in p_values:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1:
            raise ValueError("each p-value must be finite and between 0 and 1")
    n = len(p_values)
    if method == "bonferroni":
        return [min(1.0, float(p) * n) for p in p_values]
    order = sorted(range(n), key=lambda i: (p_values[i], i))
    adjusted = [0.0] * n
    if method == "holm":
        running = 0.0
        for rank, index in enumerate(order):
            running = max(running, (n - rank) * float(p_values[index]))
            adjusted[index] = min(1.0, running)
    else:
        running = 1.0
        for rank in range(n - 1, -1, -1):
            index = order[rank]
            running = min(running, float(p_values[index]) * n / (rank + 1))
            adjusted[index] = min(1.0, running)
    return adjusted

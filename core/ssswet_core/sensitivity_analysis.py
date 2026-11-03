"""Bounded one-at-a-time sensitivity analysis for deterministic models."""
from __future__ import annotations


def one_at_a_time(base: dict, variables: dict, evaluate, relative_step: float = 0.01) -> list[dict]:
    if relative_step <= 0:
        raise ValueError("relative_step must be positive")
    baseline = float(evaluate(dict(base)))
    results = []
    for name in sorted(variables):
        value = float(variables[name])
        step = max(abs(value) * relative_step, relative_step)
        changed = dict(base)
        changed[name] = value + step
        output = float(evaluate(changed))
        results.append({"variable": name, "baseline": baseline, "perturbed": output, "delta": output - baseline, "step": step})
    return results

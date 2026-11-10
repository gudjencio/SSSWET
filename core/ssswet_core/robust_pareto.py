"""Conservative interval-dominance analysis for engineering alternatives."""
from __future__ import annotations

from math import isfinite

MAX_ALTERNATIVES = 1_000
MAX_OBJECTIVES = 20


def _number(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError(f"{label} must be a finite number")
    return float(value)


def analyze_frontier(alternatives: list[dict], objectives: list[dict]) -> dict:
    if not isinstance(alternatives, list) or not 1 <= len(alternatives) <= MAX_ALTERNATIVES:
        raise ValueError(f"alternatives must contain 1 to {MAX_ALTERNATIVES} entries")
    if not isinstance(objectives, list) or not 1 <= len(objectives) <= MAX_OBJECTIVES:
        raise ValueError(f"objectives must contain 1 to {MAX_OBJECTIVES} entries")
    directions, names = {}, set()
    for objective in objectives:
        if not isinstance(objective, dict):
            raise ValueError("each objective must be an object")
        name, direction = objective.get("name"), objective.get("direction")
        if not isinstance(name, str) or not name.strip() or len(name) > 120 or name in names or direction not in {"minimize", "maximize"}:
            raise ValueError("objective names must be unique and directions must be minimize or maximize")
        names.add(name)
        directions[name] = direction
    normalized, identifiers = [], set()
    for alternative in alternatives:
        if not isinstance(alternative, dict):
            raise ValueError("each alternative must be an object")
        identifier, metrics = alternative.get("alternative_id"), alternative.get("metrics")
        if not isinstance(identifier, str) or not identifier.strip() or len(identifier) > 200 or identifier in identifiers:
            raise ValueError("alternative_id values must be unique non-empty strings")
        identifiers.add(identifier)
        if not isinstance(metrics, dict) or set(metrics) != names:
            raise ValueError("each alternative must provide exactly one metric for every objective")
        intervals = {}
        for name in names:
            metric = metrics[name]
            if not isinstance(metric, dict):
                raise ValueError("each metric must contain value and optional uncertainty")
            value = _number(metric.get("value"), "metric value")
            uncertainty = _number(metric.get("uncertainty", 0.0), "metric uncertainty")
            if uncertainty < 0:
                raise ValueError("metric uncertainty cannot be negative")
            intervals[name] = (value - uncertainty, value + uncertainty)
        normalized.append((identifier, intervals))

    def dominates(left: dict, right: dict) -> bool:
        strict = False
        for name, direction in directions.items():
            l_low, l_high = left[name]
            r_low, r_high = right[name]
            if direction == "minimize":
                if l_high > r_low:
                    return False
                strict = strict or l_high < r_low
            else:
                if l_low < r_high:
                    return False
                strict = strict or l_low > r_high
        return strict

    dominated_by = {identifier: [] for identifier, _ in normalized}
    pairs = []
    for left_index, (left_id, left_metrics) in enumerate(normalized):
        for right_id, right_metrics in normalized[left_index + 1:]:
            if dominates(left_metrics, right_metrics):
                dominated_by[right_id].append(left_id)
                pairs.append({"dominant": left_id, "dominated": right_id})
            elif dominates(right_metrics, left_metrics):
                dominated_by[left_id].append(right_id)
                pairs.append({"dominant": right_id, "dominated": left_id})
    frontier = sorted(identifier for identifier, dominators in dominated_by.items() if not dominators)
    return {
        "objective_count": len(objectives),
        "alternative_count": len(normalized),
        "pareto_frontier_ids": frontier,
        "dominance_pairs": pairs,
        "incomparable_pairs_preserved": True,
        "single_best_alternative_selected": False,
        "interval_dominance_is_conservative": True,
    }

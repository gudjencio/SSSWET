"""Safety-floor-aware Pareto comparison without a weighted composite score."""
from __future__ import annotations

from math import isfinite
from typing import Any

MAX_CANDIDATES = 500
MAX_OBJECTIVES = 30


def _finite(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be numeric")
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{field} must be finite")
    return result


def compare_designs(
    candidates: list[dict[str, Any]], objectives: list[dict[str, str]], *,
    safety_floors: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Identify non-dominated candidates; declared floors are screening constraints only."""
    if not isinstance(candidates, list) or not 1 <= len(candidates) <= MAX_CANDIDATES:
        raise ValueError(f"candidates must contain 1 to {MAX_CANDIDATES} records")
    if not isinstance(objectives, list) or not 1 <= len(objectives) <= MAX_OBJECTIVES:
        raise ValueError(f"objectives must contain 1 to {MAX_OBJECTIVES} records")
    metric_directions = {}
    for item in objectives:
        if not isinstance(item, dict):
            raise ValueError("every objective must be an object")
        name = item.get("name")
        direction = item.get("direction")
        if not isinstance(name, str) or not name.strip() or direction not in {"minimize", "maximize"}:
            raise ValueError("each objective needs a name and minimize/maximize direction")
        if name in metric_directions:
            raise ValueError("objective names must be unique")
        metric_directions[name] = direction
    floors = safety_floors or []
    if not isinstance(floors, list) or len(floors) > MAX_OBJECTIVES:
        raise ValueError("safety_floors must be a bounded list")
    normalized_floors = []
    for item in floors:
        if not isinstance(item, dict) or item.get("operator") not in {"min", "max"}:
            raise ValueError("each safety floor needs a min or max operator")
        metric = item.get("metric")
        if metric not in metric_directions:
            raise ValueError("safety floor metric must be a declared objective")
        normalized_floors.append({
            "metric": metric, "operator": item["operator"],
            "value": _finite(item.get("value"), "safety floor value"),
        })

    normalized = {}
    for item in candidates:
        if not isinstance(item, dict):
            raise ValueError("every candidate must be an object")
        candidate_id = item.get("candidate_id")
        if not isinstance(candidate_id, str) or not candidate_id.strip() or len(candidate_id) > 160:
            raise ValueError("candidate_id must contain 1 to 160 characters")
        candidate_id = candidate_id.strip()
        if candidate_id in normalized:
            raise ValueError("candidate IDs must be unique")
        metrics = item.get("metrics")
        if not isinstance(metrics, dict):
            raise ValueError("candidate metrics must be an object")
        values = {
            name: _finite(metrics[name], f"{candidate_id}.{name}")
            for name in metric_directions if name in metrics
        }
        missing = sorted(set(metric_directions) - set(values))
        floor_violations = []
        for floor in normalized_floors:
            if floor["metric"] not in values:
                continue
            value = values[floor["metric"]]
            failed = value < floor["value"] if floor["operator"] == "min" else value > floor["value"]
            if failed:
                floor_violations.append({
                    "metric": floor["metric"], "operator": floor["operator"],
                    "required": floor["value"], "observed": value,
                })
        normalized[candidate_id] = {
            "metrics": values, "missing_metrics": missing,
            "safety_floor_violations": floor_violations,
        }

    eligible = {
        key: value for key, value in normalized.items()
        if not value["missing_metrics"] and not value["safety_floor_violations"]
    }

    def dominates(left: dict, right: dict) -> bool:
        no_worse, strictly_better = True, False
        for metric, direction in metric_directions.items():
            a, b = left["metrics"][metric], right["metrics"][metric]
            better = a < b if direction == "minimize" else a > b
            worse = a > b if direction == "minimize" else a < b
            if worse:
                no_worse = False
                break
            strictly_better = strictly_better or better
        return no_worse and strictly_better

    dominated_by = {key: [] for key in eligible}
    frontier = []
    for candidate_id, candidate in eligible.items():
        dominators = sorted(
            other_id for other_id, other in eligible.items()
            if other_id != candidate_id and dominates(other, candidate)
        )
        dominated_by[candidate_id] = dominators
        if not dominators:
            frontier.append(candidate_id)
    return {
        "objective_directions": metric_directions,
        "safety_floors": normalized_floors,
        "pareto_frontier": sorted(frontier),
        "dominated_by": dominated_by,
        "ineligible": {
            key: {
                "missing_metrics": value["missing_metrics"],
                "safety_floor_violations": value["safety_floor_violations"],
            }
            for key, value in sorted(normalized.items()) if key not in eligible
        },
        "candidate_count": len(candidates),
        "eligible_candidate_count": len(eligible),
        "weighted_composite_score": None,
        "safety_certification_granted": False,
    }

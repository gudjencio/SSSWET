"""Range-based stress testing for civil rescue resource planning."""
from __future__ import annotations

from math import isfinite
from .rescue_resource_planner import ALLOWED_RESOURCES, MAX_QUANTITY

CRITICALITY = {"essential", "high", "standard"}


def _range(item, field):
    if not isinstance(item, dict):
        raise ValueError(f"{field} must be an object with min, expected and max")
    values = {}
    for key in ("min", "expected", "max"):
        value = item.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(float(value)) or not 0 <= value <= MAX_QUANTITY:
            raise ValueError(f"{field}.{key} must be a finite non-negative quantity")
        values[key] = float(value)
    if not values["min"] <= values["expected"] <= values["max"]:
        raise ValueError(f"{field} must satisfy min <= expected <= max")
    return values


def evaluate_rescue_scenario(demand_ranges: dict, supply_ranges: dict) -> dict:
    if not isinstance(demand_ranges, dict) or not isinstance(supply_ranges, dict):
        raise ValueError("demand_ranges and supply_ranges must be objects")
    unknown = (set(demand_ranges) | set(supply_ranges)) - ALLOWED_RESOURCES
    if unknown:
        raise ValueError("resource outside conservative civil-rescue allowlist: " + ", ".join(sorted(unknown)))
    results = []
    for resource in sorted(set(demand_ranges) | set(supply_ranges)):
        demand = _range(demand_ranges.get(resource, {"min": 0, "expected": 0, "max": 0}), f"demand.{resource}")
        supply = _range(supply_ranges.get(resource, {"min": 0, "expected": 0, "max": 0}), f"supply.{resource}")
        criticality = demand_ranges.get(resource, {}).get("criticality", "standard")
        if criticality not in CRITICALITY:
            raise ValueError("criticality must be essential, high or standard")
        best_shortage = max(0.0, demand["min"] - supply["max"])
        expected_shortage = max(0.0, demand["expected"] - supply["expected"])
        worst_shortage = max(0.0, demand["max"] - supply["min"])
        best_coverage = 1.0 if demand["min"] == 0 else min(1.0, supply["max"] / demand["min"])
        worst_coverage = 1.0 if demand["max"] == 0 else min(1.0, supply["min"] / demand["max"])
        results.append({
            "resource": resource,
            "criticality": criticality,
            "best_case_shortage": best_shortage,
            "expected_shortage": expected_shortage,
            "worst_case_shortage": worst_shortage,
            "best_case_coverage_ratio": best_coverage,
            "worst_case_coverage_ratio": worst_coverage,
            "critical_shortage_possible": criticality in {"essential", "high"} and worst_shortage > 0,
        })
    return {
        "resources": results,
        "resource_count": len(results),
        "critical_shortage_possible": any(item["critical_shortage_possible"] for item in results),
        "scenario_uncertainty_retained": True,
        "resource_allocation_performed": False,
        "dispatch_performed": False,
        "medical_or_evacuation_decisions_automated": False,
        "human_planning_review_required": True,
    }

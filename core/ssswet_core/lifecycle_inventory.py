"""Transparent aggregation of user-supplied life-cycle inventory factors."""
from __future__ import annotations

from math import isfinite, sqrt

MAX_FLOWS = 10_000


def aggregate_inventory(flows: list[dict]) -> dict:
    if not isinstance(flows, list) or len(flows) > MAX_FLOWS:
        raise ValueError(f"flows must be a list of at most {MAX_FLOWS} entries")
    totals: dict[tuple[str, str], dict] = {}
    source_ids = set()
    flow_ids = set()
    for flow in flows:
        if not isinstance(flow, dict):
            raise ValueError("each inventory flow must be an object")
        required = ("flow_id", "phase", "quantity_unit", "factor_basis_unit", "impact_unit", "factor_source_id", "factor_version")
        if any(not isinstance(flow.get(key), str) or not flow[key].strip() or len(flow[key]) > (50 if key in {"quantity_unit", "factor_basis_unit", "impact_unit"} else 200) for key in required):
            raise ValueError("each flow needs identifiers, phase and explicit units and factor provenance")
        if flow["flow_id"] in flow_ids:
            raise ValueError("flow_id values must be unique to prevent accidental double counting")
        flow_ids.add(flow["flow_id"])
        if flow["quantity_unit"] != flow["factor_basis_unit"]:
            raise ValueError("quantity_unit must exactly match factor_basis_unit; convert explicitly before aggregation")
        quantity, factor = flow.get("quantity"), flow.get("factor_value")
        q_uncertainty, f_uncertainty = flow.get("quantity_uncertainty", 0.0), flow.get("factor_uncertainty", 0.0)
        numbers = (quantity, factor, q_uncertainty, f_uncertainty)
        if any(isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) for value in numbers):
            raise ValueError("quantities, factors and uncertainties must be finite numbers")
        if quantity < 0 or factor < 0 or q_uncertainty < 0 or f_uncertainty < 0:
            raise ValueError("inventory values and uncertainties cannot be negative")
        key = (flow["phase"], flow["impact_unit"])
        impact = quantity * factor
        uncertainty = sqrt((factor * q_uncertainty) ** 2 + (quantity * f_uncertainty) ** 2)
        bucket = totals.setdefault(key, {"phase": key[0], "impact_unit": key[1], "impact_total": 0.0, "variance_total": 0.0, "flow_ids": [], "factor_source_ids": [], "factor_versions": []})
        bucket["impact_total"] += impact
        bucket["variance_total"] += uncertainty ** 2
        bucket["flow_ids"].append(flow["flow_id"])
        bucket["factor_source_ids"].append(flow["factor_source_id"])
        bucket["factor_versions"].append(flow["factor_version"])
        source_ids.add(flow["factor_source_id"])
    results = []
    for key in sorted(totals):
        item = totals[key]
        results.append({
            "phase": item["phase"], "impact_unit": item["impact_unit"],
            "impact_total": item["impact_total"],
            "combined_standard_uncertainty": sqrt(item["variance_total"]),
            "flow_ids": sorted(item["flow_ids"]),
            "factor_source_ids": sorted(set(item["factor_source_ids"])),
            "factor_versions": sorted(set(item["factor_versions"])),
            "uncertainty_assumption": "independent quantity and factor uncertainties",
        })
    return {
        "flow_count": len(flows),
        "source_count": len(source_ids),
        "phase_totals": results,
        "factor_library_supplied_by_project": False,
        "environmental_impact_or_lifecycle_certification_claimed": False,
    }

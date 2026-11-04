"""Non-operational, human-reviewed resource planning for civil-protection workflows."""
from __future__ import annotations
ALLOWED_RESOURCES = {"water", "medical_kit", "blanket", "radio", "food", "shelter_space"}

def _quantity(value, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label} must be a non-negative integer")
    return value

def plan_resources(needs: dict[str, int], available: dict[str, int]) -> dict:
    if not isinstance(needs, dict) or not isinstance(available, dict):
        raise TypeError("needs and available must be mappings")
    if any(resource not in ALLOWED_RESOURCES for resource in needs):
        raise ValueError("resource outside conservative rescue allowlist")
    allocations = {}
    shortages = {}
    for resource, amount in needs.items():
        amount = _quantity(amount, "resource quantities")
        stock = _quantity(available.get(resource, 0), "available stock")
        allocations[resource] = min(amount, stock)
        if allocations[resource] < amount:
            shortages[resource] = amount - allocations[resource]
    return {"allocations": allocations, "shortages": shortages, "requires_human_dispatch": True,
            "automated_dispatch": False, "medical_or_evacuation_decisions_not_automated": True}

def plan_fair_resources(requests: list[dict], available: dict[str, int]) -> dict:
    """Allocate by priority tier, proportionally within tied tiers using deterministic rounding."""
    if not isinstance(requests, list) or not isinstance(available, dict):
        raise TypeError("requests must be a list and available must be a mapping")
    for resource, stock in available.items():
        if resource not in ALLOWED_RESOURCES:
            raise ValueError("resource outside conservative rescue allowlist")
        _quantity(stock, "available stock")
    normalized = []
    seen_ids = set()
    for request in requests:
        if not isinstance(request, dict):
            raise TypeError("each request must be a mapping")
        request_id, priority, needs = request.get("request_id"), request.get("priority"), request.get("needs")
        if not isinstance(request_id, str) or not request_id.strip() or request_id in seen_ids:
            raise ValueError("request_id must be unique and non-empty")
        if isinstance(priority, bool) or not isinstance(priority, int) or not 1 <= priority <= 5:
            raise ValueError("priority must be an integer from 1 to 5")
        if not isinstance(needs, dict):
            raise TypeError("request needs must be a mapping")
        cleaned = {}
        for resource, amount in needs.items():
            if resource not in ALLOWED_RESOURCES:
                raise ValueError("resource outside conservative rescue allowlist")
            cleaned[resource] = _quantity(amount, "requested quantities")
        seen_ids.add(request_id)
        normalized.append({"request_id": request_id, "priority": priority, "needs": cleaned})
    allocations = {item["request_id"]: {} for item in normalized}
    shortages = {item["request_id"]: {} for item in normalized}
    resource_totals = {}
    resources = sorted({resource for item in normalized for resource in item["needs"]})
    for resource in resources:
        remaining = available.get(resource, 0)
        tiers = sorted({item["priority"] for item in normalized if item["needs"].get(resource, 0) > 0}, reverse=True)
        for priority in tiers:
            tier = [item for item in normalized if item["priority"] == priority and item["needs"].get(resource, 0) > 0]
            demand = sum(item["needs"][resource] for item in tier)
            if remaining >= demand:
                tier_allocations = {item["request_id"]: item["needs"][resource] for item in tier}
            else:
                exact = {item["request_id"]: remaining * item["needs"][resource] / demand for item in tier}
                tier_allocations = {
                    request_id: min(next(item["needs"][resource] for item in tier if item["request_id"] == request_id), int(value))
                    for request_id, value in exact.items()
                }
                unassigned = remaining - sum(tier_allocations.values())
                order = sorted(tier, key=lambda item: (
                    -(exact[item["request_id"]] - int(exact[item["request_id"]])), item["request_id"]
                ))
                for item in order:
                    if unassigned <= 0:
                        break
                    request_id = item["request_id"]
                    if tier_allocations[request_id] < item["needs"][resource]:
                        tier_allocations[request_id] += 1
                        unassigned -= 1
            used = sum(tier_allocations.values())
            for item in tier:
                request_id = item["request_id"]
                allocated = tier_allocations[request_id]
                allocations[request_id][resource] = allocated
                if allocated < item["needs"][resource]:
                    shortages[request_id][resource] = item["needs"][resource] - allocated
            remaining -= used
            if remaining <= 0:
                break
        resource_totals[resource] = {
            "available": available.get(resource, 0),
            "allocated": available.get(resource, 0) - remaining,
            "unallocated": remaining,
        }
    return {
        "allocations_by_request": allocations, "shortages_by_request": shortages,
        "resource_totals": resource_totals,
        "allocation_policy": "priority_then_proportional_largest_remainder",
        "requires_human_review": True, "requires_human_dispatch": True, "automated_dispatch": False,
        "medical_or_evacuation_decisions_not_automated": True,
    }

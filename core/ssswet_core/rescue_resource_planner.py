"""Non-operational resource planning for lawful civil-protection workflows."""
from __future__ import annotations

ALLOWED_RESOURCES = {"water", "medical_kit", "blanket", "radio", "food", "shelter_space"}
MAX_QUANTITY = 1_000_000_000


def _validate_inventory(values: dict[str, int], field: str) -> dict[str, int]:
    if not isinstance(values, dict):
        raise ValueError(f"{field} must be an object")
    cleaned = {}
    for resource, amount in values.items():
        if resource not in ALLOWED_RESOURCES:
            raise ValueError("resource outside conservative rescue allowlist")
        if isinstance(amount, bool) or not isinstance(amount, int) or not 0 <= amount <= MAX_QUANTITY:
            raise ValueError(f"{field} quantities must be integers between 0 and {MAX_QUANTITY}")
        cleaned[resource] = amount
    return cleaned


def plan_resources(needs: dict[str, int], available: dict[str, int]) -> dict:
    needs = _validate_inventory(needs, "needs")
    available = _validate_inventory(available, "available")
    allocations, shortages = {}, {}
    for resource, amount in sorted(needs.items()):
        stock = available.get(resource, 0)
        allocations[resource] = min(amount, stock)
        if allocations[resource] < amount:
            shortages[resource] = amount - allocations[resource]
    return {
        "allocations": allocations, "shortages": shortages,
        "remaining_stock": {key: available.get(key, 0) - allocations.get(key, 0) for key in sorted(set(available) | set(needs))},
        "requires_human_dispatch": True, "medical_or_evacuation_decisions_not_automated": True,
    }


def _fair_split(demands: dict[str, int], stock: int) -> dict[str, int]:
    """Max-min fair allocation for one priority tier, with deterministic remainders."""
    allocations = {request_id: 0 for request_id in demands}
    active = {request_id: amount for request_id, amount in demands.items() if amount > 0}
    remaining = stock
    while remaining > 0 and active:
        share, remainder = divmod(remaining, len(active))
        if share == 0:
            for request_id in sorted(active)[:remainder]:
                allocations[request_id] += 1
            remaining = 0
            break
        saturated = [request_id for request_id, amount in active.items() if amount <= share]
        if saturated:
            for request_id in sorted(saturated):
                amount = active.pop(request_id)
                allocations[request_id] += amount
                remaining -= amount
            continue
        for request_id in sorted(active):
            allocations[request_id] += share
            remaining -= share
        for request_id in sorted(active)[:remainder]:
            allocations[request_id] += 1
            remaining -= 1
        break
    return allocations


def plan_multiple_requests(requests: list[dict], available: dict[str, int]) -> dict:
    """Allocate listed supplies by priority, then max-min fairness within each tier."""
    stock = _validate_inventory(available, "available")
    if not isinstance(requests, list) or len(requests) > 100:
        raise ValueError("requests must be a list of at most 100 items")
    normalized, seen = [], set()
    for item in requests:
        if not isinstance(item, dict):
            raise ValueError("each request must be an object")
        request_id, priority = item.get("request_id"), item.get("priority", 1)
        if not isinstance(request_id, str) or not request_id.strip() or len(request_id) > 120:
            raise ValueError("request_id must contain 1 to 120 characters")
        request_id = request_id.strip()
        if request_id in seen:
            raise ValueError("request_id values must be unique")
        seen.add(request_id)
        if isinstance(priority, bool) or not isinstance(priority, int) or not 1 <= priority <= 5:
            raise ValueError("priority must be an integer from 1 (lower) to 5 (higher)")
        normalized.append({"request_id": request_id, "priority": priority, "needs": _validate_inventory(item.get("needs", {}), "needs")})
    allocations = {item["request_id"]: {} for item in normalized}
    for priority in sorted({item["priority"] for item in normalized}, reverse=True):
        tier = [item for item in normalized if item["priority"] == priority]
        for resource in sorted(ALLOWED_RESOURCES):
            demands = {item["request_id"]: item["needs"].get(resource, 0) for item in tier if item["needs"].get(resource, 0) > 0}
            split = _fair_split(demands, stock.get(resource, 0))
            stock[resource] = stock.get(resource, 0) - sum(split.values())
            for request_id, amount in split.items():
                if amount:
                    allocations[request_id][resource] = amount
    results = []
    for item in sorted(normalized, key=lambda value: (-value["priority"], value["request_id"])):
        granted = allocations[item["request_id"]]
        shortages = {resource: amount - granted.get(resource, 0) for resource, amount in sorted(item["needs"].items()) if amount > granted.get(resource, 0)}
        results.append({"request_id": item["request_id"], "priority": item["priority"], "allocations": dict(sorted(granted.items())), "shortages": shortages})
    return {
        "requests": results, "remaining_stock": dict(sorted(stock.items())),
        "priority_order": "higher priority first; max-min fair within each equal-priority tier",
        "requires_human_dispatch": True, "medical_or_evacuation_decisions_not_automated": True,
        "safety_or_legal_authorization_established": False,
    }

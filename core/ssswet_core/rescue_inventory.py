"""Freshness-aware civil-rescue stock planning with human-controlled dispatch."""
from __future__ import annotations
from datetime import date

MAX_LOTS = 500
MAX_REQUESTS = 100
MAX_QUANTITY = 1_000_000_000
ALLOWED_RESOURCES = {"water", "medical_kit", "blanket", "radio", "food", "shelter_space"}

def _date(value, field):
    if not isinstance(value, str):
        raise ValueError(f"{field} must be an ISO date")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO date") from exc

def _quantity(value, field):
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= MAX_QUANTITY:
        raise ValueError(f"{field} must be an integer between 0 and {MAX_QUANTITY}")
    return value

def _fair_split(demands: dict[str, int], stock: int) -> dict[str, int]:
    allocations = {key: 0 for key in demands}
    active = {key: value for key, value in demands.items() if value > 0}
    remaining = stock
    while active and remaining > 0:
        share, remainder = divmod(remaining, len(active))
        if share == 0:
            for key in sorted(active)[:remainder]:
                allocations[key] += 1
            break
        saturated = [key for key, need in active.items() if need <= share]
        if saturated:
            for key in sorted(saturated):
                amount = active.pop(key)
                allocations[key] += amount
                remaining -= amount
            continue
        for key in sorted(active):
            allocations[key] += share
            remaining -= share
        for key in sorted(active)[:remainder]:
            allocations[key] += 1
            remaining -= 1
        break
    return allocations

def plan_fresh_inventory(lots: list[dict], requests: list[dict], *, as_of: str, max_inspection_age_days: int = 30) -> dict:
    if not isinstance(lots, list) or len(lots) > MAX_LOTS:
        raise ValueError(f"lots must be a list of at most {MAX_LOTS} items")
    if not isinstance(requests, list) or len(requests) > MAX_REQUESTS:
        raise ValueError(f"requests must be a list of at most {MAX_REQUESTS} items")
    today = _date(as_of, "as_of")
    if isinstance(max_inspection_age_days, bool) or not isinstance(max_inspection_age_days, int) or not 0 <= max_inspection_age_days <= 3650:
        raise ValueError("max_inspection_age_days must be between 0 and 3650")
    eligible, excluded, seen_lots = [], [], set()
    for lot in lots:
        if not isinstance(lot, dict):
            raise ValueError("each lot must be an object")
        lot_id, resource = lot.get("lot_id"), lot.get("resource")
        if not isinstance(lot_id, str) or not lot_id.strip() or lot_id in seen_lots:
            raise ValueError("lot IDs must be unique non-empty strings")
        seen_lots.add(lot_id)
        if resource not in ALLOWED_RESOURCES:
            raise ValueError(f"unsupported rescue resource: {resource}")
        quantity = _quantity(lot.get("quantity"), "quantity")
        expiry, inspected = _date(lot.get("expires_on"), "expires_on"), _date(lot.get("inspected_on"), "inspected_on")
        if not isinstance(lot.get("quarantined", False), bool):
            raise ValueError("quarantined must be a boolean")
        reason = None
        if quantity == 0:
            reason = "zero_quantity"
        elif lot.get("quarantined", False):
            reason = "quarantined"
        elif expiry < today:
            reason = "expired"
        elif inspected > today:
            reason = "inspection_date_in_future"
        elif (today - inspected).days > max_inspection_age_days:
            reason = "inspection_overdue"
        elif lot.get("storage_status") != "verified":
            reason = "storage_condition_not_verified"
        if reason:
            excluded.append({"lot_id": lot_id, "reason": reason})
        else:
            eligible.append({"lot_id": lot_id, "resource": resource, "quantity": quantity,
                             "expires_on": expiry, "inspected_on": inspected})
    normalized, seen_requests = [], set()
    for item in requests:
        if not isinstance(item, dict):
            raise ValueError("each request must be an object")
        request_id, priority = item.get("request_id"), item.get("priority", 1)
        if not isinstance(request_id, str) or not request_id.strip() or request_id in seen_requests:
            raise ValueError("request IDs must be unique non-empty strings")
        seen_requests.add(request_id)
        if isinstance(priority, bool) or not isinstance(priority, int) or not 1 <= priority <= 5:
            raise ValueError("priority must be an integer from 1 to 5")
        needs = item.get("needs", {})
        if not isinstance(needs, dict) or any(key not in ALLOWED_RESOURCES for key in needs):
            raise ValueError("needs must contain supported resources")
        normalized.append({"request_id": request_id, "priority": priority,
                           "needs": {key: _quantity(value, "need") for key, value in needs.items()}})
    stock = {resource: sum(lot["quantity"] for lot in eligible if lot["resource"] == resource) for resource in ALLOWED_RESOURCES}
    allocations = {item["request_id"]: {} for item in normalized}
    remaining_by_lot = {lot["lot_id"]: lot["quantity"] for lot in eligible}
    for priority in sorted({item["priority"] for item in normalized}, reverse=True):
        tier = sorted((item for item in normalized if item["priority"] == priority), key=lambda item: item["request_id"])
        for resource in sorted(ALLOWED_RESOURCES):
            active = {item["request_id"]: item["needs"].get(resource, 0) for item in tier if item["needs"].get(resource, 0) > 0}
            shares = _fair_split(active, stock[resource])
            lots_for_resource = sorted((lot for lot in eligible if lot["resource"] == resource), key=lambda lot: (lot["expires_on"], lot["lot_id"]))
            for request_id in sorted(shares):
                need = shares[request_id]
                for lot in lots_for_resource:
                    available = remaining_by_lot[lot["lot_id"]]
                    amount = min(need, available)
                    if amount:
                        allocations[request_id].setdefault(resource, []).append({"lot_id": lot["lot_id"], "quantity": amount, "expires_on": lot["expires_on"].isoformat()})
                        remaining_by_lot[lot["lot_id"]] -= amount
                        need -= amount
                    if need == 0:
                        break
            stock[resource] -= sum(shares.values())
    results = []
    for item in sorted(normalized, key=lambda value: (-value["priority"], value["request_id"])):
        granted = {resource: sum(lot["quantity"] for lot in lots_used) for resource, lots_used in allocations[item["request_id"]].items()}
        shortages = {resource: amount - granted.get(resource, 0) for resource, amount in item["needs"].items() if amount > granted.get(resource, 0)}
        results.append({"request_id": item["request_id"], "priority": item["priority"],
                        "allocations": allocations[item["request_id"]], "granted_totals": granted, "shortages": shortages})
    remaining_lots = [{"lot_id": lot["lot_id"], "resource": lot["resource"], "quantity": remaining_by_lot[lot["lot_id"]]}
                      for lot in eligible if remaining_by_lot[lot["lot_id"]] > 0]
    return {
        "as_of": today.isoformat(), "requests": results, "excluded_lots": excluded,
        "remaining_eligible_lots": remaining_lots,
        "allocation_policy": "priority descending, max-min fair within equal-priority tiers, then first-expire-first-out",
        "expired_or_unverified_stock_allocated": False, "requires_human_dispatch": True,
        "medical_or_evacuation_decisions_automated": False, "legal_or_safety_authorization_established": False,
    }

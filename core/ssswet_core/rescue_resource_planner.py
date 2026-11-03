"""Non-operational rescue resource planning for lawful civil-protection workflows."""
from __future__ import annotations

ALLOWED_RESOURCES = {"water", "medical_kit", "blanket", "radio", "food", "shelter_space"}


def plan_resources(needs: dict[str, int], available: dict[str, int]) -> dict:
    if any(resource not in ALLOWED_RESOURCES for resource in needs):
        raise ValueError("resource outside conservative rescue allowlist")
    allocations = {}
    shortages = {}
    for resource, amount in needs.items():
        if isinstance(amount, bool) or not isinstance(amount, int) or amount < 0:
            raise ValueError("resource quantities must be non-negative integers")
        stock = max(0, int(available.get(resource, 0)))
        allocations[resource] = min(amount, stock)
        if allocations[resource] < amount:
            shortages[resource] = amount - allocations[resource]
    return {"allocations": allocations, "shortages": shortages, "requires_human_dispatch": True, "medical_or_evacuation_decisions_not_automated": True}

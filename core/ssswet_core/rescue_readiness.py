"""Human-controlled rescue workflow readiness checklist."""
from __future__ import annotations

CHECKS = ("location_confirmed", "communications_available", "resources_checked", "human_dispatch_confirmed", "medical_authority_available")


def assess(state: dict) -> dict:
    missing = [name for name in CHECKS if not bool(state.get(name))]
    return {"ready_for_human_review": not missing, "missing": missing, "automated_dispatch": False}

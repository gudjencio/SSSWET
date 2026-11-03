"""Deterministic locale fallback without silently inventing translations."""
from __future__ import annotations


def resolve(requested: str, available: list[str], default: str = "en") -> dict:
    available = sorted(set(available))
    requested = requested.replace("_", "-")
    candidates = [requested, requested.split("-")[0]]
    selected = next((item for item in candidates if item in available), None)
    if selected is None and default in available:
        selected = default
    return {"requested": requested, "selected": selected, "fallback_used": selected != requested, "translation_invented": False}

"""Detect likely source duplication before counting corroboration."""
from __future__ import annotations


def group_sources(sources: list[dict]) -> dict:
    groups = {}
    for source in sources:
        key = source.get("publisher") or source.get("doi") or source.get("domain") or source.get("id")
        groups.setdefault(str(key).casefold(), []).append(source.get("id"))
    return {key: sorted(value) for key, value in sorted(groups.items())}

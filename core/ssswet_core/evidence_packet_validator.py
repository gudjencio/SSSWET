"""Validate completeness of public evidence packets before review."""
from __future__ import annotations

REQUIRED = ("title", "summary", "source_ids", "method", "limitations")


def validate_packet(packet: dict) -> dict:
    missing = [key for key in REQUIRED if not packet.get(key)]
    sources = packet.get("source_ids", [])
    duplicate_sources = len(sources) != len(set(sources)) if isinstance(sources, list) else True
    if not isinstance(sources, list):
        missing.append("source_ids:list")
    return {"valid_for_review": not missing and not duplicate_sources, "missing": missing, "duplicate_sources": duplicate_sources, "scientific_validity_established": False}

"""Identify missing reproducibility inputs without judging scientific validity."""
from __future__ import annotations

REQUIRED = ("protocol_id", "protocol_version", "software_version", "dataset_refs", "parameters", "source_ids")


def inspect(manifest: dict, artifacts: dict | None = None) -> dict:
    missing = [field for field in REQUIRED if field not in manifest]
    artifacts = artifacts or {}
    missing_artifacts = sorted(name for name, present in artifacts.items() if not present)
    return {"complete": not missing and not missing_artifacts, "missing_fields": missing, "missing_artifacts": missing_artifacts, "scientific_validity_established": False}

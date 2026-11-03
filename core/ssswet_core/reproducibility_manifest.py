"""Canonical manifests for repeatable research runs."""
from __future__ import annotations
import json
from hashlib import sha256


def build_manifest(*, protocol_id: str, protocol_version: int, dataset_refs: list[dict], software_version: str, parameters: dict, source_ids: list[str]) -> dict:
    if not protocol_id.strip() or protocol_version < 1 or not software_version.strip():
        raise ValueError("protocol, version and software version are required")
    payload = {"protocol_id": protocol_id, "protocol_version": protocol_version, "dataset_refs": dataset_refs, "software_version": software_version, "parameters": parameters, "source_ids": sorted(set(source_ids))}
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return {**payload, "canonical_sha256": sha256(canonical.encode()).hexdigest(), "reproducibility_state": "manifest_complete"}


def compare_manifests(left: dict, right: dict) -> dict:
    keys = sorted(set(left) | set(right))
    differences = {key: {"left": left.get(key), "right": right.get(key)} for key in keys if left.get(key) != right.get(key)}
    return {"identical": not differences, "differences": differences, "comparison_is_scientific_validation": False}

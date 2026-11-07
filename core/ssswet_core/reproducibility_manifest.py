"""Canonical, verifiable manifests for repeatable research runs."""
from __future__ import annotations
import json
from hashlib import sha256

MAX_MANIFEST_CHARS = 250000


def _canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _flatten(value: object, prefix: str = "") -> dict[str, object]:
    result: dict[str, object] = {}
    if isinstance(value, dict):
        if not value and prefix:
            result[prefix] = {}
        for key in sorted(value):
            path = f"{prefix}.{key}" if prefix else str(key)
            result.update(_flatten(value[key], path))
    elif isinstance(value, list):
        if not value and prefix:
            result[prefix] = []
        for index, item in enumerate(value):
            result.update(_flatten(item, f"{prefix}[{index}]"))
    else:
        result[prefix] = value
    return result


def build_manifest(
    *, protocol_id: str, protocol_version: int, dataset_refs: list[dict],
    software_version: str, parameters: dict, source_ids: list[str],
    environment: dict | None = None, random_seed: int | str | None = None,
    input_checksums: dict | None = None,
) -> dict:
    if not isinstance(protocol_id, str) or not protocol_id.strip() or len(protocol_id) > 200:
        raise ValueError("protocol_id is required")
    if isinstance(protocol_version, bool) or not isinstance(protocol_version, int) or protocol_version < 1:
        raise ValueError("protocol_version must be a positive integer")
    if not isinstance(software_version, str) or not software_version.strip() or len(software_version) > 200:
        raise ValueError("software_version is required")
    if not isinstance(dataset_refs, list) or len(dataset_refs) > 500 or any(not isinstance(item, dict) for item in dataset_refs):
        raise ValueError("dataset_refs must be a list of at most 500 objects")
    if not isinstance(parameters, dict) or not isinstance(source_ids, list) or len(source_ids) > 1000:
        raise ValueError("parameters must be an object and source_ids a list of at most 1000 items")
    if any(not isinstance(item, str) or not item.strip() for item in source_ids):
        raise ValueError("source_ids must contain non-empty strings")
    if environment is not None and not isinstance(environment, dict):
        raise ValueError("environment must be an object")
    if input_checksums is not None and not isinstance(input_checksums, dict):
        raise ValueError("input_checksums must be an object")
    if random_seed is not None and (isinstance(random_seed, bool) or not isinstance(random_seed, (int, str))):
        raise ValueError("random_seed must be an integer, string or null")
    payload = {
        "schema_version": 1, "protocol_id": protocol_id.strip(),
        "protocol_version": protocol_version, "dataset_refs": sorted(dataset_refs, key=_canonical),
        "software_version": software_version.strip(), "parameters": parameters,
        "source_ids": sorted(set(source_ids)), "environment": environment or {},
        "random_seed": random_seed, "input_checksums": input_checksums or {},
        "reproducibility_state": "manifest_complete", "scientific_validity_established": False,
    }
    canonical = _canonical(payload)
    if len(canonical) > MAX_MANIFEST_CHARS:
        raise ValueError(f"manifest exceeds {MAX_MANIFEST_CHARS} characters")
    return {**payload, "canonical_sha256": sha256(canonical.encode("utf-8")).hexdigest()}


def verify_manifest(manifest: dict) -> dict:
    if not isinstance(manifest, dict):
        raise ValueError("manifest must be an object")
    recorded = manifest.get("canonical_sha256")
    payload = {key: value for key, value in manifest.items() if key not in {"canonical_sha256", "verification"}}
    try:
        canonical = _canonical(payload)
    except (TypeError, ValueError) as exc:
        raise ValueError("manifest must contain JSON-compatible finite values") from exc
    if len(canonical) > MAX_MANIFEST_CHARS:
        raise ValueError(f"manifest exceeds {MAX_MANIFEST_CHARS} characters")
    expected = sha256(canonical.encode("utf-8")).hexdigest()
    return {
        "valid": isinstance(recorded, str) and recorded == expected,
        "recorded_sha256": recorded, "expected_sha256": expected,
        "tampered_or_incomplete": not (isinstance(recorded, str) and recorded == expected),
    }


def compare_manifests(left: dict, right: dict) -> dict:
    if not isinstance(left, dict) or not isinstance(right, dict):
        raise ValueError("both manifests must be objects")
    keys = sorted(set(left) | set(right))
    differences = {
        key: {"left": left.get(key), "right": right.get(key)}
        for key in keys if left.get(key) != right.get(key) or (key in left) != (key in right)
    }
    left_flat, right_flat = _flatten(left), _flatten(right)
    paths = sorted(set(left_flat) | set(right_flat))
    changed_paths = [
        {"path": path, "left": left_flat.get(path), "right": right_flat.get(path)}
        for path in paths if left_flat.get(path) != right_flat.get(path) or (path in left_flat) != (path in right_flat)
    ]
    return {
        "identical": not differences, "differences": differences,
        "changed_paths": changed_paths, "comparison_is_scientific_validation": False,
    }

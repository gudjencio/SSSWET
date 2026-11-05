"""Canonical, verifiable manifests for repeatable research runs."""
from __future__ import annotations

import json
from hashlib import sha256


_PAYLOAD_FIELDS = ("protocol_id", "protocol_version", "dataset_refs", "software_version", "parameters", "source_ids")


def _canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def build_manifest(*, protocol_id: str, protocol_version: int, dataset_refs: list[dict],
                   software_version: str, parameters: dict, source_ids: list[str]) -> dict:
    if not isinstance(protocol_id, str) or not protocol_id.strip():
        raise ValueError("protocol_id is required")
    if isinstance(protocol_version, bool) or not isinstance(protocol_version, int) or protocol_version < 1:
        raise ValueError("protocol_version must be a positive integer")
    if not isinstance(software_version, str) or not software_version.strip():
        raise ValueError("software_version is required")
    if not isinstance(dataset_refs, list) or any(not isinstance(item, dict) for item in dataset_refs):
        raise ValueError("dataset_refs must be a list of dictionaries")
    canonical_refs = []
    seen_refs = set()
    for item in dataset_refs:
        try:
            encoded = _canonical(item)
        except (TypeError, ValueError) as exc:
            raise ValueError("dataset references must be finite JSON-compatible dictionaries") from exc
        if encoded in seen_refs:
            raise ValueError("duplicate dataset reference")
        seen_refs.add(encoded)
        canonical_refs.append(json.loads(encoded))
    canonical_refs.sort(key=_canonical)
    if not isinstance(parameters, dict):
        raise ValueError("parameters must be a dictionary")
    try:
        canonical_parameters = json.loads(_canonical(parameters))
    except (TypeError, ValueError) as exc:
        raise ValueError("parameters must be finite JSON-compatible values") from exc
    if not isinstance(source_ids, list) or any(not isinstance(item, str) or not item.strip() for item in source_ids):
        raise ValueError("source_ids must be a list of non-empty strings")
    payload = {
        "protocol_id": protocol_id.strip(),
        "protocol_version": protocol_version,
        "dataset_refs": canonical_refs,
        "software_version": software_version.strip(),
        "parameters": canonical_parameters,
        "source_ids": sorted({item.strip() for item in source_ids}),
    }
    digest = sha256(_canonical(payload).encode("utf-8")).hexdigest()
    return {**payload, "canonical_sha256": digest, "reproducibility_state": "manifest_complete"}


def verify_manifest(manifest: dict) -> dict:
    if not isinstance(manifest, dict):
        return {"valid": False, "reason": "manifest_not_a_dictionary"}
    missing = [field for field in _PAYLOAD_FIELDS + ("canonical_sha256",) if field not in manifest]
    if missing:
        return {"valid": False, "reason": "missing_fields", "missing_fields": missing}
    payload = {field: manifest[field] for field in _PAYLOAD_FIELDS}
    try:
        actual = sha256(_canonical(payload).encode("utf-8")).hexdigest()
    except (TypeError, ValueError):
        return {"valid": False, "reason": "non_canonical_payload"}
    expected = manifest.get("canonical_sha256")
    return {"valid": isinstance(expected, str) and actual == expected,
            "expected_fingerprint": expected, "actual_fingerprint": actual,
            "reason": "" if actual == expected else "fingerprint_mismatch"}


def compare_manifests(left: dict, right: dict) -> dict:
    left_integrity = verify_manifest(left)
    right_integrity = verify_manifest(right)
    keys = sorted(set(left) | set(right))
    differences = {key: {"left": left.get(key), "right": right.get(key)}
                   for key in keys if left.get(key) != right.get(key)}
    return {
        "identical": not differences,
        "differences": differences,
        "left_integrity": left_integrity,
        "right_integrity": right_integrity,
        "comparison_is_scientific_validation": False,
    }

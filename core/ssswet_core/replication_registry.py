"""Append-only run fingerprint registry for transparent replication comparisons."""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any

MAX_ATTEMPTS = 2_000
MAX_DATASETS = 100
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_OUTCOMES = {"positive", "negative", "inconclusive", "failed", "not_run"}
_FINGERPRINT_FIELDS = ("protocol_fingerprint", "environment_fingerprint", "analysis_fingerprint")


def _canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _identifier(value: Any, field: str, maximum: int = 160) -> str:
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > maximum:
        raise ValueError(f"{field} must contain 1 to {maximum} characters")
    return value.strip()


def _digest(value: Any, field: str) -> str:
    if not isinstance(value, str) or not _DIGEST.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase SHA-256 digest")
    return value


class ReplicationRegistry:
    """In-memory append-only registry; persistence remains the caller's responsibility."""

    def __init__(self) -> None:
        self._records: dict[str, dict[str, Any]] = {}

    def record_attempt(
        self, *, run_id: str, protocol_fingerprint: str,
        dataset_fingerprints: list[str], environment_fingerprint: str,
        analysis_fingerprint: str, outcome: str,
        deviation_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        run_id = _identifier(run_id, "run_id")
        if run_id in self._records:
            raise ValueError("run_id already exists; attempts are append-only")
        if len(self._records) >= MAX_ATTEMPTS:
            raise ValueError(f"registry is limited to {MAX_ATTEMPTS} attempts")
        fingerprints = {
            field: _digest(value, field)
            for field, value in (
                ("protocol_fingerprint", protocol_fingerprint),
                ("environment_fingerprint", environment_fingerprint),
                ("analysis_fingerprint", analysis_fingerprint),
            )
        }
        if not isinstance(dataset_fingerprints, list) or len(dataset_fingerprints) > MAX_DATASETS:
            raise ValueError(f"dataset_fingerprints must be a list of at most {MAX_DATASETS} digests")
        datasets = [_digest(item, "dataset_fingerprint") for item in dataset_fingerprints]
        if len(datasets) != len(set(datasets)):
            raise ValueError("dataset_fingerprints must be unique")
        if outcome not in _OUTCOMES:
            raise ValueError("outcome must be positive, negative, inconclusive, failed or not_run")
        deviations = deviation_ids or []
        if not isinstance(deviations, list) or len(deviations) > 100:
            raise ValueError("deviation_ids must be a list of at most 100 identifiers")
        deviations = sorted({_identifier(item, "deviation_id") for item in deviations})
        if len(deviations) != len(deviation_ids or []):
            raise ValueError("deviation_ids must be unique")
        payload = {
            "schema_version": 1, "run_id": run_id, **fingerprints,
            "dataset_fingerprints": sorted(datasets), "outcome": outcome,
            "deviation_ids": deviations,
        }
        payload["record_fingerprint"] = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()
        self._records[run_id] = payload
        return json.loads(_canonical(payload))

    def compare(self, left_run_id: str, right_run_id: str) -> dict[str, Any]:
        left_id = _identifier(left_run_id, "left_run_id")
        right_id = _identifier(right_run_id, "right_run_id")
        if left_id not in self._records or right_id not in self._records:
            raise ValueError("both run IDs must exist in the registry")
        left, right = self._records[left_id], self._records[right_id]
        fields = (*_FINGERPRINT_FIELDS, "dataset_fingerprints", "deviation_ids")
        differences = [
            {"field": field, "left": left[field], "right": right[field]}
            for field in fields if left[field] != right[field]
        ]
        protocol_match = left["protocol_fingerprint"] == right["protocol_fingerprint"]
        return {
            "left_run_id": left_id, "right_run_id": right_id,
            "protocol_match": protocol_match,
            "matching_fields": [field for field in fields if left[field] == right[field]],
            "differences": differences,
            "comparability": (
                "same_declared_inputs_and_method"
                if not differences else
                "protocol_mismatch" if not protocol_match else "partial_match"
            ),
            "outcomes": {"left": left["outcome"], "right": right["outcome"]},
            "replication_success_established": False,
            "scientific_validity_established": False,
        }

    def get(self, run_id: str) -> dict[str, Any] | None:
        record = self._records.get(str(run_id))
        return None if record is None else json.loads(_canonical(record))

    def export(self, *, limit: int = 500) -> list[dict[str, Any]]:
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= MAX_ATTEMPTS:
            raise ValueError(f"limit must be between 1 and {MAX_ATTEMPTS}")
        records = list(self._records.values())[-limit:]
        return [json.loads(_canonical(item)) for item in records]

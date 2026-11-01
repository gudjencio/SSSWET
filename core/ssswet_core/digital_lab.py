"""Shared digital laboratory: versioned protocols and auditable run comparisons.

This module records researcher-supplied protocols and execution results. It does
not execute laboratory work, run arbitrary submitted code, or certify a
reproduction. Simulation and real-observation records remain distinct.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
from math import isfinite
from typing import Any
import json


PROTOCOL_STATES = {"draft", "published", "withdrawn"}
RUN_KINDS = {"simulation", "real_observation"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False)


@dataclass(frozen=True)
class LabProtocol:
    protocol_id: str
    version: int
    title: str
    objective: str
    owner_campaign_id: str
    procedure: tuple[str, ...]
    required_parameters: tuple[str, ...]
    expected_outputs: tuple[str, ...]
    units: dict[str, str]
    controls: tuple[str, ...]
    limitations: tuple[str, ...]
    safety_notes: tuple[str, ...]
    state: str = "draft"
    reviewed_by: str = ""
    review_note: str = ""
    created_at: str = ""
    content_hash: str = ""

    def __post_init__(self):
        required = (self.protocol_id, self.title, self.objective, self.owner_campaign_id)
        if any(not isinstance(x, str) or not x.strip() for x in required):
            raise ValueError("Protocol ID, title, objective and owner campaign are required")
        if not isinstance(self.version, int) or self.version < 1:
            raise ValueError("Protocol version must be a positive integer")
        if self.state not in PROTOCOL_STATES:
            raise ValueError("Unsupported protocol state")
        for values in (self.procedure, self.required_parameters, self.expected_outputs):
            if len(set(values)) != len(values) or any(not x.strip() for x in values):
                raise ValueError("Protocol lists must contain unique, non-empty values")
        if self.state == "published" and (not self.reviewed_by.strip() or not self.review_note.strip()):
            raise ValueError("Publishing requires a named reviewer and a review note")


@dataclass(frozen=True)
class LabRun:
    run_id: str
    protocol_id: str
    protocol_version: int
    campaign_id: str
    kind: str
    parameters: dict[str, Any]
    outputs: dict[str, Any]
    method: str
    environment: dict[str, Any]
    code_or_model_reference: str
    provenance_group: str
    independence_declared: bool
    limitations: tuple[str, ...] = ()
    recorded_at: str = ""
    record_hash: str = ""
    source_ids: tuple[str, ...] = ()
    dataset_ids: tuple[str, ...] = ()

    def __post_init__(self):
        required = (self.run_id, self.protocol_id, self.campaign_id, self.method)
        if any(not isinstance(x, str) or not x.strip() for x in required):
            raise ValueError("Run ID, protocol, campaign and method are required")
        if self.protocol_version < 1 or self.kind not in RUN_KINDS:
            raise ValueError("Invalid protocol version or execution kind")
        if not isinstance(self.parameters, dict) or not isinstance(self.outputs, dict):
            raise ValueError("Run parameters and outputs must be objects")
        if not isinstance(self.environment, dict):
            raise ValueError("Run environment must be an object")
        if not isinstance(self.independence_declared, bool):
            raise ValueError("Independence must be explicitly declared")
        if len(set(self.source_ids)) != len(self.source_ids) or len(set(self.dataset_ids)) != len(self.dataset_ids):
            raise ValueError("Source and dataset identifiers must be unique")
        _canonical(self.parameters)
        _canonical(self.outputs)
        _canonical(self.environment)


def _verify_fingerprint(record: dict, field: str) -> bool:
    """Verify a stored protocol/run against its canonical SHA-256 fingerprint."""
    digest = record.get(field)
    if not isinstance(digest, str) or len(digest) != 64:
        return False
    payload = dict(record)
    payload[field] = ""
    try:
        actual = sha256(_canonical(payload).encode("utf-8")).hexdigest()
    except (TypeError, ValueError):
        return False
    return actual == digest


def _compare_values(left: Any, right: Any, tolerance: float, path: str = "") -> list[dict]:
    if isinstance(left, dict) and isinstance(right, dict):
        differences = []
        for key in sorted(set(left) | set(right)):
            child = f"{path}.{key}" if path else str(key)
            if key not in left or key not in right:
                differences.append({"field": child, "left": left.get(key), "right": right.get(key), "reason": "missing_key"})
            else:
                differences.extend(_compare_values(left[key], right[key], tolerance, child))
        return differences
    if isinstance(left, list) and isinstance(right, list):
        if len(left) != len(right):
            return [{"field": path, "left": left, "right": right, "reason": "different_length"}]
        return [item for i, (a, b) in enumerate(zip(left, right))
                for item in _compare_values(a, b, tolerance, f"{path}[{i}]")]
    if isinstance(left, (int, float)) and not isinstance(left, bool) and isinstance(right, (int, float)) and not isinstance(right, bool):
        return [] if abs(float(left) - float(right)) <= tolerance else [
            {"field": path, "left": left, "right": right, "reason": "outside_tolerance"}
        ]
    return [] if type(left) is type(right) and left == right else [
        {"field": path, "left": left, "right": right, "reason": "different_value"}
    ]


class DigitalLabService:
    def __init__(self, store):
        self.store = store

    def publish_protocol(self, protocol: LabProtocol) -> dict:
        if protocol.state != "published":
            raise ValueError("Only an explicitly reviewed published protocol can be shared")
        if not protocol.procedure or not protocol.required_parameters or not protocol.expected_outputs:
            raise ValueError("Published protocols require procedure, parameters and expected outputs")
        if not protocol.controls or not protocol.limitations:
            raise ValueError("Published protocols require controls and stated limitations")
        from dataclasses import replace
        protocol = replace(protocol, created_at=protocol.created_at or _now(), content_hash="")
        payload = asdict(protocol)
        digest = sha256(_canonical(payload).encode("utf-8")).hexdigest()
        protocol = replace(protocol, content_hash=digest)
        return self.store.save_lab_protocol(protocol)

    def record_run(self, run: LabRun) -> dict:
        protocol = self.store.get_lab_protocol(run.protocol_id, run.protocol_version)
        if protocol is None or protocol["state"] != "published":
            raise ValueError("Run requires an existing published protocol version")
        if not _verify_fingerprint(protocol, "content_hash"):
            raise ValueError("Published protocol fingerprint check failed; the record may have been altered")
        if run.campaign_id == protocol["owner_campaign_id"]:
            raise ValueError("A reproduction run must be recorded by another campaign")
        if not set(protocol["required_parameters"]).issubset(run.parameters):
            raise ValueError("Run is missing required protocol parameters")
        if not set(protocol["expected_outputs"]).issubset(run.outputs):
            raise ValueError("Run is missing expected protocol outputs")
        if run.kind not in RUN_KINDS:
            raise ValueError("Unsupported run kind")
        from dataclasses import replace
        run = replace(run, recorded_at=run.recorded_at or _now(), record_hash="")
        digest = sha256(_canonical(asdict(run)).encode("utf-8")).hexdigest()
        run = replace(run, record_hash=digest)
        return self.store.save_lab_run(run)

    def compare_runs(self, left_run_id: str, right_run_id: str, tolerance: float = 0.0) -> dict:
        if isinstance(tolerance, bool) or not isinstance(tolerance, (int, float)) or not isfinite(tolerance) or tolerance < 0:
            raise ValueError("Tolerance must be a finite, non-negative number")
        tolerance = float(tolerance)
        left = self.store.get_lab_run(left_run_id)
        right = self.store.get_lab_run(right_run_id)
        if left is None or right is None:
            raise ValueError("Both lab runs must exist")
        if left_run_id == right_run_id:
            raise ValueError("A run cannot be compared with itself")
        if not _verify_fingerprint(left, "record_hash") or not _verify_fingerprint(right, "record_hash"):
            raise ValueError("Lab run fingerprint check failed; a record may have been altered")
        same_protocol = (
            left["protocol_id"] == right["protocol_id"]
            and left["protocol_version"] == right["protocol_version"]
        )
        same_kind = left["kind"] == right["kind"]
        same_parameters = _canonical(left["parameters"]) == _canonical(right["parameters"])
        differences = _compare_values(left["outputs"], right["outputs"], tolerance)
        comparable = same_protocol and same_kind and same_parameters
        shared_source_ids = sorted(set(left.get("source_ids", [])) & set(right.get("source_ids", [])))
        shared_dataset_ids = sorted(set(left.get("dataset_ids", [])) & set(right.get("dataset_ids", [])))
        distinct_provenance_groups = bool(
            left.get("provenance_group") and right.get("provenance_group")
            and left["provenance_group"] != right["provenance_group"]
        )
        result = {
            "comparison_id": sha256(f"{left_run_id}|{right_run_id}|{tolerance}".encode()).hexdigest(),
            "left_run_id": left_run_id,
            "right_run_id": right_run_id,
            "same_protocol_version": same_protocol,
            "same_execution_kind": same_kind,
            "same_parameters": same_parameters,
            "different_campaigns": left["campaign_id"] != right["campaign_id"],
            "independence_declared_by_both": bool(left["independence_declared"] and right["independence_declared"]),
            "independence_independently_verified": False,
            "provenance_groups_distinct": distinct_provenance_groups,
            "shared_source_ids": shared_source_ids,
            "shared_dataset_ids": shared_dataset_ids,
            "comparable": comparable,
            "independent_reproduction_candidate": (
                comparable and left["campaign_id"] != right["campaign_id"]
                and left["independence_declared"] and right["independence_declared"]
                and distinct_provenance_groups and not shared_source_ids and not shared_dataset_ids
            ),
            "outputs_match_within_tolerance": comparable and not differences,
            "tolerance": tolerance,
            "differences": differences,
            "left_provenance_group": left["provenance_group"],
            "right_provenance_group": right["provenance_group"],
            "requires_human_review": True,
            "scientific_validity_established": False,
            "interpretation": "Matching recorded outputs do not establish model validity or scientific truth." if comparable and not differences else "Differences or incompatible run conditions require investigation; no run is selected as correct.",
            "compared_at": _now(),
            "source_ids": sorted(set(left.get("source_ids", [])) | set(right.get("source_ids", []))),
            "dataset_ids": sorted(set(left.get("dataset_ids", [])) | set(right.get("dataset_ids", []))),
        }
        return self.store.save_lab_comparison(result)

    def overview(self, limit: int = 200) -> dict:
        protocols = self.store.lab_protocol_history(limit=limit)
        runs = self.store.lab_run_history(limit=limit)
        comparisons = self.store.lab_comparison_history(limit=limit)
        protocol_integrity = [
            {"protocol_id": item.get("protocol_id"), "version": item.get("version"),
             "intact": _verify_fingerprint(item, "content_hash")}
            for item in protocols
        ]
        run_integrity = [
            {"run_id": item.get("run_id"),
             "intact": _verify_fingerprint(item, "record_hash")}
            for item in runs
        ]
        return {
            "protocols": protocols,
            "runs": runs,
            "comparisons": comparisons,
            "integrity": {
                "protocols_checked": len(protocol_integrity),
                "runs_checked": len(run_integrity),
                "all_intact": all(x["intact"] for x in protocol_integrity + run_integrity),
                "protocols": protocol_integrity,
                "runs": run_integrity,
            },
            "protocol_count": len(protocols),
            "run_count": len(runs),
            "comparison_count": len(comparisons),
            "scientific_validity_established": False,
            "automatic_execution": False,
        }

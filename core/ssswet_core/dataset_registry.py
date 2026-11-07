"""Immutable, provenance-aware registry for researcher-supplied datasets.

The registry stores metadata and declared content digests, not dataset files.
A digest identifies byte-identical content only when computed over the same bytes;
it does not establish quality, legality, representativeness or scientific truth.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
import re

PRIVACY_CLASSIFICATIONS = {"unspecified", "public", "internal", "confidential", "personal_data", "sensitive_data"}
CONSENT_STATES = {"not_recorded", "not_required", "documented", "pending", "withdrawn"}
ACCESS_SCOPES = {"public", "project", "restricted"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


@dataclass(frozen=True)
class DatasetVersion:
    dataset_id: str
    version: int
    title: str
    description: str
    campaign_id: str
    license: str
    source_ids: tuple[str, ...]
    content_sha256: str = ""
    parent_version: int = 0
    metadata: dict | None = None
    registered_at: str = ""
    record_fingerprint: str = ""
    privacy_classification: str = "unspecified"
    consent_status: str = "not_recorded"
    retention_policy: str = "not_recorded"
    access_scope: str = "restricted"

    def __post_init__(self):
        for value in (self.dataset_id, self.title, self.description, self.campaign_id, self.license):
            if not isinstance(value, str) or not value.strip():
                raise ValueError("Dataset identity, description, campaign and license are required")
        if isinstance(self.version, bool) or not isinstance(self.version, int) or self.version < 1:
            raise ValueError("Dataset version must be a positive integer")
        if isinstance(self.parent_version, bool) or not isinstance(self.parent_version, int) or self.parent_version < 0:
            raise ValueError("Parent version must be a non-negative integer")
        if self.parent_version >= self.version and self.parent_version != 0:
            raise ValueError("Parent version must be an earlier version")
        if self.content_sha256 and not re.fullmatch(r"[0-9a-f]{64}", self.content_sha256):
            raise ValueError("Content SHA-256 must be 64 lowercase hexadecimal characters")
        if not isinstance(self.source_ids, (tuple, list)) or len(self.source_ids) > 1000 or any(not isinstance(item, str) or not item.strip() for item in self.source_ids):
            raise ValueError("Dataset source identifiers must be a list of at most 1000 non-empty strings")
        if len(set(self.source_ids)) != len(self.source_ids):
            raise ValueError("Dataset source identifiers must be unique")
        if self.privacy_classification not in PRIVACY_CLASSIFICATIONS:
            raise ValueError("Unsupported privacy classification")
        if self.consent_status not in CONSENT_STATES:
            raise ValueError("Unsupported consent status")
        if self.access_scope not in ACCESS_SCOPES:
            raise ValueError("Unsupported dataset access scope")
        if not isinstance(self.retention_policy, str) or not self.retention_policy.strip() or len(self.retention_policy) > 500:
            raise ValueError("retention_policy must contain 1 to 500 characters")
        if self.metadata is not None and len(_canonical(self.metadata)) > 50000:
            raise ValueError("dataset metadata exceeds 50000 characters")


@dataclass(frozen=True)
class DatasetTransformation:
    transformation_id: str
    dataset_id: str
    input_version: int
    output_version: int
    operation: str
    parameters: dict
    software: str
    performed_by: str
    limitations: str
    recorded_at: str = ""

    def __post_init__(self):
        required = (self.transformation_id, self.dataset_id, self.operation, self.software, self.performed_by, self.limitations)
        if any(not isinstance(x, str) or not x.strip() for x in required):
            raise ValueError("Transformation identity, operation, software, operator and limitations are required")
        if isinstance(self.input_version, bool) or isinstance(self.output_version, bool) or not isinstance(self.input_version, int) or not isinstance(self.output_version, int) or self.input_version < 1 or self.output_version <= self.input_version:
            raise ValueError("Transformation output must be a later dataset version")
        if len(_canonical(self.parameters)) > 50000:
            raise ValueError("transformation parameters exceed 50000 characters")


def _valid_record(record: dict) -> bool:
    digest = record.get("record_fingerprint", "")
    if not isinstance(digest, str) or len(digest) != 64:
        return False
    payload = dict(record)
    payload["record_fingerprint"] = ""
    try:
        return sha256(_canonical(payload).encode("utf-8")).hexdigest() == digest
    except (TypeError, ValueError):
        return False


def governance_issues(record: dict) -> list[str]:
    """Return review flags for declared governance metadata; this is not legal advice."""
    issues = []
    if record.get("privacy_classification", "unspecified") == "unspecified":
        issues.append("privacy_classification_not_recorded")
    consent = record.get("consent_status", "not_recorded")
    if consent == "not_recorded":
        issues.append("consent_status_not_recorded")
    if consent == "pending":
        issues.append("consent_review_pending")
    if consent == "withdrawn":
        issues.append("consent_withdrawn")
    privacy = record.get("privacy_classification", "unspecified")
    if privacy in {"personal_data", "sensitive_data"} and consent not in {"documented", "not_required"}:
        issues.append("consent_or_other_lawful_basis_review_required")
    if privacy in {"personal_data", "sensitive_data"} and record.get("access_scope") == "public":
        issues.append("public_access_for_personal_data")
    retention = record.get("retention_policy", "not_recorded")
    if not isinstance(retention, str) or not retention.strip() or retention == "not_recorded":
        issues.append("retention_policy_not_recorded")
    license_value = str(record.get("license", "")).strip().casefold()
    if license_value in {"", "unknown", "unspecified", "not known"}:
        issues.append("license_terms_not_recorded")
    return sorted(set(issues))


class DatasetRegistry:
    def __init__(self, store):
        self.store = store

    def register_version(self, dataset: DatasetVersion) -> dict:
        if dataset.version == 1 and dataset.parent_version != 0:
            raise ValueError("The first dataset version cannot have a parent")
        if dataset.version > 1 and dataset.parent_version != dataset.version - 1:
            raise ValueError("A new dataset version must identify its immediately preceding version")
        record = asdict(dataset)
        record["registered_at"] = dataset.registered_at or _now()
        record["record_fingerprint"] = ""
        record["record_fingerprint"] = sha256(_canonical(record).encode("utf-8")).hexdigest()
        return self.store.save_lab_dataset(record)

    def record_transformation(self, transformation: DatasetTransformation) -> dict:
        source = self.store.get_lab_dataset(transformation.dataset_id, transformation.input_version)
        target = self.store.get_lab_dataset(transformation.dataset_id, transformation.output_version)
        if source is None or target is None:
            raise ValueError("unknown dataset version: transformation input and output must both be registered")
        if target.get("parent_version") != transformation.input_version:
            raise ValueError("Output dataset version must declare the transformation input as its parent")
        record = asdict(transformation)
        record["recorded_at"] = transformation.recorded_at or _now()
        return self.store.save_lab_dataset_transformation(record)

    def overview(self, limit: int = 200) -> dict:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1000:
            raise ValueError("limit must be an integer between 1 and 1000")
        versions = self.store.lab_dataset_history(limit=limit)
        transformations = self.store.lab_dataset_transformation_history(limit=limit)
        integrity = [{"dataset_id": item.get("dataset_id"), "version": item.get("version"), "intact": _valid_record(item)} for item in versions]
        by_digest: dict[str, list[dict]] = {}
        for item in versions:
            digest = item.get("content_sha256", "")
            if digest:
                by_digest.setdefault(digest, []).append({
                    "dataset_id": item.get("dataset_id"), "version": item.get("version"), "campaign_id": item.get("campaign_id"),
                })
        shared_content = [
            {"content_sha256": digest, "records": entries,
             "campaigns": sorted({entry["campaign_id"] for entry in entries}),
             "cross_campaign": len({entry["campaign_id"] for entry in entries}) > 1}
            for digest, entries in sorted(by_digest.items()) if len(entries) > 1
        ]
        governance = [
            {"dataset_id": item.get("dataset_id"), "version": item.get("version"), "issues": governance_issues(item)}
            for item in versions
        ]
        return {
            "datasets": versions, "transformations": transformations,
            "integrity": {"versions_checked": len(integrity), "all_intact": all(item["intact"] for item in integrity), "versions": integrity},
            "governance": {
                "versions_checked": len(governance),
                "versions_with_flags": sum(bool(item["issues"]) for item in governance),
                "all_review_flags_clear": all(not item["issues"] for item in governance),
                "versions": governance, "legal_compliance_established": False,
            },
            "shared_content_candidates": shared_content,
            "dataset_count": len({item["dataset_id"] for item in versions}),
            "version_count": len(versions), "transformation_count": len(transformations),
            "files_stored": False, "scientific_validity_established": False,
        }

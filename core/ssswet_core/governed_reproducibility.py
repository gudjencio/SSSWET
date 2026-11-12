"""Governance-gated reproducibility manifests for registered datasets."""
from __future__ import annotations

from typing import Any

from .dataset_registry import governance_issues
from .reproducibility_manifest import build_manifest

MAX_DATASET_REFS = 500
SCOPES = {"internal", "project", "public"}


def build_governed_manifest(
    store: Any,
    *,
    protocol_id: str,
    protocol_version: int,
    dataset_refs: list[dict],
    software_version: str,
    parameters: dict,
    source_ids: list[str],
    publication_scope: str = "internal",
    environment: dict | None = None,
    random_seed: int | str | None = None,
    input_checksums: dict | None = None,
) -> dict:
    """Gate manifest creation on declared dataset access and governance metadata.

    This is a workflow safeguard, not a legal-compliance or ethics approval.
    """
    if publication_scope not in SCOPES:
        raise ValueError("publication_scope must be internal, project or public")
    if environment is not None and not isinstance(environment, dict):
        raise ValueError("environment must be an object")
    if not isinstance(dataset_refs, list) or len(dataset_refs) > MAX_DATASET_REFS:
        raise ValueError(f"dataset_refs must be a list of at most {MAX_DATASET_REFS} records")

    blockers: list[dict] = []
    warnings: list[dict] = []
    normalized_refs = []
    seen = set()
    for ref in dataset_refs:
        if not isinstance(ref, dict):
            raise ValueError("each dataset reference must be an object")
        dataset_id = ref.get("dataset_id")
        version = ref.get("version")
        if not isinstance(dataset_id, str) or not dataset_id.strip():
            raise ValueError("each dataset reference requires dataset_id")
        if isinstance(version, bool) or not isinstance(version, int) or version < 1:
            raise ValueError("each dataset reference requires a positive integer version")
        key = (dataset_id.strip(), version)
        if key in seen:
            raise ValueError("dataset references must be unique")
        seen.add(key)
        record = store.get_lab_dataset(*key)
        if record is None:
            blockers.append({
                "dataset_id": key[0], "version": version,
                "code": "dataset_version_not_registered",
            })
            continue

        privacy = record.get("privacy_classification", "unspecified")
        consent = record.get("consent_status", "not_recorded")
        access = record.get("access_scope", "restricted")
        metadata = record.get("metadata") if isinstance(record.get("metadata"), dict) else {}
        license_value = str(record.get("license", "")).strip().casefold()
        if consent == "withdrawn":
            blockers.append({"dataset_id": key[0], "version": version, "code": "consent_withdrawn"})
        if privacy in {"personal_data", "sensitive_data"} and consent not in {"documented", "not_required"}:
            blockers.append({
                "dataset_id": key[0], "version": version,
                "code": "personal_or_sensitive_data_lacks_recorded_basis",
            })
        if privacy in {"personal_data", "sensitive_data"} and consent in {"documented", "not_required"}:
            basis_reference = str(metadata.get("consent_basis_reference", "")).strip()
            if not basis_reference or len(basis_reference) > 1000:
                blockers.append({
                    "dataset_id": key[0], "version": version,
                    "code": "consent_basis_reference_missing",
                })
        if publication_scope == "public" and privacy != "public":
            blockers.append({
                "dataset_id": key[0], "version": version,
                "code": "public_scope_requires_explicit_public_privacy_classification",
            })
        if publication_scope == "public" and consent not in {"documented", "not_required"}:
            blockers.append({
                "dataset_id": key[0], "version": version,
                "code": "public_scope_requires_recorded_consent_basis",
            })
        if publication_scope == "public" and access != "public":
            blockers.append({
                "dataset_id": key[0], "version": version,
                "code": "dataset_access_scope_not_public",
            })
        if publication_scope == "project" and access == "restricted":
            blockers.append({
                "dataset_id": key[0], "version": version,
                "code": "dataset_access_scope_restricted",
            })
        if license_value in {"", "unknown", "unspecified", "not known"}:
            target = blockers if publication_scope == "public" else warnings
            target.append({
                "dataset_id": key[0], "version": version,
                "code": "license_terms_not_recorded",
            })
        if not str(record.get("content_sha256", "")).strip():
            blockers.append({
                "dataset_id": key[0], "version": version,
                "code": "content_digest_not_recorded",
            })
        for issue in governance_issues(record):
            if issue not in {"consent_withdrawn", "consent_review_pending",
                             "consent_or_other_lawful_basis_review_required",
                             "public_access_for_personal_data", "license_terms_not_recorded",
                             "retention_policy_not_recorded"}:
                warnings.append({
                    "dataset_id": key[0], "version": version,
                    "code": issue,
                })
        if "retention_policy_not_recorded" in governance_issues(record):
            warnings.append({
                "dataset_id": key[0], "version": version,
                "code": "retention_policy_not_recorded",
            })

        normalized_refs.append({
            "dataset_id": key[0],
            "version": version,
            "title": str(record.get("title", ""))[:300],
            "content_sha256": record.get("content_sha256", ""),
            "license": record.get("license", ""),
            "privacy_classification": privacy,
            "consent_status": consent,
            "access_scope": access,
        })

    report = {
        "eligible_for_manifest": not blockers,
        "publication_scope": publication_scope,
        "blocking_issues": blockers,
        "review_warnings": warnings,
        "dataset_versions_checked": len(seen),
        "legal_compliance_established": False,
        "ethics_or_consent_approval_established": False,
        "raw_dataset_files_included": False,
        "scientific_validity_established": False,
    }
    if blockers:
        return {**report, "manifest": None, "manifest_created": False}

    environment_payload = dict(environment or {})
    if "ssswet_dataset_governance_gate" in environment_payload:
        raise ValueError("environment reserves ssswet_dataset_governance_gate")
    environment_payload["ssswet_dataset_governance_gate"] = {
        "publication_scope": publication_scope,
        "gate_version": 1,
    }
    manifest = build_manifest(
        protocol_id=protocol_id,
        protocol_version=protocol_version,
        dataset_refs=normalized_refs,
        software_version=software_version,
        parameters=parameters,
        source_ids=source_ids,
        environment=environment_payload,
        random_seed=random_seed,
        input_checksums=input_checksums,
    )
    return {
        **report,
        "manifest": manifest,
        "manifest_created": True,
        "legal_compliance_established": False,
        "scientific_validity_established": False,
    }

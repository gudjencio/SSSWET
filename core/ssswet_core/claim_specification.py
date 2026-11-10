"""Versioned, context-explicit claim contracts for reproducible comparison.

This module validates researcher-supplied structure. It never extracts facts
from prose or decides whether a claim is true.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import re
from typing import Iterable


MAX_EVIDENCE_REFS = 100
MAX_CLAIM_TEXT = 4000


def _clean(value: str, field: str, *, required: bool = False) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be text")
    result = " ".join(value.strip().split())
    if required and not result:
        raise ValueError(f"{field} is required")
    if len(result) > MAX_CLAIM_TEXT:
        raise ValueError(f"{field} is too long")
    return result


def _key(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().casefold())


@dataclass(frozen=True)
class ClaimSpecification:
    claim_id: str
    version: int
    statement: str
    subject: str
    predicate: str
    value: str
    scope: str = ""
    conditions: str = ""
    population: str = ""
    comparator: str = ""
    unit: str = ""
    timeframe: str = ""
    outcome: str = ""
    method: str = ""
    uncertainty_note: str = ""
    evidence_refs: tuple[str, ...] = ()
    supersedes_version: str = ""

    def __post_init__(self) -> None:
        for field in ("claim_id", "statement", "subject", "predicate", "value"):
            _clean(getattr(self, field), field, required=True)
        for field in (
            "scope", "conditions", "population", "comparator", "unit",
            "timeframe", "outcome", "method", "uncertainty_note",
            "supersedes_version",
        ):
            _clean(getattr(self, field), field)
        if isinstance(self.version, bool) or not isinstance(self.version, int) or self.version < 1:
            raise ValueError("version must be a positive integer")
        if self.version == 1 and self.supersedes_version:
            raise ValueError("version 1 cannot supersede another version")
        if self.version > 1 and not self.supersedes_version.strip():
            raise ValueError("later versions must identify the version they supersede")
        if not isinstance(self.evidence_refs, tuple) or len(self.evidence_refs) > MAX_EVIDENCE_REFS:
            raise ValueError(f"evidence_refs must be a tuple of at most {MAX_EVIDENCE_REFS} IDs")
        cleaned = [_clean(item, "evidence reference", required=True) for item in self.evidence_refs]
        if len(set(cleaned)) != len(cleaned):
            raise ValueError("evidence references must be unique")

    @property
    def version_ref(self) -> str:
        return f"{self.claim_id}@{self.version}"

    @property
    def comparability_key(self) -> tuple[str, ...]:
        """Context key; the asserted value is deliberately excluded."""
        return tuple(_key(getattr(self, name)) for name in (
            "subject", "predicate", "scope", "conditions", "population",
            "comparator", "unit", "timeframe", "outcome", "method",
        ))

    @property
    def fingerprint(self) -> str:
        payload = asdict(self)
        payload["evidence_refs"] = list(self.evidence_refs)
        canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        return sha256(canonical.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["evidence_refs"] = list(self.evidence_refs)
        payload["version_ref"] = self.version_ref
        payload["comparability_key"] = list(self.comparability_key)
        payload["fingerprint"] = self.fingerprint
        return payload


def validate_claim_history(claims: Iterable[ClaimSpecification]) -> dict:
    """Validate complete, gap-free version chains without mutating any claim."""
    items = list(claims)
    if len(items) > 2000:
        raise ValueError("claim history is limited to 2,000 versions")
    if any(not isinstance(item, ClaimSpecification) for item in items):
        raise ValueError("every history item must be a ClaimSpecification")
    grouped: dict[str, dict[int, ClaimSpecification]] = {}
    for item in items:
        versions = grouped.setdefault(item.claim_id, {})
        if item.version in versions:
            raise ValueError(f"duplicate claim version: {item.version_ref}")
        versions[item.version] = item
    errors = []
    for claim_id, versions in sorted(grouped.items()):
        numbers = sorted(versions)
        expected = list(range(1, numbers[-1] + 1))
        if numbers != expected:
            errors.append({"claim_id": claim_id, "issue": "version_gap", "versions": numbers})
            continue
        for number in numbers[1:]:
            expected_parent = f"{claim_id}@{number - 1}"
            if versions[number].supersedes_version != expected_parent:
                errors.append({
                    "claim_id": claim_id, "version": number,
                    "issue": "incorrect_supersedes_reference",
                    "expected": expected_parent,
                    "actual": versions[number].supersedes_version,
                })
    return {
        "valid": not errors,
        "claim_count": len(grouped),
        "version_count": len(items),
        "errors": errors,
        "history_mutated": False,
        "scientific_validity_established": False,
    }


def comparable(left: ClaimSpecification, right: ClaimSpecification) -> bool:
    if not isinstance(left, ClaimSpecification) or not isinstance(right, ClaimSpecification):
        raise ValueError("both values must be ClaimSpecification instances")
    return left.comparability_key == right.comparability_key

"""Agent-to-pricing evidence adapter with independent review separation.

Agent submissions are treated as claims until source verification and a
separate verifier approval are recorded. This adapter does not call AI agents,
fetch sources, or infer costs; it validates structured records supplied by
those workflows.
"""
from __future__ import annotations

from collections import defaultdict
from decimal import Decimal, InvalidOperation
from typing import Any

from .provisional_pricing import (
    REQUIRED_COST_CATEGORIES,
    estimate_provisional_technology_price,
)

ALLOWED_AGENT_ROLES = {
    "general_researcher",
    "independent_verifier",
    "medical_researcher",
    "materials_scientist",
    "data_analyst",
    "systems_engineer",
    "ethics_reviewer",
    "futures_analyst",
}


def _amount(value: Any, field: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f"{field} must be a valid decimal") from exc
    if not result.is_finite() or result < 0:
        raise ValueError(f"{field} must be a finite non-negative amount")
    return result


def build_agent_pricing_estimate(
    *,
    estimate_id: str,
    submissions: list[dict[str, Any]],
    independent_review: dict[str, Any] | None,
    currency: str,
    uncertainty_rate: Decimal | str | int | float,
    tax_rate: Decimal | str | int | float | None,
    confidence: Decimal | str | int | float,
) -> dict[str, Any]:
    """Aggregate agent-submitted cost evidence and enforce a separate review.

    Each submission requires a known agent role, unique submission ID,
    category, source reference, low/base/high values, and source verification.
    The independent reviewer must be a different agent and must approve the
    exact estimate ID. Missing or unverified evidence remains non-publishable.
    """
    estimate_id = str(estimate_id).strip()
    if not estimate_id or len(estimate_id) > 120:
        raise ValueError("estimate_id must contain 1 to 120 characters")
    if not isinstance(submissions, list):
        raise ValueError("submissions must be a list")

    seen_ids: set[str] = set()
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    evidence_complete = True
    source_refs: list[str] = []

    for record in submissions:
        if not isinstance(record, dict):
            raise ValueError("each submission must be an object")
        submission_id = str(record.get("submission_id", "")).strip()
        agent_id = str(record.get("agent_id", "")).strip()
        role = str(record.get("agent_role", "")).strip()
        category = record.get("category")
        if not submission_id or submission_id in seen_ids:
            raise ValueError("submission IDs must be present and unique")
        seen_ids.add(submission_id)
        if not agent_id or len(agent_id) > 100 or role not in ALLOWED_AGENT_ROLES:
            raise ValueError("submission must identify a known agent role and ID")
        if role == "independent_verifier":
            raise ValueError("independent verifier cannot submit the costs it reviews")
        if category not in REQUIRED_COST_CATEGORIES:
            raise ValueError(f"unsupported cost category: {category}")

        source_ref = str(record.get("source_ref", "")).strip()
        verified = record.get("source_verified") is True
        if not source_ref or len(source_ref) > 500 or not verified:
            evidence_complete = False
        elif source_ref not in source_refs:
            source_refs.append(source_ref)

        values = {
            key: _amount(record.get(key), f"{submission_id}.{key}")
            for key in ("low", "base", "high")
        }
        if not values["low"] <= values["base"] <= values["high"]:
            raise ValueError(f"{submission_id} must satisfy low <= base <= high")
        grouped[category].append({
            **values,
            "source_ref": source_ref,
            "verified": verified and bool(source_ref),
            "agent_id": agent_id,
            "agent_role": role,
        })

    aggregated = []
    for category in REQUIRED_COST_CATEGORIES:
        items = grouped.get(category, [])
        if not items:
            continue
        aggregated.append({
            "category": category,
            "low": str(sum((item["low"] for item in items), Decimal("0"))),
            "base": str(sum((item["base"] for item in items), Decimal("0"))),
            "high": str(sum((item["high"] for item in items), Decimal("0"))),
            "source_ref": " | ".join(dict.fromkeys(item["source_ref"] for item in items if item["source_ref"])),
            "verified": all(item["verified"] for item in items),
        })

    review_ok = False
    reviewer_id = ""
    review_reason = "independent_review_missing"
    if isinstance(independent_review, dict):
        reviewer_id = str(independent_review.get("reviewer_agent_id", "")).strip()
        reviewer_role = str(independent_review.get("reviewer_role", "")).strip()
        reviewed_id = str(independent_review.get("estimate_id", "")).strip()
        approved = independent_review.get("approved") is True
        author_ids = {str(record.get("agent_id", "")).strip() for record in submissions}
        review_ok = (
            bool(reviewer_id)
            and reviewer_role == "independent_verifier"
            and reviewer_id not in author_ids
            and reviewed_id == estimate_id
            and approved
            and bool(str(independent_review.get("review_reference", "")).strip())
        )
        if review_ok:
            review_reason = "independent_review_approved"
        elif reviewer_id in author_ids and reviewer_id:
            review_reason = "reviewer_also_authored_cost_submission"
        elif reviewed_id != estimate_id:
            review_reason = "review_targets_different_estimate"
        elif not approved:
            review_reason = "independent_review_not_approved"
        else:
            review_reason = "independent_review_record_incomplete"

    # An incomplete source set is still sent to the core calculator, which
    # reports missing categories and blocks publication without inventing data.
    result = estimate_provisional_technology_price(
        cost_items=aggregated,
        currency=currency,
        uncertainty_rate=uncertainty_rate,
        tax_rate=tax_rate,
        confidence=confidence,
        independent_verifier_approved=review_ok,
    )
    result["estimate_id"] = estimate_id
    result["source_evidence_complete"] = evidence_complete
    result["independent_review_status"] = review_reason
    result["independent_reviewer_agent_id"] = reviewer_id or None
    result["agent_submission_count"] = len(submissions)
    result["agent_submitted_source_refs"] = source_refs
    if not evidence_complete:
        result["publishable"] = False
        result["status"] = "withheld_pending_evidence_or_review"
        result["evidence_complete"] = False
    return result

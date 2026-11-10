"""Dissent-preserving synthesis for structured research deliberations.

This is a transparent record assembler, not a voting system, scientific
adjudicator, autonomous agent, or safety approval mechanism.
"""
from __future__ import annotations

from hashlib import sha256
import json


MAX_REVIEWS = 100
MAX_TEXT = 4000
MAX_CONTEXT_BYTES = 250_000
MAX_REVIEW_BYTES = 20_000


def build_deliberation_synthesis(
    case_id: str, claim_id: str, reviews: list[dict], *,
    evidence_coverage: dict | None = None,
    disagreement: dict | None = None,
    reassessment: dict | None = None,
) -> dict:
    for value, field in ((case_id, "case_id"), (claim_id, "claim_id")):
        if not isinstance(value, str) or not value.strip() or len(value) > 200:
            raise ValueError(f"{field} is required and limited to 200 characters")
    if not isinstance(reviews, list) or len(reviews) > MAX_REVIEWS:
        raise ValueError(f"reviews must be a list of at most {MAX_REVIEWS}")
    normalized = []
    seen = set()
    seen_reviewers = set()
    for review in reviews:
        if not isinstance(review, dict):
            raise ValueError("every review must be a dictionary")
        reviewer = review.get("reviewer_id")
        review_id = review.get("review_id", reviewer)
        position = review.get("position")
        if not isinstance(reviewer, str) or not reviewer.strip():
            raise ValueError("every review requires reviewer_id")
        if not isinstance(review_id, str) or not review_id.strip() or review_id in seen:
            raise ValueError("review IDs must be unique and non-empty")
        if not isinstance(position, str) or not position.strip() or len(position) > 100:
            raise ValueError("every review requires a bounded explicit position")
        if reviewer in seen_reviewers:
            raise ValueError("reviewer IDs must be unique within one synthesis")
        seen.add(review_id)
        seen_reviewers.add(reviewer)
        item = dict(review)
        encoded_review = json.dumps(item, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
        if len(encoded_review) > MAX_REVIEW_BYTES:
            raise ValueError("a review record exceeds the 20 KB limit")
        for field in ("rationale", "limitations", "uncertainty_note"):
            value = item.get(field, "")
            if not isinstance(value, str) or len(value) > MAX_TEXT:
                raise ValueError(f"{field} must be text of at most {MAX_TEXT} characters")
        normalized.append(item)
    normalized.sort(key=lambda item: (
        item["reviewer_id"], str(item.get("submitted_at", "")),
        str(item.get("review_id", item["reviewer_id"])),
    ))
    coverage = evidence_coverage or {}
    disagreement = disagreement or {}
    reassessment = reassessment or {}
    if not all(isinstance(item, dict) for item in (coverage, disagreement, reassessment)):
        raise ValueError("coverage, disagreement and reassessment summaries must be dictionaries")
    context_bytes = json.dumps(
        [coverage, disagreement, reassessment], ensure_ascii=False, sort_keys=True, default=str,
    ).encode("utf-8")
    if len(context_bytes) > MAX_CONTEXT_BYTES:
        raise ValueError("combined evidence and review summaries exceed the 250 KB limit")
    counts = {}
    for item in normalized:
        key = item["position"].strip().casefold()
        counts[key] = counts.get(key, 0) + 1
    if not normalized:
        pattern = "no_submissions"
    elif len(counts) == 1:
        pattern = "unanimous_recorded_positions"
    else:
        pattern = "mixed_recorded_positions"

    gaps = []
    for claim in coverage.get("claims", []) if isinstance(coverage, dict) else []:
        gaps.extend(
            {"claim_id": claim.get("claim_id", ""), "gap": gap}
            for gap in claim.get("coverage_gaps", [])
        )
    unresolved = []
    if pattern == "mixed_recorded_positions":
        unresolved.append("Reviewers recorded different positions; preserve and examine each rationale.")
    if any(item["position"].casefold() in {"abstains", "inconclusive", "unable_to_assess"} for item in normalized):
        unresolved.append("At least one reviewer abstained or could not reach an assessment.")
    if gaps:
        unresolved.append("Evidence coverage gaps remain for one or more claims.")
    if reassessment.get("reassessment_recommended"):
        unresolved.append("One or more review dependencies changed or are missing.")
    if disagreement.get("case_count", 0):
        unresolved.append("Declared methodological or contextual differences require human interpretation.")

    payload = {
        "format": "ssswet-deliberation-synthesis-v1",
        "case_id": case_id.strip(), "claim_id": claim_id.strip(),
        "review_count": len(normalized), "position_pattern": pattern,
        "position_counts": dict(sorted(counts.items())),
        "reviewer_positions": normalized,
        "evidence_coverage_gaps": gaps,
        "disagreement_summary": disagreement,
        "reassessment_summary": reassessment,
        "unresolved_questions": unresolved,
        "human_review_required": bool(unresolved),
        "majority_vote_used": False,
        "minority_positions_preserved": True,
        "scientific_validity_established": False,
        "operational_authorization": False,
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return {**payload, "synthesis_sha256": sha256(canonical.encode("utf-8")).hexdigest()}

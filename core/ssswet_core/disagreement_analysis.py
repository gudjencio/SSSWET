"""Decompose declared reviewer disagreements into inspectable dimensions."""
from __future__ import annotations

from collections import defaultdict


MAX_REVIEWS = 2000
DIMENSIONS = ("scope", "method", "measurement", "population", "timeframe", "assumptions", "analysis_plan")


def analyze_disagreements(reviews: list[dict]) -> dict:
    if not isinstance(reviews, list) or len(reviews) > MAX_REVIEWS:
        raise ValueError(f"reviews must be a list of at most {MAX_REVIEWS} records")
    grouped = defaultdict(list)
    seen = set()
    for review in reviews:
        if not isinstance(review, dict):
            raise ValueError("each review must be a dictionary")
        case_id, reviewer_id, position = (
            review.get("case_id"), review.get("reviewer_id"), review.get("position")
        )
        if not all(isinstance(value, str) and value.strip() for value in (case_id, reviewer_id, position)):
            raise ValueError("case_id, reviewer_id and position are required")
        key = (case_id, reviewer_id)
        if key in seen:
            raise ValueError("reviewer IDs must be unique within a case")
        seen.add(key)
        grouped[case_id].append(review)

    reports = []
    for case_id, items in sorted(grouped.items()):
        positions = defaultdict(list)
        for item in items:
            positions[item["position"].strip().casefold()].append(item["reviewer_id"])
        dimensions = {}
        for field in DIMENSIONS:
            values = sorted({
                " ".join(str(item.get(field, "")).casefold().split())
                for item in items if str(item.get(field, "")).strip()
            })
            if len(values) > 1:
                dimensions[field] = values
        source_usage = defaultdict(list)
        for item in items:
            for source_id in item.get("source_ids", []):
                if isinstance(source_id, str) and source_id.strip():
                    source_usage[source_id.strip()].append(item["reviewer_id"])
        shared_sources = {
            source: sorted(reviewers)
            for source, reviewers in sorted(source_usage.items()) if len(reviewers) > 1
        }
        reports.append({
            "case_id": case_id, "review_count": len(items),
            "position_counts": {key: len(value) for key, value in sorted(positions.items())},
            "reviewers_by_position": {key: sorted(value) for key, value in sorted(positions.items())},
            "position_disagreement": len(positions) > 1,
            "declared_methodological_differences": dimensions,
            "shared_source_ids": shared_sources,
            "shared_source_overlap_requires_independence_review": bool(shared_sources),
            "resolution": "unresolved_until_human_review",
            "automatic_resolution": False,
        })
    return {
        "cases": reports, "case_count": len(reports),
        "review_count": len(reviews),
        "declared_dimensions_only": True,
        "majority_vote_used": False,
    }

"""Inter-reviewer concordance statistics; agreement is not correctness."""
from __future__ import annotations
from itertools import combinations
from .assurance_common import identifier

MAX_RATINGS = 2000
SCHEMA_VERSION = 1
MIN_MATCHED_ITEMS = 5
LABELS = {"accept", "needs_revision", "reject", "uncertain"}


def measure_reviewer_concordance(ratings: list[dict], *, minimum_items: int = MIN_MATCHED_ITEMS) -> dict:
    if not isinstance(ratings, list) or len(ratings) > MAX_RATINGS:
        raise ValueError(f"ratings must contain at most {MAX_RATINGS} items")
    if isinstance(minimum_items, bool) or not isinstance(minimum_items, int) or not 2 <= minimum_items <= 1000:
        raise ValueError("minimum_items must be between 2 and 1000")
    by_pair, seen, reviewers = {}, set(), set()
    for item in ratings:
        if not isinstance(item, dict):
            raise ValueError("each rating must be an object")
        item_id = identifier(item.get("item_id"), "item_id")
        reviewer = identifier(item.get("reviewer_id"), "reviewer_id")
        decision = item.get("decision")
        if decision not in LABELS:
            raise ValueError("unsupported reviewer decision")
        key = (item_id, reviewer)
        if key in seen:
            raise ValueError("a reviewer may rate an item only once per batch")
        seen.add(key)
        by_pair.setdefault(reviewer, {})[item_id] = decision
        reviewers.add(reviewer)
    pairs = []
    for left, right in combinations(sorted(reviewers), 2):
        common = sorted(set(by_pair[left]) & set(by_pair[right]))
        n = len(common)
        observed = sum(by_pair[left][item] == by_pair[right][item] for item in common) / n if n else None
        kappa = None
        expected = None
        if n >= minimum_items:
            left_counts = {label: sum(by_pair[left][item] == label for item in common) for label in LABELS}
            right_counts = {label: sum(by_pair[right][item] == label for item in common) for label in LABELS}
            expected = sum(left_counts[label] * right_counts[label] for label in LABELS) / (n * n)
            if expected < 1:
                kappa = (observed - expected) / (1 - expected)
        pairs.append({"reviewer_pair": [left, right], "matched_item_count": n, "raw_agreement": round(observed, 6) if observed is not None else None, "chance_expected_agreement": round(expected, 6) if expected is not None else None, "cohen_kappa": round(kappa, 6) if kappa is not None else None, "minimum_sample_met": n >= minimum_items, "prevalence_caveat": "Kappa can be unstable under prevalence imbalance; inspect raw counts and context."})
    return {"schema_version": SCHEMA_VERSION, "reviewer_count": len(reviewers), "rating_count": len(ratings), "pairwise_results": pairs, "reviewer_rankings_created": False, "agreement_is_correctness": False, "unmatched_ratings_retained": True}

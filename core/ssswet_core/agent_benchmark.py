"""Versioned, reviewer-scored evaluation of declared agent capabilities.

Scores describe a fixed benchmark run, not general intelligence or competence.
"""
from __future__ import annotations
from hashlib import sha256
import json
from math import isfinite

MAX_CASES = 200
_OUTCOMES = {"correct": 1.0, "partial": 0.5, "incorrect": 0.0, "abstained": 0.0}

def _canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)

def evaluate_agent_benchmark(*, benchmark_id: str, version: str, cases: list[dict], reviews: list[dict]) -> dict:
    if not isinstance(benchmark_id, str) or not benchmark_id.strip() or len(benchmark_id) > 120:
        raise ValueError("benchmark_id must contain 1 to 120 characters")
    if not isinstance(version, str) or not version.strip() or len(version) > 80:
        raise ValueError("version must contain 1 to 80 characters")
    if not isinstance(cases, list) or not 1 <= len(cases) <= MAX_CASES:
        raise ValueError(f"cases must contain 1 to {MAX_CASES} items")
    if not isinstance(reviews, list) or len(reviews) > MAX_CASES:
        raise ValueError("reviews must be a list no larger than the case set")
    normalized_cases = {}
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("each case must be an object")
        case_id, capability, weight = case.get("case_id"), case.get("capability"), case.get("weight", 1)
        if not isinstance(case_id, str) or not case_id.strip() or len(case_id) > 120 or case_id in normalized_cases:
            raise ValueError("case IDs must be unique non-empty strings of at most 120 characters")
        if not isinstance(capability, str) or not capability.strip() or len(capability) > 120:
            raise ValueError("each case must name a capability of at most 120 characters")
        if isinstance(weight, bool) or not isinstance(weight, (int, float)) or not isfinite(weight) or not 0 < weight <= 100:
            raise ValueError("case weight must be finite and between 0 and 100")
        try:
            canonical_case = _canonical(case)
        except (TypeError, ValueError) as exc:
            raise ValueError("benchmark cases must contain finite JSON-compatible values") from exc
        if len(canonical_case) > 10_000:
            raise ValueError("each benchmark case must be at most 10000 characters")
        case_fingerprint = sha256(canonical_case.encode("utf-8")).hexdigest()
        normalized_cases[case_id] = {
            "case_id": case_id, "capability": capability.strip(),
            "weight": float(weight), "case_fingerprint": case_fingerprint,
        }
    normalized_reviews = {}
    for review in reviews:
        if not isinstance(review, dict):
            raise ValueError("each review must be an object")
        case_id = review.get("case_id")
        if case_id not in normalized_cases or case_id in normalized_reviews:
            raise ValueError("reviews must reference each case at most once")
        outcome, reviewer, confidence = review.get("outcome"), review.get("reviewer_id"), review.get("confidence")
        if outcome not in _OUTCOMES:
            raise ValueError("outcome must be correct, partial, incorrect or abstained")
        if not isinstance(reviewer, str) or not reviewer.strip() or len(reviewer) > 120:
            raise ValueError("reviewer_id is required for an auditable result")
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not isfinite(confidence) or not 0 <= confidence <= 1:
            raise ValueError("confidence must be finite and between 0 and 1")
        normalized_reviews[case_id] = {"outcome": outcome, "reviewer_id": reviewer.strip(), "confidence": float(confidence)}
    case_results, capability_totals = [], {}
    weighted_total = reviewed_weight_total = brier_total = 0.0
    reviewed = abstained = 0
    for case_id, case in sorted(normalized_cases.items()):
        review = normalized_reviews.get(case_id)
        outcome = review["outcome"] if review else "unreviewed"
        score = _OUTCOMES[outcome] if review else 0.0
        if review:
            reviewed_weight_total += case["weight"]
            weighted_total += case["weight"] * score
            reviewed += 1
            if outcome == "abstained":
                abstained += 1
            else:
                brier_total += (review["confidence"] - score) ** 2
        bucket = capability_totals.setdefault(case["capability"], {
            "case_count": 0, "reviewed_count": 0, "weighted_score": 0.0, "weight": 0.0,
        })
        bucket["case_count"] += 1
        if review:
            bucket["reviewed_count"] += 1
            bucket["weighted_score"] += case["weight"] * score
            bucket["weight"] += case["weight"]
        case_results.append({
            "case_id": case_id, "capability": case["capability"], "outcome": outcome,
            "score": score, "weight": case["weight"],
            "case_fingerprint": case["case_fingerprint"],
            "reviewer_id": review["reviewer_id"] if review else None,
        })
    capability_scores = {
        name: {
            "case_count": item["case_count"],
            "reviewed_count": item["reviewed_count"],
            "coverage": round(item["reviewed_count"] / item["case_count"], 6),
            "weighted_score": round(item["weighted_score"] / item["weight"], 6) if item["weight"] else None,
        }
        for name, item in sorted(capability_totals.items())
    }
    canonical_cases = [normalized_cases[key] for key in sorted(normalized_cases)]
    return {
        "benchmark_id": benchmark_id.strip(), "version": version.strip(),
        "case_set_sha256": sha256(_canonical(canonical_cases).encode("utf-8")).hexdigest(),
        "case_count": len(cases), "reviewed_count": reviewed,
        "coverage": round(reviewed / len(cases), 6),
        "abstention_rate_of_reviewed": round(abstained / reviewed, 6) if reviewed else None,
        "weighted_score": round(weighted_total / reviewed_weight_total, 6) if reviewed_weight_total else None,
        "reviewed_weight_total": round(reviewed_weight_total, 6),
        "brier_score_non_abstained": round(brier_total / max(1, reviewed - abstained), 6) if reviewed > abstained else None,
        "capability_scores": capability_scores, "case_results": case_results,
        "unreviewed_case_ids": sorted(set(normalized_cases) - set(normalized_reviews)),
        "reviewed_outcomes_are_human_annotations": True,
        "general_intelligence_or_real_world_competence_claim": False,
    }

def compare_benchmark_reports(previous: dict, current: dict) -> dict:
    if not isinstance(previous, dict) or not isinstance(current, dict) or previous.get("benchmark_id") != current.get("benchmark_id"):
        raise ValueError("reports must belong to the same benchmark")
    before_items, after_items = previous.get("case_results"), current.get("case_results")
    if not isinstance(before_items, list) or not isinstance(after_items, list):
        raise ValueError("reports must contain case_results lists")
    before, after = {}, {}
    for target, items in ((before, before_items), (after, after_items)):
        for item in items:
            if not isinstance(item, dict) or not isinstance(item.get("case_id"), str) or not item["case_id"]:
                raise ValueError("case_results must contain unique case IDs")
            if item["case_id"] in target:
                raise ValueError("case_results must not contain duplicate case IDs")
            target[item["case_id"]] = item
    shared = sorted(set(before) & set(after))
    changes = [
        {"case_id": key, "previous": before[key].get("outcome"), "current": after[key].get("outcome"),
         "score_delta": round(after[key].get("score", 0) - before[key].get("score", 0), 6)}
        for key in shared if before[key].get("outcome") != after[key].get("outcome")
    ]
    changed_definitions = [
        key for key in shared
        if before[key].get("case_fingerprint") != after[key].get("case_fingerprint")
    ]
    same_case_set = (
        isinstance(previous.get("case_set_sha256"), str)
        and previous.get("case_set_sha256") == current.get("case_set_sha256")
        and not (set(after) ^ set(before))
    )
    before_score, after_score = previous.get("weighted_score"), current.get("weighted_score")
    score_delta = None
    if same_case_set and isinstance(before_score, (int, float)) and isinstance(after_score, (int, float)):
        if isfinite(before_score) and isfinite(after_score):
            score_delta = round(after_score - before_score, 6)
    return {
        "benchmark_id": previous["benchmark_id"],
        "shared_case_count": len(shared),
        "added_case_ids": sorted(set(after) - set(before)),
        "removed_case_ids": sorted(set(before) - set(after)),
        "changed_cases": changes,
        "changed_case_definition_ids": changed_definitions,
        "case_set_sha256_matches": same_case_set,
        "weighted_score_delta": score_delta,
        "comparison_is_like_for_like": same_case_set,
        "does_not_establish_general_intelligence": True,
    }

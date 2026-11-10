"""Reviewer agreement against explicitly adjudicated reference cases.

Metrics describe agreement with a supplied reference set, not truth or
reviewer competence. Abstentions are reported separately and never scored as
incorrect or silently discarded.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from math import sqrt


LABELS = ("supports", "challenges", "mixed")
MAX_CASES = 2000


def _wilson(successes: int, total: int) -> tuple[float, float] | None:
    if total == 0:
        return None
    z = 1.959963984540054
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    margin = z * sqrt((p * (1 - p) / total) + (z * z / (4 * total * total))) / denominator
    return round(max(0.0, center - margin), 4), round(min(1.0, center + margin), 4)


def evaluate_reviewer_agreement(cases: list[dict]) -> dict:
    if not isinstance(cases, list) or len(cases) > MAX_CASES:
        raise ValueError(f"cases must be a list of at most {MAX_CASES}")
    grouped = defaultdict(list)
    seen_cases = set()
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("each case must be a dictionary")
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not case_id.strip() or case_id in seen_cases:
            raise ValueError("case IDs must be unique and non-empty")
        seen_cases.add(case_id)
        if case.get("reference_status") != "human_adjudicated":
            raise ValueError("reference cases must be explicitly human_adjudicated")
        reference = case.get("reference")
        if reference not in LABELS:
            raise ValueError("unsupported reference label")
        assessments = case.get("assessments", [])
        if not isinstance(assessments, list) or len(assessments) > 100:
            raise ValueError("assessments must be a list of at most 100 entries")
        reviewer_ids = set()
        for assessment in assessments:
            if not isinstance(assessment, dict):
                raise ValueError("assessment must be a dictionary")
            reviewer = assessment.get("reviewer_id")
            outcome = assessment.get("outcome")
            if not isinstance(reviewer, str) or not reviewer.strip():
                raise ValueError("reviewer_id is required")
            if outcome not in (*LABELS, "abstains"):
                raise ValueError("unsupported reviewer outcome")
            if reviewer in reviewer_ids:
                raise ValueError("a reviewer may submit only once per case")
            reviewer_ids.add(reviewer)
            grouped[reviewer].append((reference, outcome, case_id))

    reports = []
    for reviewer, rows in sorted(grouped.items()):
        scored = [(reference, outcome) for reference, outcome, _ in rows if outcome != "abstains"]
        abstentions = sum(outcome == "abstains" for _, outcome, _ in rows)
        matrix = {actual: {predicted: 0 for predicted in LABELS} for actual in LABELS}
        for actual, predicted in scored:
            matrix[actual][predicted] += 1
        total = len(scored)
        correct = sum(matrix[label][label] for label in LABELS)
        per_label = {}
        f1_values = []
        for label in LABELS:
            tp = matrix[label][label]
            fp = sum(matrix[actual][label] for actual in LABELS if actual != label)
            fn = sum(matrix[label][predicted] for predicted in LABELS if predicted != label)
            precision = tp / (tp + fp) if tp + fp else None
            recall = tp / (tp + fn) if tp + fn else None
            f1 = (
                2 * precision * recall / (precision + recall)
                if precision is not None and recall is not None and precision + recall else
                0.0 if precision is not None or recall is not None else None
            )
            if f1 is not None:
                f1_values.append(f1)
            per_label[label] = {
                "precision": None if precision is None else round(precision, 4),
                "recall": None if recall is None else round(recall, 4),
                "f1": None if f1 is None else round(f1, 4),
            }
        reference_counts = Counter(actual for actual, _ in scored)
        predicted_counts = Counter(predicted for _, predicted in scored)
        expected = sum(reference_counts[label] * predicted_counts[label] for label in LABELS) / (total * total) if total else 0.0
        observed = correct / total if total else None
        kappa = None if total == 0 or expected == 1 else (observed - expected) / (1 - expected)
        reports.append({
            "reviewer_id": reviewer, "case_count": len(rows),
            "scored_case_count": total, "abstention_count": abstentions,
            "abstention_rate": round(abstentions / len(rows), 4) if rows else 0.0,
            "agreement_with_reference": None if observed is None else round(observed, 4),
            "agreement_wilson_95": _wilson(correct, total),
            "cohen_kappa": None if kappa is None else round(kappa, 4),
            "macro_f1": round(sum(f1_values) / len(f1_values), 4) if f1_values else None,
            "per_label": per_label, "confusion_matrix": matrix,
            "small_sample_warning": total < 10,
            "case_ids": sorted(case_id for _, _, case_id in rows),
            "reference_is_ground_truth": False,
        })
    return {
        "reviewers": reports, "reviewer_count": len(reports),
        "case_count": len(cases),
        "interpretation": "Agreement with a supplied human-adjudicated reference set only; this does not establish scientific truth, reviewer competence, or independence.",
        "reviewer_ranking_produced": False,
        "abstentions_scored_as_incorrect": False,
    }

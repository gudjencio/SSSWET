"""Transparent, human-entered research programme prioritisation rubric.

Scores are decision-support inputs, not measurements of scientific truth.
Only fully assessed programmes receive a comparable overall score.
"""
from __future__ import annotations

from typing import Any, Mapping

CRITERIA = (
    {"key": "societal_benefit", "weight": 20, "label": "Potential societal benefit",
     "description": "Potential to improve human wellbeing, safety or essential services."},
    {"key": "ecological_benefit", "weight": 20, "label": "Ecological and animal benefit",
     "description": "Potential benefits for ecosystems, biodiversity and animal welfare."},
    {"key": "evidence_maturity", "weight": 15, "label": "Evidence maturity",
     "description": "Quality, relevance, independence and reproducibility of available evidence."},
    {"key": "technical_feasibility", "weight": 15, "label": "Technical feasibility",
     "description": "Plausibility of a defined development path using known methods."},
    {"key": "resource_accessibility", "weight": 10, "label": "Resource accessibility",
     "description": "Availability of skills, infrastructure, materials and responsible partners."},
    {"key": "safety_legal_readiness", "weight": 20, "label": "Safety and legal readiness",
     "description": "Strength of safeguards, oversight, regulatory pathway and risk controls."},
)
CRITERION_KEYS = tuple(item["key"] for item in CRITERIA)
MAX_SCORE = 5
WEIGHT_TOTAL = sum(item["weight"] for item in CRITERIA)


def framework_definition() -> dict[str, Any]:
    """Return the public rubric and its interpretation rules."""
    return {
        "criteria": [dict(item) for item in CRITERIA],
        "scale": {"minimum": 0, "maximum": MAX_SCORE,
                  "meaning": "0 = very low / absent; 5 = very strong / well established"},
        "weight_total": WEIGHT_TOTAL,
        "scoring_method": "weighted arithmetic mean, normalized to 0–100",
        "comparison_rule": "Only assessments with all six criteria scored are ranked.",
        "human_review_required": True,
        "automatic_funding_decisions": False,
        "scientific_validity_established": False,
        "limitations": [
            "Scores are human-entered judgements and may reflect uncertainty or bias.",
            "A high score does not prove that a technology works or is safe.",
            "Missing criteria remain unassessed and are never silently treated as zero.",
            "Assessments should cite current primary evidence and be reviewed periodically.",
            "Legal, ethical and safety requirements can block work regardless of score.",
        ],
    }


def score_assessment(programme_id: str, scores: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and score one programme; incomplete assessments are not ranked."""
    identifier = str(programme_id).strip()
    if not identifier or len(identifier) > 160:
        raise ValueError("programme_id must contain between 1 and 160 characters")
    if not isinstance(scores, Mapping):
        raise ValueError("scores must be an object keyed by rubric criterion")

    unknown = sorted(set(scores) - set(CRITERION_KEYS))
    if unknown:
        raise ValueError("unknown criteria: " + ", ".join(unknown))

    normalized: dict[str, int | float | None] = {}
    missing: list[str] = []
    weighted_total = 0.0
    assessed_weight = 0
    for criterion in CRITERIA:
        key = criterion["key"]
        value = scores.get(key)
        if value is None or value == "":
            normalized[key] = None
            missing.append(key)
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{key} must be a number from 0 to {MAX_SCORE}, or null")
        if value < 0 or value > MAX_SCORE:
            raise ValueError(f"{key} must be between 0 and {MAX_SCORE}")
        normalized[key] = value
        weighted_total += float(value) * criterion["weight"]
        assessed_weight += criterion["weight"]

    complete = not missing
    score = round(weighted_total / WEIGHT_TOTAL * 20, 2) if complete else None
    return {
        "programme_id": identifier,
        "scores": normalized,
        "score": score,
        "coverage_percent": round(assessed_weight / WEIGHT_TOTAL * 100, 1),
        "assessment_status": "complete" if complete else "incomplete",
        "missing_criteria": missing,
        "rank_eligible": complete,
        "human_review_required": True,
        "scientific_validity_established": False,
    }


def rank_assessments(assessments: list[Mapping[str, Any]]) -> dict[str, Any]:
    """Rank only complete, validated assessment records; leave the rest visible."""
    if not isinstance(assessments, list):
        raise ValueError("assessments must be a list")
    evaluated = []
    seen: set[str] = set()
    for item in assessments:
        if not isinstance(item, Mapping):
            raise ValueError("each assessment must be an object")
        result = score_assessment(item.get("programme_id", ""), item.get("scores", {}))
        if result["programme_id"] in seen:
            raise ValueError("programme_id values must be unique")
        seen.add(result["programme_id"])
        evaluated.append(result)

    ranked = sorted(
        (item for item in evaluated if item["rank_eligible"]),
        key=lambda item: (-item["score"], item["programme_id"].casefold()),
    )
    incomplete = sorted(
        (item for item in evaluated if not item["rank_eligible"]),
        key=lambda item: item["programme_id"].casefold(),
    )
    for position, item in enumerate(ranked, start=1):
        item["rank"] = position
    return {
        "ranked": ranked,
        "incomplete": incomplete,
        "ranked_count": len(ranked),
        "incomplete_count": len(incomplete),
        "ranking_is_advisory": True,
        "automatic_funding_decisions": False,
        "scientific_validity_established": False,
    }

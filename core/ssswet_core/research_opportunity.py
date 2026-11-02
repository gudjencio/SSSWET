"""Transparent research opportunity scoring with graph-derived leverage.

All judgement inputs are explicitly supplied by reviewers. Missing information
prevents ranking; dependency leverage is computed only from supported graph
edges and only when graph coverage has been reviewed as complete.
"""
from __future__ import annotations

from typing import Any, Mapping

CRITERIA = (
    {"key": "evidence_maturity", "weight": 20, "label": "Evidence maturity"},
    {"key": "technical_feasibility", "weight": 20, "label": "Technical feasibility"},
    {"key": "next_experiment_readiness", "weight": 15, "label": "Readiness of the next test"},
    {"key": "resource_efficiency", "weight": 15, "label": "Resource efficiency"},
    {"key": "safety_legal_readiness", "weight": 20, "label": "Safety and legal readiness"},
    {"key": "dependency_leverage", "weight": 10, "label": "Supported downstream leverage"},
)
SCORE_KEYS = tuple(item["key"] for item in CRITERIA)


def evaluate_research_opportunity(
    programme_id: str,
    inputs: Mapping[str, Any],
    dependency_graph: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Score a fully evidenced opportunity; never infer missing human judgements."""
    if not isinstance(programme_id, str) or not programme_id.strip() or len(programme_id) > 160:
        raise ValueError("programme_id must contain between 1 and 160 characters")
    if not isinstance(inputs, Mapping):
        raise ValueError("inputs must be an object")
    allowed = {"evidence_maturity", "technical_feasibility",
               "next_experiment_readiness", "resource_efficiency",
               "safety_legal_readiness", "dependency_review_complete"}
    unknown = sorted(set(inputs) - allowed)
    if unknown:
        raise ValueError("unknown inputs: " + ", ".join(unknown))

    graph_complete = inputs.get("dependency_review_complete")
    if not isinstance(graph_complete, bool):
        raise ValueError("dependency_review_complete must be explicitly true or false")
    if graph_complete and not isinstance(dependency_graph, Mapping):
        raise ValueError("a dependency graph is required when graph review is complete")

    downstream = None
    if graph_complete:
        relations = dependency_graph.get("relations")
        if not isinstance(relations, list):
            raise ValueError("dependency graph must contain a relations list")
        supported = set()
        for relation in relations:
            if not isinstance(relation, Mapping):
                raise ValueError("each dependency relation must be an object")
            if relation.get("state") == "supported" and relation.get("prerequisite_id") == programme_id:
                if relation.get("relation_type") == "prerequisite":
                    supported.add(relation.get("dependent_id"))
                elif relation.get("relation_type") == "enables":
                    supported.add(relation.get("dependent_id"))
        if None in supported:
            raise ValueError("supported graph relations require dependent programme identifiers")
        downstream = len(supported)
        leverage_score = min(5.0, float(downstream))
    else:
        leverage_score = None

    scores = {}
    missing = []
    for key in SCORE_KEYS[:-1]:
        value = inputs.get(key)
        if value is None:
            scores[key] = None
            missing.append(key)
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 5:
            raise ValueError(f"{key} must be a number from 0 to 5, or null")
        scores[key] = float(value)
    scores["dependency_leverage"] = leverage_score
    if not graph_complete:
        missing.append("dependency_leverage")

    complete = not missing
    weighted = sum(float(scores[item["key"]]) * item["weight"]
                   for item in CRITERIA if scores[item["key"]] is not None)
    assessed_weight = sum(item["weight"] for item in CRITERIA
                          if scores[item["key"]] is not None)
    score = round(weighted / 5, 2) if complete else None
    return {
        "programme_id": programme_id,
        "scores": scores,
        "score": score,
        "coverage_percent": round(assessed_weight, 1),
        "downstream_programmes_unlocked": downstream,
        "assessment_status": "complete" if complete else "incomplete",
        "missing_criteria": missing,
        "rank_eligible": complete,
        "interpretation": "Advisory research opportunity index; not a probability, scientific result, safety certificate, or funding decision.",
        "human_review_required": True,
        "automatic_funding_decisions": False,
        "scientific_validity_established": False,
    }


def rank_research_opportunities(items: list[Mapping[str, Any]], dependency_graph: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    evaluated = []
    seen = set()
    for item in items:
        if not isinstance(item, Mapping):
            raise ValueError("each opportunity must be an object")
        result = evaluate_research_opportunity(
            item.get("programme_id", ""), item.get("inputs", {}), dependency_graph
        )
        if result["programme_id"] in seen:
            raise ValueError("programme identifiers must be unique")
        seen.add(result["programme_id"])
        evaluated.append(result)
    ranked = sorted((x for x in evaluated if x["rank_eligible"]),
                    key=lambda x: (-x["score"], x["programme_id"].casefold()))
    incomplete = sorted((x for x in evaluated if not x["rank_eligible"]),
                        key=lambda x: x["programme_id"].casefold())
    for index, item in enumerate(ranked, 1):
        item["rank"] = index
    return {
        "ranked": ranked, "incomplete": incomplete,
        "ranked_count": len(ranked), "incomplete_count": len(incomplete),
        "ranking_is_advisory": True, "automatic_funding_decisions": False,
        "scientific_validity_established": False,
    }

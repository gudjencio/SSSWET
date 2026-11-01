"""Deterministic, bounded adaptive proposals for simulation scenarios.

The optimizer ranks only caller-supplied candidate scenarios and explicitly
scored observations. It does not invent parameter ranges, execute models,
estimate statistical confidence, or claim global optimality.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any
import json
import math


@dataclass(frozen=True)
class ScenarioObservation:
    scenario_id: str
    score: float


@dataclass(frozen=True)
class ScenarioProposal:
    scenario_id: str
    parameters: dict[str, Any]
    predicted_score: float
    exploration_score: float
    selection_score: float
    nearest_observation_id: str
    rationale: str


@dataclass(frozen=True)
class OptimizationReport:
    direction: str
    proposals: tuple[ScenarioProposal, ...]
    excluded_observed: tuple[str, ...]
    warnings: tuple[str, ...]


class AdaptiveScenarioOptimizer:
    """Rank a finite candidate set using nearest-neighbour estimates.

    The combined ranking gives equal weight to predicted objective quality
    and distance from prior observations. Scores are heuristics, not
    probabilities or confidence intervals.
    """

    @staticmethod
    def _canonical(parameters: dict[str, Any]) -> str:
        return json.dumps(
            parameters, ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        )

    def propose(
        self,
        candidates: list[Any],
        observations: list[ScenarioObservation],
        count: int = 3,
        direction: str = "maximize",
    ) -> OptimizationReport:
        if direction not in {"maximize", "minimize"}:
            raise ValueError("direction must be 'maximize' or 'minimize'")
        if not isinstance(count, int) or isinstance(count, bool) or count < 1:
            raise ValueError("count must be a positive integer")
        if not candidates:
            raise ValueError("At least one explicit candidate is required")
        if len(candidates) > 10000:
            raise ValueError("At most 10000 candidates may be ranked")
        if len(observations) > 10000:
            raise ValueError("At most 10000 observations may be used")

        candidate_ids = [item.scenario_id for item in candidates]
        if any(not isinstance(value, str) or not value.strip() for value in candidate_ids):
            raise ValueError("Candidate scenario IDs must be non-empty strings")
        if len(set(candidate_ids)) != len(candidate_ids):
            raise ValueError("Candidate scenario IDs must be unique")
        for item in candidates:
            if not isinstance(item.parameters, dict):
                raise ValueError("Candidate parameters must be dictionaries")
            self._canonical(item.parameters)

        observation_ids = [item.scenario_id for item in observations]
        if len(set(observation_ids)) != len(observation_ids):
            raise ValueError("Observation scenario IDs must be unique")
        if any(not math.isfinite(float(item.score)) for item in observations):
            raise ValueError("Observation scores must be finite numbers")
        if not observations:
            raise ValueError("At least one scored observation is required")

        observed_ids = set(observation_ids)
        observed_candidates = set()
        for candidate in candidates:
            if candidate.scenario_id in observed_ids:
                observed_candidates.add(candidate.scenario_id)

        # Only parameters that are numeric and consistently present in every
        # candidate and observed scenario contribute to geometric distance.
        # Observations contain scores only, so parameter vectors for them are
        # obtained from candidates by matching their scenario IDs.
        candidate_by_id = {item.scenario_id: item for item in candidates}
        observed_vectors = [
            candidate_by_id[item.scenario_id].parameters
            for item in observations if item.scenario_id in candidate_by_id
        ]
        if not observed_vectors:
            raise ValueError(
                "Each observation must refer to a candidate scenario so its parameters are known"
            )
        keys = set(candidates[0].parameters)
        for item in candidates:
            keys &= set(item.parameters)
        for vector in observed_vectors:
            keys &= set(vector)
        numeric_keys = sorted(
            key for key in keys
            if all(
                isinstance(item.parameters[key], (int, float))
                and not isinstance(item.parameters[key], bool)
                and math.isfinite(float(item.parameters[key]))
                for item in candidates
            )
            and all(
                isinstance(vector[key], (int, float))
                and not isinstance(vector[key], bool)
                and math.isfinite(float(vector[key]))
                for vector in observed_vectors
            )
        )
        if not numeric_keys:
            raise ValueError("At least one shared finite numeric parameter is required")

        bounds = {
            key: (
                min(float(item.parameters[key]) for item in candidates),
                max(float(item.parameters[key]) for item in candidates),
            )
            for key in numeric_keys
        }

        def distance(left: dict[str, Any], right: dict[str, Any]) -> float:
            terms = []
            for key in numeric_keys:
                low, high = bounds[key]
                scale = high - low
                delta = 0.0 if scale == 0 else (
                    float(left[key]) - float(right[key])
                ) / scale
                terms.append(delta * delta)
            return math.sqrt(sum(terms) / len(terms))

        scores = {item.scenario_id: float(item.score) for item in observations}
        best = (max if direction == "maximize" else min)(scores.values())
        worst = (min if direction == "maximize" else max)(scores.values())
        score_span = best - worst

        ranked = []
        excluded = []
        for candidate in candidates:
            if candidate.scenario_id in observed_ids:
                excluded.append(candidate.scenario_id)
                continue
            neighbours = [
                (distance(candidate.parameters, candidate_by_id[item.scenario_id].parameters), item)
                for item in observations if item.scenario_id in candidate_by_id
            ]
            nearest_distance, nearest = min(neighbours, key=lambda pair: (pair[0], pair[1].scenario_id))
            predicted = scores[nearest.scenario_id]
            exploitation = (
                0.5 if score_span == 0 else
                ((predicted - worst) / score_span if direction == "maximize"
                 else (worst - predicted) / score_span)
            )
            exploration = min(1.0, nearest_distance)
            selection = 0.5 * exploitation + 0.5 * exploration
            ranked.append(ScenarioProposal(
                candidate.scenario_id,
                dict(candidate.parameters),
                predicted,
                exploration,
                selection,
                nearest.scenario_id,
                "Nearest-neighbour score estimate combined equally with normalized distance from observed scenarios; heuristic only.",
            ))

        ranked.sort(key=lambda item: (-item.selection_score, item.scenario_id))
        warnings = (
            "Proposals are selected only from the finite candidate set supplied by the operator.",
            "Predicted scores use nearest-neighbour carry-forward, not a fitted or validated scientific model.",
            "Exploration and selection scores are heuristics, not probabilities, confidence intervals, or proof of optimality.",
            "Results depend on the supplied objective scores, candidate ranges, and parameter scaling.",
        )
        return OptimizationReport(
            direction, tuple(ranked[:count]), tuple(sorted(excluded)), warnings
        )

    @staticmethod
    def to_dict(report: OptimizationReport) -> dict[str, Any]:
        return asdict(report)

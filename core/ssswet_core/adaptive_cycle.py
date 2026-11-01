"""Human-scored bridge from completed simulation studies to adaptive proposals."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .adaptive_optimization import (
    AdaptiveScenarioOptimizer,
    OptimizationReport,
    ScenarioObservation,
)
from .simulation_study import SimulationScenario, SimulationStudy


@dataclass(frozen=True)
class AdaptiveCycle:
    study_id: str
    report: OptimizationReport
    reviewed_scenario_ids: tuple[str, ...]


def propose_from_study(
    study: SimulationStudy,
    candidates: list[SimulationScenario],
    reviewed_scores: dict[str, float],
    count: int = 3,
    direction: str = "maximize",
) -> AdaptiveCycle:
    """Propose new scenarios using scores explicitly assessed by a human.

    A score is accepted only for a scenario represented by at least two
    successfully completed model runs in the supplied study. The score itself
    is provided by the caller; model outputs are never silently converted
    into objective scores.
    """
    if not study.study_id.strip():
        raise ValueError("A study ID is required")
    if not reviewed_scores:
        raise ValueError("At least one human-reviewed objective score is required")
    successful_counts: dict[str, int] = {}
    for run in study.runs:
        if run.status == "completed":
            successful_counts[run.scenario_id] = successful_counts.get(run.scenario_id, 0) + 1
    observations = []
    for scenario_id, score in reviewed_scores.items():
        if successful_counts.get(scenario_id, 0) < 2:
            raise ValueError(
                f"Scenario {scenario_id!r} needs at least two completed model runs before scoring"
            )
        observations.append(ScenarioObservation(scenario_id, score))
    report = AdaptiveScenarioOptimizer().propose(
        candidates, observations, count=count, direction=direction
    )
    return AdaptiveCycle(
        study.study_id,
        report,
        tuple(sorted(reviewed_scores)),
    )


def adaptive_cycle_to_dict(cycle: AdaptiveCycle) -> dict[str, Any]:
    return {
        "study_id": cycle.study_id,
        "reviewed_scenario_ids": list(cycle.reviewed_scenario_ids),
        "report": AdaptiveScenarioOptimizer.to_dict(cycle.report),
        "execution_state": "proposal_only",
        "requires_human_approval_before_execution": True,
    }

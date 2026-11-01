"""Read-only planning for explicitly nominated pairwise parameter interactions.

The planner proposes balanced two-factor grids from protocol metadata. It
does not analyze outcomes, estimate interaction effects, or execute studies.
"""
from __future__ import annotations

from itertools import product
from typing import Any

from .parameter_sensitivity import (
    ParameterSensitivityPlanner,
    _fingerprint,
)


class ParameterInteractionPlanner:
    """Build bounded pairwise factorial scenarios for human review."""

    MAX_SCENARIOS_PER_PROTOCOL = 500

    def __init__(self, store):
        self.store = store

    def build(self, limit: int = 200) -> dict:
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 500:
            raise ValueError("limit must be an integer between 1 and 500")

        plans = []
        for protocol in self.store.lab_protocol_history(limit=limit):
            if protocol.get("state") != "published":
                continue
            required = list(protocol.get("required_parameters") or [])
            metadata = protocol.get("parameter_sensitivity") or {}
            candidates = metadata.get("interaction_candidates", [])
            if not candidates:
                continue

            errors: list[str] = []
            if not isinstance(candidates, list):
                candidates = []
                errors.append("interaction_candidates must be a list.")

            designs = {}
            design_errors = {}
            for name in required:
                design, issues = ParameterSensitivityPlanner._parameter_design(
                    protocol, name, metadata.get(name)
                )
                if design is not None:
                    designs[name] = design
                else:
                    design_errors[name] = issues or ["No valid sensitivity definition was supplied."]

            baseline = {name: design["baseline"] for name, design in designs.items()}
            pair_plans = []
            all_scenarios = []
            seen_pairs = set()

            for index, candidate in enumerate(candidates):
                if not isinstance(candidate, dict):
                    errors.append(f"Candidate {index + 1} must be an object.")
                    continue
                pair = candidate.get("parameters")
                if (
                    not isinstance(pair, list) or len(pair) != 2
                    or any(not isinstance(name, str) or name not in required for name in pair)
                    or pair[0] == pair[1]
                ):
                    errors.append(f"Candidate {index + 1} must name two distinct required parameters.")
                    continue
                pair_key = tuple(sorted(pair))
                if pair_key in seen_pairs:
                    errors.append(f"Duplicate interaction candidate: {pair_key[0]} + {pair_key[1]}.")
                    continue
                seen_pairs.add(pair_key)

                rationale = candidate.get("rationale")
                if not isinstance(rationale, str) or not rationale.strip():
                    errors.append(f"Candidate {index + 1} requires a rationale.")
                    continue
                replicates = candidate.get("replicates")
                if isinstance(replicates, bool) or not isinstance(replicates, int) or not 2 <= replicates <= 100:
                    errors.append(f"Candidate {index + 1} replicates must be an integer between 2 and 100.")
                    continue
                if any(name not in designs for name in pair):
                    pair_plans.append({
                        "parameters": pair,
                        "classification": "incomplete_factor_metadata",
                        "errors": {
                            name: design_errors.get(name, ["No valid parameter definition."])
                            for name in pair if name not in designs
                        },
                        "scenarios": [],
                        "scenario_count": 0,
                    })
                    continue

                first, second = (designs[name] for name in pair)
                grid_count = len(first["levels"]) * len(second["levels"]) * replicates
                if len(all_scenarios) + grid_count > self.MAX_SCENARIOS_PER_PROTOCOL:
                    pair_plans.append({
                        "parameters": pair,
                        "classification": "scenario_limit_exceeded",
                        "errors": [f"Pairwise grid would exceed the {self.MAX_SCENARIOS_PER_PROTOCOL}-scenario protocol limit."],
                        "scenarios": [],
                        "scenario_count": 0,
                    })
                    continue

                pair_scenarios = []
                for first_level, second_level in product(first["levels"], second["levels"]):
                    for replicate in range(1, replicates + 1):
                        values = dict(baseline)
                        values[pair[0]] = first_level
                        values[pair[1]] = second_level
                        scenario = {
                            "protocol_id": protocol["protocol_id"],
                            "protocol_version": protocol["version"],
                            "interaction": list(pair),
                            "factor_levels": {
                                pair[0]: {"value": first_level, "unit": first["unit"]},
                                pair[1]: {"value": second_level, "unit": second["unit"]},
                            },
                            "replicate": replicate,
                            "parameters": values,
                            "execution_authorized": False,
                        }
                        scenario["scenario_id"] = _fingerprint(scenario)[:20]
                        pair_scenarios.append(scenario)
                pair_plans.append({
                    "parameters": list(pair),
                    "classification": "ready_for_human_review",
                    "rationale": rationale,
                    "design_type": "balanced_two_factor_full_factorial",
                    "levels_per_factor": {
                        pair[0]: len(first["levels"]),
                        pair[1]: len(second["levels"]),
                    },
                    "replicates_per_combination": replicates,
                    "scenario_count": len(pair_scenarios),
                    "scenarios": pair_scenarios,
                    "other_parameters_held_at_baseline": [
                        name for name in required if name not in pair
                    ],
                    "run_order": "not_assigned; randomization and blocking require human review",
                    "interaction_effect_estimated": False,
                    "causality_established": False,
                })
                all_scenarios.extend(pair_scenarios)

            valid_pairs = sum(
                pair.get("classification") == "ready_for_human_review"
                for pair in pair_plans
            )
            plans.append({
                "plan_id": _fingerprint({
                    "protocol_id": protocol["protocol_id"],
                    "protocol_version": protocol["version"],
                    "candidates": candidates,
                    "pair_plans": [
                        {key: value for key, value in pair.items() if key != "scenarios"}
                        for pair in pair_plans
                    ],
                    "errors": errors,
                })[:24],
                "protocol_id": protocol["protocol_id"],
                "protocol_version": protocol["version"],
                "protocol_title": protocol.get("title", ""),
                "classification": (
                    "ready_for_human_review"
                    if valid_pairs == len(candidates) and not errors
                    else "incomplete_or_limited"
                ),
                "candidate_pair_count": len(candidates),
                "ready_pair_count": valid_pairs,
                "pair_plans": pair_plans,
                "errors": errors,
                "scenario_count": len(all_scenarios),
                "design_scope": "explicitly_nominated_pairwise_interactions_only",
                "interaction_effects_established": False,
                "causal_effects_established": False,
                "observed_trends": [],
                "requires_human_review": True,
                "human_approval_required_before_execution": True,
                "randomization_required_before_execution": True,
                "automatic_task_creation": False,
                "automatic_execution": False,
                "scientific_validity_established": False,
                "interpretation": (
                    "These are proposed pairwise factorial scenarios, not observations. "
                    "No interaction effect or causal relationship has been estimated. "
                    "Randomization, blocking, outcome analysis, power and uncertainty review remain outstanding."
                ),
            })

        return {
            "plans": plans,
            "count": len(plans),
            "ready_for_human_review": sum(
                plan["classification"] == "ready_for_human_review" for plan in plans
            ),
            "automatic_task_creation": False,
            "automatic_execution": False,
            "scientific_validity_established": False,
            "read_only": True,
        }

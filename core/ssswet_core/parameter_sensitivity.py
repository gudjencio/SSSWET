"""Read-only, evidence-bounded parameter sensitivity study planning.

Plans are generated only from explicit protocol metadata. This module never
executes experiments, creates tasks, estimates causal effects, or treats a
planned design as observed evidence.
"""
from __future__ import annotations

from hashlib import sha256
from math import isfinite
from typing import Any
import json


def _finite_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and isfinite(float(value))
    )


def _fingerprint(value: dict) -> str:
    canonical = json.dumps(
        value, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False,
    )
    return sha256(canonical.encode("utf-8")).hexdigest()


class ParameterSensitivityPlanner:
    """Build transparent one-factor-at-a-time designs from published protocols."""

    def __init__(self, store):
        self.store = store

    @staticmethod
    def _parameter_design(protocol: dict, parameter: str, spec: Any) -> tuple[dict | None, list[str]]:
        errors: list[str] = []
        if not isinstance(spec, dict):
            return None, ["Parameter design must be an object."]
        unit = spec.get("unit")
        protocol_unit = (protocol.get("units") or {}).get(parameter)
        if not isinstance(unit, str) or not unit.strip():
            errors.append("A non-empty unit is required.")
        elif not isinstance(protocol_unit, str) or unit != protocol_unit:
            errors.append("The design unit must exactly match the protocol's declared unit.")

        value_range = spec.get("range")
        if not isinstance(value_range, dict):
            errors.append("An explicit numeric range is required.")
            minimum = maximum = None
        else:
            minimum = value_range.get("minimum")
            maximum = value_range.get("maximum")
            if not _finite_number(minimum) or not _finite_number(maximum):
                errors.append("Range minimum and maximum must be finite numbers.")
            elif float(minimum) >= float(maximum):
                errors.append("Range minimum must be lower than range maximum.")

        baseline = spec.get("baseline")
        if not _finite_number(baseline):
            errors.append("A finite baseline value is required.")
        elif _finite_number(minimum) and _finite_number(maximum) and not float(minimum) <= float(baseline) <= float(maximum):
            errors.append("Baseline must lie inside the declared range.")

        levels = spec.get("levels")
        if not isinstance(levels, list) or not 3 <= len(levels) <= 9:
            errors.append("Provide between 3 and 9 explicit numeric levels.")
            levels = []
        elif any(not _finite_number(item) for item in levels):
            errors.append("Every level must be a finite number.")
        elif len({float(item) for item in levels}) != len(levels):
            errors.append("Parameter levels must be unique.")
        elif _finite_number(minimum) and _finite_number(maximum) and any(
            not float(minimum) <= float(item) <= float(maximum) for item in levels
        ):
            errors.append("Every level must lie inside the declared range.")
        if _finite_number(baseline) and levels and all(
            _finite_number(item) for item in levels
        ) and float(baseline) not in {float(item) for item in levels}:
            errors.append("The baseline must be included among the tested levels.")

        uncertainty = spec.get("measurement_uncertainty")
        if not isinstance(uncertainty, dict) or not _finite_number(uncertainty.get("value")) or float(uncertainty.get("value", -1)) < 0:
            errors.append("A finite, non-negative measurement uncertainty is required.")
        elif uncertainty.get("unit") != unit:
            errors.append("Measurement uncertainty must use the parameter's declared unit.")

        replicates = spec.get("replicates")
        if isinstance(replicates, bool) or not isinstance(replicates, int) or not 2 <= replicates <= 100:
            errors.append("Replicates must be an integer between 2 and 100.")
        safety = spec.get("safety_constraints")
        if not isinstance(safety, str) or not safety.strip():
            errors.append("Explicit safety constraints and operating boundaries are required.")
        rationale = spec.get("rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            errors.append("A rationale for varying this parameter is required.")

        if errors:
            return None, errors
        return {
            "parameter": parameter,
            "unit": unit,
            "range": {"minimum": minimum, "maximum": maximum},
            "baseline": baseline,
            "levels": levels,
            "measurement_uncertainty": uncertainty,
            "replicates": replicates,
            "safety_constraints": safety,
            "rationale": rationale,
        }, []

    def build(self, limit: int = 200) -> dict:
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 500:
            raise ValueError("limit must be an integer between 1 and 500")

        protocols = self.store.lab_protocol_history(limit=limit)
        plans = []
        for protocol in protocols:
            if protocol.get("state") != "published":
                continue
            required = protocol.get("required_parameters") or []
            configured = protocol.get("parameter_sensitivity") or {}
            if not required:
                continue
            parameter_designs = []
            errors_by_parameter = {}
            for parameter in required:
                design, errors = self._parameter_design(
                    protocol, parameter, configured.get(parameter)
                )
                if design is None:
                    errors_by_parameter[parameter] = errors or ["No sensitivity design was supplied."]
                else:
                    parameter_designs.append(design)

            ready = len(parameter_designs) == len(required) and not errors_by_parameter
            baseline = {
                item["parameter"]: item["baseline"] for item in parameter_designs
            }
            scenarios = []
            if ready:
                for design in parameter_designs:
                    for level in design["levels"]:
                        values = dict(baseline)
                        values[design["parameter"]] = level
                        for replicate in range(1, design["replicates"] + 1):
                            scenario = {
                                "protocol_id": protocol["protocol_id"],
                                "protocol_version": protocol["version"],
                                "parameter": design["parameter"],
                                "level": level,
                                "unit": design["unit"],
                                "replicate": replicate,
                                "parameters": values,
                                "execution_authorized": False,
                            }
                            scenario["scenario_id"] = _fingerprint(scenario)[:20]
                            scenarios.append(scenario)

            plan = {
                "plan_id": _fingerprint({
                    "protocol_id": protocol["protocol_id"],
                    "protocol_version": protocol["version"],
                    "parameter_designs": parameter_designs,
                    "errors": errors_by_parameter,
                })[:24],
                "protocol_id": protocol["protocol_id"],
                "protocol_version": protocol["version"],
                "protocol_title": protocol.get("title", ""),
                "classification": "ready_for_human_review" if ready else "incomplete_design",
                "design_type": "one_factor_at_a_time",
                "required_parameter_count": len(required),
                "configured_parameter_count": len(parameter_designs),
                "parameter_designs": parameter_designs,
                "missing_or_invalid_designs": errors_by_parameter,
                "baseline_parameters": baseline if ready else {},
                "scenarios": scenarios,
                "scenario_count": len(scenarios),
                "parameter_interactions": "not_assessed",
                "causal_effects_established": False,
                "observed_trends": [],
                "requires_human_review": True,
                "human_approval_required_before_execution": True,
                "automatic_task_creation": False,
                "automatic_execution": False,
                "scientific_validity_established": False,
                "interpretation": (
                    "This is a proposed controlled design, not an experiment or an observation. "
                    "One-factor-at-a-time plans do not estimate parameter interactions or establish causality."
                ),
            }
            plans.append(plan)

        return {
            "plans": plans,
            "count": len(plans),
            "ready_for_human_review": sum(
                item["classification"] == "ready_for_human_review" for item in plans
            ),
            "automatic_task_creation": False,
            "automatic_execution": False,
            "scientific_validity_established": False,
            "read_only": True,
        }

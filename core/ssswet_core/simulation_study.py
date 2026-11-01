"""Reproducible, bounded comparison of explicit computational simulation models.

This runner invokes only caller-supplied Python callables. It does not execute
physical experiments, provide a scientific model by itself, or infer truth from
agreement. Scenario parameters are explicit and recorded with each run.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
from typing import Any, Callable
import json


@dataclass(frozen=True)
class SimulationScenario:
    scenario_id: str
    parameters: dict[str, Any]


@dataclass(frozen=True)
class SimulationModelRun:
    model_id: str
    provider: str
    scenario_id: str
    status: str
    parameters_json: str
    output_json: str
    output_hash: str
    error_type: str = ""


@dataclass(frozen=True)
class SimulationStudy:
    study_id: str
    objective: str
    runs: tuple[SimulationModelRun, ...]
    scenario_agreement: dict[str, str]
    warnings: tuple[str, ...]


class MultiModelSimulationRunner:
    """Run explicitly supplied models against the same bounded scenarios."""

    def run(
        self,
        study_id: str,
        objective: str,
        scenarios: list[SimulationScenario],
        models: dict[str, tuple[str, Callable[[dict[str, Any]], Any]]],
    ) -> SimulationStudy:
        if not study_id.strip() or not objective.strip():
            raise ValueError("study_id and objective are required")
        if not scenarios:
            raise ValueError("At least one explicit scenario is required")
        if len(scenarios) > 100:
            raise ValueError("A study is limited to 100 scenarios")
        if len(models) < 2:
            raise ValueError("At least two configured models are required")
        if len(models) > 20:
            raise ValueError("A study is limited to 20 models")
        scenario_ids = [item.scenario_id for item in scenarios]
        if any(not item.strip() for item in scenario_ids) or len(set(scenario_ids)) != len(scenario_ids):
            raise ValueError("Scenario IDs must be non-empty and unique")
        for model_id, (provider, invoke) in models.items():
            if not model_id.strip() or not provider.strip() or not callable(invoke):
                raise ValueError("Each model needs an ID, provider name and callable")

        runs: list[SimulationModelRun] = []
        agreements: dict[str, str] = {}
        for scenario in scenarios:
            parameters_json = json.dumps(
                scenario.parameters, ensure_ascii=False, sort_keys=True,
                separators=(",", ":"), allow_nan=False,
            )
            scenario_hashes: set[str] = set()
            successful = 0
            for model_id, (provider, invoke) in models.items():
                try:
                    output = invoke(dict(scenario.parameters))
                    output_json = json.dumps(
                        output, ensure_ascii=False, sort_keys=True,
                        separators=(",", ":"), default=str, allow_nan=False,
                    )
                    digest = sha256(output_json.encode("utf-8")).hexdigest()
                    successful += 1
                    scenario_hashes.add(digest)
                    runs.append(SimulationModelRun(
                        model_id, provider, scenario.scenario_id, "completed",
                        parameters_json, output_json, digest,
                    ))
                except Exception as exc:
                    runs.append(SimulationModelRun(
                        model_id, provider, scenario.scenario_id, "failed",
                        parameters_json, "", sha256(b"").hexdigest(),
                        type(exc).__name__,
                    ))
            if successful < 2:
                agreements[scenario.scenario_id] = "insufficient_outputs"
            elif len(scenario_hashes) == 1:
                agreements[scenario.scenario_id] = "identical_outputs"
            else:
                agreements[scenario.scenario_id] = "divergent_outputs"

        warnings = [
            "Outputs are computational simulation results, not real-world observations.",
            "Agreement does not establish model validity, independence, or scientific truth.",
            "Model assumptions, equations, units, calibration and domain of validity require expert review.",
            "Only the supplied parameter values were varied; no unrequested parameter search was performed.",
        ]
        if any(run.status == "failed" for run in runs):
            warnings.append("At least one model run failed; affected scenario comparisons may be incomplete.")
        if any(value == "divergent_outputs" for value in agreements.values()):
            warnings.append("Divergent outputs should be investigated; this runner does not select a winning model.")
        return SimulationStudy(study_id, objective, tuple(runs), agreements, tuple(warnings))

    @staticmethod
    def to_dict(study: SimulationStudy) -> dict[str, Any]:
        return asdict(study)

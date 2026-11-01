"""Structured, review-first experimental planning and result comparison.

Plans are proposals. Simulated outputs and real observations are stored as
separate record types and are never automatically promoted to verified facts.
"""
from dataclasses import dataclass, asdict
from typing import Any
import json


PLAN_STATES = {"draft", "ready_for_review", "approved_for_execution", "archived"}
EXECUTION_KINDS = {"simulation", "real_observation"}
ASSESSMENT_STATES = {"consistent_with_prediction", "inconsistent_with_prediction", "inconclusive"}


@dataclass(frozen=True)
class ExperimentPlan:
    experiment_id: str
    hypothesis_id: str
    objective: str
    prediction: str
    independent_variables: tuple[str, ...] = ()
    dependent_variables: tuple[str, ...] = ()
    controlled_variables: tuple[str, ...] = ()
    protocol: tuple[str, ...] = ()
    controls_and_baselines: tuple[str, ...] = ()
    falsification_criteria: tuple[str, ...] = ()
    safety_notes: tuple[str, ...] = ()
    missing_information: tuple[str, ...] = ()
    state: str = "draft"


@dataclass(frozen=True)
class ExperimentRecord:
    record_id: str
    experiment_id: str
    kind: str
    values: dict[str, Any]
    method: str
    limitations: tuple[str, ...] = ()
    source_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ExperimentAssessment:
    record_id: str
    state: str
    explanation: str
    criteria_evaluated: tuple[str, ...]
    requires_human_review: bool = True


def draft_experiment_plan(
    experiment_id: str,
    hypothesis_id: str,
    hypothesis_text: str,
) -> ExperimentPlan:
    """Create a transparent scaffold; never invent variables or a protocol."""
    text = hypothesis_text.strip()
    if not experiment_id.strip() or not hypothesis_id.strip() or not text:
        raise ValueError("experiment_id, hypothesis_id and hypothesis_text are required")
    return ExperimentPlan(
        experiment_id=experiment_id.strip(),
        hypothesis_id=hypothesis_id.strip(),
        objective=f"Design a test of the hypothesis: {text}",
        prediction="RESEARCHER INPUT REQUIRED: state a measurable prediction.",
        missing_information=(
            "independent_variables",
            "dependent_variables",
            "controlled_variables",
            "protocol",
            "controls_and_baselines",
            "falsification_criteria",
            "domain_specific_safety_review",
        ),
        safety_notes=("Do not execute until risks, permissions and domain-specific safeguards are reviewed.",),
        state="draft",
    )


def validate_experiment_plan(plan: ExperimentPlan) -> list[str]:
    if plan.state not in PLAN_STATES:
        raise ValueError(f"Unsupported plan state: {plan.state}")
    required = {
        "prediction": plan.prediction,
        "independent_variables": plan.independent_variables,
        "dependent_variables": plan.dependent_variables,
        "protocol": plan.protocol,
        "controls_and_baselines": plan.controls_and_baselines,
        "falsification_criteria": plan.falsification_criteria,
    }
    missing = list(plan.missing_information)
    for key, value in required.items():
        if not value or (isinstance(value, str) and ("RESEARCHER INPUT REQUIRED" in value)):
            if key not in missing:
                missing.append(key)
    if not plan.hypothesis_id.strip() or not plan.objective.strip():
        raise ValueError("A hypothesis reference and objective are required")
    return sorted(set(missing))


def make_experiment_record(
    record_id: str,
    experiment_id: str,
    kind: str,
    values: dict[str, Any],
    method: str,
    limitations: tuple[str, ...] = (),
    source_ids: tuple[str, ...] = (),
) -> ExperimentRecord:
    if kind not in EXECUTION_KINDS:
        raise ValueError(f"Unsupported execution kind: {kind}")
    if not record_id.strip() or not experiment_id.strip() or not method.strip():
        raise ValueError("record_id, experiment_id and method are required")
    if not isinstance(values, dict):
        raise ValueError("values must be a dictionary")
    return ExperimentRecord(
        record_id=record_id, experiment_id=experiment_id, kind=kind,
        values=values, method=method, limitations=tuple(limitations),
        source_ids=tuple(source_ids),
    )


def compare_record_to_prediction(
    record: ExperimentRecord,
    prediction_key: str,
    expected_value: Any,
    tolerance: float | None = None,
) -> ExperimentAssessment:
    """Compare an explicitly supplied value; this is not scientific validation."""
    if prediction_key not in record.values:
        return ExperimentAssessment(
            record.record_id, "inconclusive",
            f"No observed value was supplied for '{prediction_key}'.",
            (), True,
        )
    observed = record.values[prediction_key]
    if tolerance is not None:
        if tolerance < 0:
            raise ValueError("tolerance must be non-negative")
        try:
            consistent = abs(float(observed) - float(expected_value)) <= tolerance
        except (TypeError, ValueError):
            return ExperimentAssessment(
                record.record_id, "inconclusive",
                "Numeric tolerance comparison requires numeric observed and expected values.",
                (), True,
            )
    else:
        consistent = observed == expected_value
    state = "consistent_with_prediction" if consistent else "inconsistent_with_prediction"
    label = "matches" if consistent else "does not match"
    return ExperimentAssessment(
        record.record_id, state,
        f"The recorded value {observed!r} {label} the supplied prediction {expected_value!r}. "
        "This comparison alone does not establish or refute the hypothesis.",
        (f"{prediction_key}: observed={observed!r}; expected={expected_value!r}",),
        True,
    )


def plan_to_dict(plan: ExperimentPlan) -> dict:
    return asdict(plan)


def record_to_dict(record: ExperimentRecord) -> dict:
    return asdict(record)


def assessment_to_dict(assessment: ExperimentAssessment) -> dict:
    return asdict(assessment)

"""Explicit hypothesis-versus-observation matrix with conservative outcomes.

Only declared variable/condition matches are evaluated. No statistical
significance, causal effect, or scientific truth is inferred.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Iterable


MAX_HYPOTHESES = 100
MAX_PREDICTIONS = 500
MAX_OBSERVATIONS = 2000


def _norm(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("comparison fields must be text")
    return re.sub(r"\s+", " ", value.strip().casefold())


@dataclass(frozen=True)
class Prediction:
    variable: str
    expected_value: str
    conditions: str = ""
    disconfirming_value: str = ""

    def __post_init__(self) -> None:
        if not _norm(self.variable) or not _norm(self.expected_value):
            raise ValueError("prediction variable and expected_value are required")
        for name in ("conditions", "disconfirming_value"):
            _norm(getattr(self, name))


@dataclass(frozen=True)
class Hypothesis:
    hypothesis_id: str
    statement: str
    predictions: tuple[Prediction, ...]
    version: int = 1
    supersedes_id: str = ""

    def __post_init__(self) -> None:
        if not _norm(self.hypothesis_id) or not _norm(self.statement):
            raise ValueError("hypothesis ID and statement are required")
        if not isinstance(self.version, int) or isinstance(self.version, bool) or self.version < 1:
            raise ValueError("hypothesis version must be a positive integer")
        if self.version > 1 and not _norm(self.supersedes_id):
            raise ValueError("a revised hypothesis must identify its predecessor")
        if not isinstance(self.predictions, tuple) or not self.predictions:
            raise ValueError("at least one explicit prediction is required")
        if len(self.predictions) > MAX_PREDICTIONS or any(
            not isinstance(item, Prediction) for item in self.predictions
        ):
            raise ValueError(f"predictions must contain at most {MAX_PREDICTIONS} Prediction objects")


@dataclass(frozen=True)
class Observation:
    observation_id: str
    variable: str
    value: str
    conditions: str = ""
    source_ids: tuple[str, ...] = ()
    uncertainty_note: str = ""

    def __post_init__(self) -> None:
        for name in ("observation_id", "variable", "value"):
            if not _norm(getattr(self, name)):
                raise ValueError(f"{name} is required")
        if (not isinstance(self.source_ids, tuple) or len(self.source_ids) > 100
                or any(not isinstance(item, str) or not item.strip() for item in self.source_ids)):
            raise ValueError("observation source IDs must be a tuple of at most 100 non-empty IDs")
        if len(set(self.source_ids)) != len(self.source_ids):
            raise ValueError("observation source IDs must be unique")


def evaluate_hypotheses(
    hypotheses: Iterable[Hypothesis], observations: Iterable[Observation],
) -> dict:
    hypotheses = list(hypotheses)
    observations = list(observations)
    if not hypotheses or len(hypotheses) > MAX_HYPOTHESES:
        raise ValueError(f"hypotheses must contain 1 to {MAX_HYPOTHESES} entries")
    if len(observations) > MAX_OBSERVATIONS:
        raise ValueError(f"observations are limited to {MAX_OBSERVATIONS}")
    if any(not isinstance(item, Hypothesis) for item in hypotheses):
        raise ValueError("all hypotheses must be Hypothesis objects")
    if any(not isinstance(item, Observation) for item in observations):
        raise ValueError("all observations must be Observation objects")
    if len({item.hypothesis_id for item in hypotheses}) != len(hypotheses):
        raise ValueError("hypothesis IDs must be unique")
    if len({item.observation_id for item in observations}) != len(observations):
        raise ValueError("observation IDs must be unique")

    reports = []
    for hypothesis in hypotheses:
        results = []
        for prediction in hypothesis.predictions:
            matches = [
                observation for observation in observations
                if _norm(observation.variable) == _norm(prediction.variable)
                and _norm(observation.conditions) == _norm(prediction.conditions)
            ]
            if not matches:
                results.append({
                    "prediction": asdict(prediction), "status": "not_tested",
                    "observation_ids": [], "source_ids": [],
                })
                continue
            values = {_norm(item.value) for item in matches}
            expected = _norm(prediction.expected_value)
            disconfirming = _norm(prediction.disconfirming_value)
            if len(values) > 1:
                status = "mixed_observations"
            elif expected in values:
                status = "consistent_with_prediction"
            elif disconfirming and disconfirming in values:
                status = "inconsistent_with_prediction"
            else:
                status = "different_value_requires_review"
            results.append({
                "prediction": asdict(prediction), "status": status,
                "observation_ids": sorted(item.observation_id for item in matches),
                "source_ids": sorted({source for item in matches for source in item.source_ids}),
            })
        statuses = {item["status"] for item in results}
        overall = (
            "not_tested" if statuses == {"not_tested"} else
            "mixed" if "mixed_observations" in statuses or (
                "consistent_with_prediction" in statuses and
                any(value in statuses for value in ("inconsistent_with_prediction", "different_value_requires_review"))
            ) else
            "consistent_with_observations" if statuses == {"consistent_with_prediction"} else
            "challenged_by_observations" if statuses & {"inconsistent_with_prediction", "different_value_requires_review"} else
            "partially_tested"
        )
        reports.append({
            "hypothesis_id": hypothesis.hypothesis_id,
            "version": hypothesis.version,
            "prediction_results": results,
            "descriptive_outcome": overall,
            "automatic_hypothesis_selection": False,
            "scientific_validity_established": False,
        })
    return {
        "hypotheses": reports,
        "hypothesis_count": len(reports),
        "observation_count": len(observations),
        "unmatched_observation_count": sum(
            1 for observation in observations
            if not any(
                _norm(observation.variable) == _norm(prediction.variable)
                and _norm(observation.conditions) == _norm(prediction.conditions)
                for hypothesis in hypotheses for prediction in hypothesis.predictions
            )
        ),
        "negative_results_preserved": True,
        "automatic_hypothesis_selection": False,
    }

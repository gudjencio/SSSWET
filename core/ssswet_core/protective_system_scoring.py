"""Evidence-gated scoring for protective systems and assistive exoskeletons.

Scores describe documented development readiness and engineering trade-offs. They
must never be interpreted as a certification, a combat rating, or proof of a
specific protection level.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping

DIMENSIONS = (
    "protection_evidence",
    "mass_efficiency",
    "mobility",
    "energy_efficiency",
    "thermal_management",
    "maintainability",
    "safety",
    "human_factors",
    "cost_efficiency",
    "evidence_maturity",
)

WEIGHTS = {
    "protection_evidence": 0.20,
    "mass_efficiency": 0.08,
    "mobility": 0.08,
    "energy_efficiency": 0.05,
    "thermal_management": 0.08,
    "maintainability": 0.08,
    "safety": 0.20,
    "human_factors": 0.08,
    "cost_efficiency": 0.05,
    "evidence_maturity": 0.10,
}

REQUIRED_GATES = (
    "intended_use_defined",
    "hazards_defined",
    "measurable_test_plan_defined",
    "safety_review_complete",
)


@dataclass(frozen=True)
class DimensionScore:
    """A 0–5 score tied to explicit evidence."""

    value: float | None
    source_refs: tuple[str, ...] = ()
    evidence_status: str = "unknown"
    note: str = ""

    def __post_init__(self) -> None:
        if self.value is not None and not 0 <= self.value <= 5:
            raise ValueError("dimension scores must be between 0 and 5")
        if self.evidence_status not in {"unknown", "target", "observed", "verified"}:
            raise ValueError("invalid evidence status")
        if self.evidence_status in {"observed", "verified"} and not self.source_refs:
            raise ValueError("observed and verified scores require source references")


@dataclass(frozen=True)
class ProtectiveSystemScore:
    system_id: str
    revision: str
    dimensions: Mapping[str, DimensionScore]
    gates: Mapping[str, bool]
    weighted_score: float | None
    readiness: str
    reasons: tuple[str, ...] = field(default_factory=tuple)


def _normalise_dimension(value: object) -> DimensionScore:
    if isinstance(value, DimensionScore):
        return value
    if value is None:
        return DimensionScore(None)
    if isinstance(value, (int, float)):
        return DimensionScore(float(value), evidence_status="target")
    if isinstance(value, Mapping):
        return DimensionScore(
            value=value.get("value"),
            source_refs=tuple(value.get("source_refs", ())),
            evidence_status=value.get("evidence_status", "unknown"),
            note=value.get("note", ""),
        )
    raise TypeError("dimension input must be a DimensionScore, number, mapping, or None")


def calculate_protective_system_score(
    system_id: str,
    *,
    revision: str = "unknown",
    dimensions: Mapping[str, object],
    gates: Mapping[str, bool],
) -> ProtectiveSystemScore:
    """Calculate a score only when the evidence and safety gates permit ranking.

    Numeric inputs without evidence metadata are treated as targets, not observed
    performance. A candidate cannot receive a ranking score until every dimension
    has a documented value and all required gates are true.
    """
    if not system_id.strip():
        raise ValueError("system_id is required")
    if not revision.strip():
        raise ValueError("revision is required")

    normalised = {name: _normalise_dimension(dimensions.get(name)) for name in DIMENSIONS}
    reasons: list[str] = []

    missing_dimensions = [name for name, item in normalised.items() if item.value is None]
    if missing_dimensions:
        reasons.append("missing dimensions: " + ", ".join(missing_dimensions))

    invalid_observation = [
        name for name, item in normalised.items()
        if item.value is not None and item.evidence_status in {"observed", "verified"} and not item.source_refs
    ]
    if invalid_observation:
        reasons.append("observed or verified dimensions without sources: " + ", ".join(invalid_observation))

    missing_gates = [name for name in REQUIRED_GATES if not gates.get(name, False)]
    if missing_gates:
        reasons.append("required safety gates incomplete: " + ", ".join(missing_gates))

    weighted_score = None
    readiness = "not_ready"
    if not reasons:
        weighted_score = round(
            sum(normalised[name].value * WEIGHTS[name] for name in DIMENSIONS),
            3,
        )
        readiness = "rankable"

    return ProtectiveSystemScore(
        system_id=system_id,
        revision=revision,
        dimensions=normalised,
        gates=dict(gates),
        weighted_score=weighted_score,
        readiness=readiness,
        reasons=tuple(reasons),
    )


def rank_protective_systems(scores: Iterable[ProtectiveSystemScore]) -> list[ProtectiveSystemScore]:
    """Return only evidence-gated systems, highest score first.

    Non-rankable systems are intentionally excluded rather than assigned a zero.
    This prevents missing evidence from being mistaken for poor performance.
    """
    rankable = [item for item in scores if item.readiness == "rankable" and item.weighted_score is not None]
    return sorted(rankable, key=lambda item: (-item.weighted_score, item.system_id))

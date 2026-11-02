"""Evidence-gated progression rules for SSSWET technologies.

The progression layer turns the project's ambition into an auditable engineering
rule: a new revision must not knowingly regress a documented capability. A
revision may still be rejected, paused, or returned to research when evidence,
safety, reliability, or legality is insufficient. That is scientific persistence,
not a promise that every hypothesis will succeed.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

CAPABILITIES = (
    "usefulness",
    "performance",
    "durability",
    "efficiency",
    "safety",
    "maintainability",
    "evidence_maturity",
)

REQUIRED_EVIDENCE = {"observed", "verified"}


@dataclass(frozen=True)
class CapabilityValue:
    value: float | None
    evidence_status: str = "unknown"
    source_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.value is not None and not 0 <= self.value <= 5:
            raise ValueError("capability values must be between 0 and 5")
        if self.evidence_status not in {"unknown", "target", "observed", "verified"}:
            raise ValueError("invalid capability evidence status")
        if self.evidence_status in REQUIRED_EVIDENCE and not self.source_refs:
            raise ValueError("observed or verified capability values require source references")


@dataclass(frozen=True)
class ProgressionDecision:
    accepted: bool
    status: str
    reasons: tuple[str, ...]
    improvements: tuple[str, ...]
    regressions: tuple[str, ...]


def _normalise(value: object) -> CapabilityValue:
    if isinstance(value, CapabilityValue):
        return value
    if value is None:
        return CapabilityValue(None)
    if isinstance(value, (int, float)):
        return CapabilityValue(float(value), "target")
    if isinstance(value, Mapping):
        return CapabilityValue(
            value=value.get("value"),
            evidence_status=value.get("evidence_status", "unknown"),
            source_refs=tuple(value.get("source_refs", ())),
        )
    raise TypeError("capability must be a CapabilityValue, number, mapping, or None")


def evaluate_progression(
    previous: Mapping[str, object],
    candidate: Mapping[str, object],
    *,
    candidate_safety_gate: bool,
    candidate_legality_gate: bool,
) -> ProgressionDecision:
    """Evaluate whether a candidate revision can supersede a previous revision.

    Every known, evidence-backed capability in the previous revision becomes a
    non-regression floor. Missing candidate evidence never passes as an
    improvement. A candidate can be more advanced while remaining unapproved
    for deployment until safety, legality, and independent evidence are ready.
    """
    old = {name: _normalise(previous.get(name)) for name in CAPABILITIES}
    new = {name: _normalise(candidate.get(name)) for name in CAPABILITIES}
    reasons: list[str] = []
    improvements: list[str] = []
    regressions: list[str] = []

    for name in CAPABILITIES:
        before, after = old[name], new[name]
        if before.value is None:
            continue
        if before.evidence_status not in REQUIRED_EVIDENCE:
            continue
        if after.value is None:
            regressions.append(f"{name}: candidate value is missing")
            continue
        if after.value < before.value:
            regressions.append(f"{name}: {after.value:g} < previous {before.value:g}")
        elif after.value > before.value and after.evidence_status in REQUIRED_EVIDENCE:
            improvements.append(name)

    if regressions:
        reasons.append("candidate contains a documented capability regression")
    if not candidate_safety_gate:
        reasons.append("candidate safety gate is incomplete")
    if not candidate_legality_gate:
        reasons.append("candidate legal/compliance gate is incomplete")

    if any(
        old[name].value is not None and old[name].evidence_status in REQUIRED_EVIDENCE
        and new[name].value is not None and new[name].value > old[name].value
        and new[name].evidence_status not in REQUIRED_EVIDENCE
        for name in CAPABILITIES
    ):
        reasons.append("claimed improvements require observed or verified evidence")

    accepted = not reasons
    return ProgressionDecision(
        accepted=accepted,
        status="progression_accepted" if accepted else "progression_blocked",
        reasons=tuple(reasons),
        improvements=tuple(improvements),
        regressions=tuple(regressions),
    )


def persistence_status(reason: str, *, continue_research: bool = True) -> dict:
    """Record a non-abandonment decision without forcing unsafe experimentation."""
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("reason is required")
    return {
        "continue_research": bool(continue_research),
        "reason": reason.strip(),
        "allowed_next_steps": [
            "reassess_evidence",
            "revise_hypothesis",
            "run_safe_simulation",
            "seek_independent_review",
            "improve_design",
            "record_negative_result",
        ],
        "constraint": "Persistence never overrides safety, law, ethics, or evidence requirements.",
    }

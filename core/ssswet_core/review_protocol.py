"""Structured, conservative synthesis of independent research reviews.

A literature-search pass is not a scientific verdict. This module preserves
that distinction and keeps uncertainty and evidence provenance visible.
"""
from dataclasses import dataclass
from math import isfinite
from typing import Any


@dataclass(frozen=True)
class ReviewSynthesis:
    review_count: int
    evidence_lead_count: int
    source_ids: tuple[str, ...]
    reviewers: tuple[str, ...]
    uncertainty_levels: tuple[str, ...]
    outcome: str
    unresolved_questions: tuple[str, ...]

    def to_public_text(self) -> str:
        lines = [
            "INDEPENDENT PEER-REVIEW SYNTHESIS",
            f"Review passes recorded: {self.review_count}",
            f"Evidence leads returned: {self.evidence_lead_count}",
            f"Review outcome: {self.outcome}",
            "Uncertainty: " + (", ".join(self.uncertainty_levels) or "not reported"),
            "Reviewing roles: " + (", ".join(self.reviewers) or "not recorded"),
            "Traceable source identifiers: " + (
                ", ".join(self.source_ids) if self.source_ids else "none returned"
            ),
            "Interpretation: this synthesis records review activity only. It does not "
            "establish that any claim is true, independently reproduced, clinically "
            "validated, safe, or ready for implementation.",
            "Unresolved questions:",
        ]
        lines.extend(f"- {item}" for item in self.unresolved_questions)
        return "\n".join(lines)


def build_review_synthesis(reviews: list[dict[str, Any]]) -> ReviewSynthesis:
    """Summarise review records without promoting claims to verified findings."""
    valid = [item for item in reviews if isinstance(item, dict)]
    sources: list[str] = []
    reviewers: list[str] = []
    uncertainty_values: list[float] = []
    evidence_count = 0

    for item in valid:
        role_value = item.get("reviewer_role", "")
        role = role_value.strip()[:100] if isinstance(role_value, str) else ""
        if role and role not in reviewers:
            reviewers.append(role)
        evidence = item.get("evidence", ())
        if isinstance(evidence, (list, tuple)):
            # Count only concrete, non-empty evidence entries.
            evidence_count += sum(
                1 for entry in evidence
                if isinstance(entry, str) and bool(entry.strip())
            )
        source_ids = item.get("source_ids", ())
        if isinstance(source_ids, (list, tuple)):
            for source_id in source_ids:
                if not isinstance(source_id, str):
                    continue
                value = source_id.strip()[:300]
                if value and value not in sources:
                    sources.append(value)
        try:
            uncertainty = float(item.get("uncertainty"))
        except (TypeError, ValueError):
            continue
        if isfinite(uncertainty) and 0.0 <= uncertainty <= 1.0:
            uncertainty_values.append(uncertainty)

    if not valid:
        outcome = "no_review_records"
    elif not sources and evidence_count == 0:
        outcome = "insufficient_evidence_leads"
    elif not sources:
        outcome = "evidence_leads_without_traceable_sources"
    else:
        # Recording a review is not the same as completing scientific validation.
        outcome = "provisional_review_recorded"

    levels = tuple(
        "high" if value >= 0.67 else "moderate" if value >= 0.34 else "lower"
        for value in uncertainty_values
    )
    questions = [
        "Have the full source documents been inspected, rather than bibliographic metadata alone?",
        "Do independent sources support or contradict each specific claim?",
        "Have methods, data quality, reproducibility and alternative explanations been assessed?",
        "Are safety, ethical, legal and accessibility implications resolved for the intended application?",
        "If reviewers disagree, what evidence would discriminate between their interpretations?",
    ]
    if not sources:
        questions.insert(0, "No traceable source identifiers were returned; can relevant primary sources be located and linked?")
    if evidence_count == 0:
        questions.insert(0, "No concrete evidence entries were recorded; what observations or source passages support each claim?")
    return ReviewSynthesis(
        review_count=len(valid),
        evidence_lead_count=evidence_count,
        source_ids=tuple(sources[:30]),
        reviewers=tuple(reviewers),
        uncertainty_levels=levels,
        outcome=outcome,
        unresolved_questions=tuple(questions),
    )

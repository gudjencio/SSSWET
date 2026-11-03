"""Explicit, auditable comparison of structured research claims.

This module deliberately avoids guessing whether two free-form paragraphs
contradict each other. Claims conflict only when they share a subject and
predicate but assert different normalized values. A detected conflict is a
review lead, not a scientific conclusion.
"""
from dataclasses import dataclass
import re


def _normalize(value: str) -> str:
    """Normalize case and all whitespace without changing scientific values."""
    return re.sub(r"\s+", " ", value.strip().casefold())


@dataclass(frozen=True)
class ResearchClaim:
    subject: str
    predicate: str
    value: str
    source_id: str
    statement: str = ""

    def __post_init__(self) -> None:
        for field_name in ("subject", "predicate", "value", "source_id"):
            field_value = getattr(self, field_name)
            if not isinstance(field_value, str) or not field_value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")


@dataclass(frozen=True)
class ClaimConflict:
    subject: str
    predicate: str
    values: tuple[str, ...]
    source_ids: tuple[str, ...] = ()
    explanation: str = ""


class ContradictionDetector:
    """Detect directly comparable claims with incompatible asserted values."""

    def compare(self, claims: list[ResearchClaim]) -> list[ClaimConflict]:
        buckets: dict[tuple[str, str], list[ResearchClaim]] = {}
        for claim in claims:
            key = (_normalize(claim.subject), _normalize(claim.predicate))
            buckets.setdefault(key, []).append(claim)

        conflicts: list[ClaimConflict] = []
        for (subject, predicate), group in buckets.items():
            values: dict[str, list[ResearchClaim]] = {}
            for claim in group:
                values.setdefault(_normalize(claim.value), []).append(claim)
            if len(values) < 2:
                continue
            source_ids = tuple(sorted({claim.source_id for claim in group}))
            if len(source_ids) < 2:
                continue
            display_values = tuple(sorted({claim.value.strip() for claim in group}, key=str.casefold))
            conflicts.append(ClaimConflict(
                subject=subject,
                predicate=predicate,
                values=display_values,
                source_ids=source_ids,
                explanation=(
                    "Distinct sources report different normalized values for "
                    "the same subject and predicate. Check units, conditions, "
                    "methods, dates, and source provenance before interpreting "
                    "this as a substantive contradiction."
                ),
            ))
        return sorted(conflicts, key=lambda item: (item.subject, item.predicate))

    def requires_third_review(self, claims: list[ResearchClaim]) -> bool:
        """Indicate whether a conflict merits independent review."""
        return bool(self.compare(claims))

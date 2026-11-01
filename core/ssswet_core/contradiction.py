"""Explicit, auditable comparison of structured research claims.

This module deliberately avoids guessing whether two free-form paragraphs
contradict each other. Claims conflict only when they share a subject and
predicate but assert different normalized values.
"""
from dataclasses import dataclass
import re


def _normalize(value: str) -> str:
    return re.sub(r"\\s+", " ", value.strip().casefold())


@dataclass(frozen=True)
class ResearchClaim:
    subject: str
    predicate: str
    value: str
    source_id: str
    statement: str = ""

    def __post_init__(self) -> None:
        for field_name in ("subject", "predicate", "value", "source_id"):
            if not getattr(self, field_name).strip():
                raise ValueError(f"{field_name} must not be empty")


@dataclass(frozen=True)
class ClaimConflict:
    subject: str
    predicate: str
    values: tuple[str, ...]
    source_ids: tuple[str, ...]
    explanation: str


class ContradictionDetector:
    """Detects directly comparable claims with incompatible asserted values."""

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
            # Repeated claims from one source do not create independent disagreement.
            source_ids = tuple(sorted({c.source_id for c in group}))
            if len(source_ids) < 2:
                continue
            display_values = tuple(sorted({c.value.strip() for c in group}, key=str.casefold))
            conflicts.append(ClaimConflict(
                subject=subject,
                predicate=predicate,
                values=display_values,
                source_ids=source_ids,
                explanation=(
                    "Independent sources assert different values for the same "
                    "subject and predicate; an additional review is required."
                ),
            ))
        return conflicts

    def requires_third_review(self, claims: list[ResearchClaim]) -> bool:
        return bool(self.compare(claims))

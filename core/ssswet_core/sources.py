"""Transparent source metadata and quality rubric.

A source score ranks research material for review; it is not a probability
that a claim is true and never upgrades a finding's verification state.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class SourceRecord:
    source_id: str
    title: str
    url: str = ""
    source_type: str = "unknown"
    peer_reviewed: bool = False
    primary_source: bool = False
    methods_available: bool = False
    publication_date_known: bool = False
    limitations: tuple[str, ...] = field(default_factory=tuple)
    retrieved_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self) -> None:
        if not self.source_id.strip():
            raise ValueError("source_id must not be empty")
        if not self.title.strip():
            raise ValueError("title must not be empty")


@dataclass(frozen=True)
class SourceAssessment:
    source_id: str
    score: float
    tier: str
    factors: tuple[str, ...]
    warning: str = (
        "Source quality is a review aid, not proof that any particular claim is true."
    )


class SourceQualityAssessor:
    """Applies a visible rubric without silently treating the score as truth."""

    def assess(self, source: SourceRecord) -> SourceAssessment:
        score = 0.0
        factors: list[str] = []

        if source.peer_reviewed:
            score += 0.25
            factors.append("peer_reviewed")
        if source.primary_source:
            score += 0.25
            factors.append("primary_source")
        if source.methods_available:
            score += 0.25
            factors.append("methods_available")
        if source.publication_date_known:
            score += 0.10
            factors.append("publication_date_known")
        if source.url.startswith("https://"):
            score += 0.05
            factors.append("https_url")
        if source.limitations:
            score -= min(0.20, 0.05 * len(source.limitations))
            factors.append("limitations_declared")

        score = max(0.0, min(1.0, score))
        tier = "high" if score >= 0.75 else "moderate" if score >= 0.45 else "limited"
        return SourceAssessment(
            source_id=source.source_id,
            score=round(score, 3),
            tier=tier,
            factors=tuple(factors),
        )

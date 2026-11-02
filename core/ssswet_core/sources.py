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
    doi: str = ""
    authors: tuple[str, ...] = field(default_factory=tuple)
    institutions: tuple[str, ...] = field(default_factory=tuple)
    dataset_ids: tuple[str, ...] = field(default_factory=tuple)
    related_source_ids: tuple[str, ...] = field(default_factory=tuple)
    provenance_group: str = ""

    def __post_init__(self) -> None:
        if not self.source_id.strip():
            raise ValueError("source_id must not be empty")
        if not self.title.strip():
            raise ValueError("title must not be empty")
        if self.doi and not self.doi.strip():
            raise ValueError("doi must be a non-empty string when provided")
        if len(set(self.dataset_ids)) != len(self.dataset_ids):
            raise ValueError("dataset_ids must not contain duplicates")
        if self.source_id in self.related_source_ids:
            raise ValueError("A source cannot be related to itself")


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


def analyze_source_independence(records: list[dict]) -> dict:
    """Compare declared source provenance without inferring independence from silence."""
    normalized = []
    seen = set()
    for record in records:
        source_id = str(record.get("source_id", "")).strip()
        if not source_id or source_id in seen:
            continue
        seen.add(source_id)
        normalized.append(record)

    pairs = []
    for index, left in enumerate(normalized):
        for right in normalized[index + 1:]:
            signals = []
            contextual = []
            left_doi = str(left.get("doi", "")).casefold().replace("https://doi.org/", "").strip()
            right_doi = str(right.get("doi", "")).casefold().replace("https://doi.org/", "").strip()
            if left_doi and left_doi == right_doi:
                signals.append("same_doi")
            if left.get("provenance_group") and left.get("provenance_group") == right.get("provenance_group"):
                signals.append("same_provenance_group")
            if set(left.get("dataset_ids", [])) & set(right.get("dataset_ids", [])):
                signals.append("shared_dataset")
            if (right["source_id"] in left.get("related_source_ids", [])
                    or left["source_id"] in right.get("related_source_ids", [])):
                signals.append("declared_related_source")
            if set(left.get("authors", [])) & set(right.get("authors", [])):
                contextual.append("shared_author")
            if set(left.get("institutions", [])) & set(right.get("institutions", [])):
                contextual.append("shared_institution")
            pairs.append({
                "source_ids": [left["source_id"], right["source_id"]],
                "dependency_signals": sorted(signals),
                "contextual_overlaps": sorted(contextual),
                "independence_status": (
                    "possible_dependency_requires_review" if signals
                    else "not_established"
                ),
            })
    return {
        "source_count": len(normalized),
        "pair_count": len(pairs),
        "pairs": pairs,
        "independent_source_count": None,
        "independence_established": False,
        "warning": (
            "Shared provenance signals warrant review; shared authors or institutions are contextual "
            "overlaps only. Absence of recorded overlap does not establish independence."
        ),
    }

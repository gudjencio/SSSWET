"""Context-aware comparison for explicitly structured research claims."""
from dataclasses import dataclass
from .contradiction import ResearchClaim, ClaimConflict


@dataclass(frozen=True)
class ClaimContext:
    claim: ResearchClaim
    scope: str = ""
    conditions: str = ""
    unit: str = ""
    observed_at: str = ""


class ContextAwareClaimComparator:
    """Avoid direct comparisons across declared scopes, conditions or units."""

    @staticmethod
    def _key(value: str) -> str:
        return " ".join(value.casefold().split())

    def compare(self, items: list[ClaimContext]) -> list[ClaimConflict]:
        groups = {}
        for item in items:
            claim = item.claim
            key = (
                self._key(claim.subject), self._key(claim.predicate),
                self._key(item.scope), self._key(item.conditions),
                self._key(item.unit),
            )
            groups.setdefault(key, []).append(item)
        results = []
        for key, group in groups.items():
            values = {}
            for item in group:
                values.setdefault(self._key(item.claim.value), []).append(item)
            if len(values) < 2:
                continue
            sources = tuple(sorted({item.claim.source_id for item in group}))
            if len(sources) < 2:
                continue
            dates = tuple(sorted({item.observed_at.strip() for item in group if item.observed_at.strip()}))
            complete_dates = all(item.observed_at.strip() for item in group)
            classification = "temporal_difference_needs_review" if complete_dates and len(dates) > 1 else "potential_conflict"
            display_values = tuple(sorted({item.claim.value.strip() for item in group}, key=str.casefold))
            results.append(ClaimConflict(
                subject=key[0], predicate=key[1], values=display_values,
                source_ids=sources,
                explanation="Different sources report different values in the same declared scope, conditions and unit. Inspect methods, uncertainty and provenance; no claim is selected as correct.",
                classification=classification, observed_at_values=dates,
            ))
        return sorted(results, key=lambda result: (result.subject, result.predicate, result.classification))

    @staticmethod
    def comparability_key(item: ClaimContext) -> tuple[str, str, str, str, str]:
        claim = item.claim
        return (
            " ".join(claim.subject.casefold().split()),
            " ".join(claim.predicate.casefold().split()),
            " ".join(item.scope.casefold().split()),
            " ".join(item.conditions.casefold().split()),
            " ".join(item.unit.casefold().split()),
        )

"""Context-aware comparison for explicitly structured research claims."""
from dataclasses import dataclass
from .contradiction import ResearchClaim

@dataclass(frozen=True)
class ClaimContext:
    claim: ResearchClaim
    scope: str = ""
    conditions: str = ""
    unit: str = ""
    observed_at: str = ""

@dataclass(frozen=True)
class ContextualConflict:
    subject: str
    predicate: str
    values: tuple[str, ...]
    source_ids: tuple[str, ...]
    explanation: str
    classification: str
    observed_at_values: tuple[str, ...]

class ContextAwareClaimComparator:
    """Compare claims only within matching declared contexts."""
    @staticmethod
    def _key(value: str) -> str:
        return " ".join(value.casefold().split())

    def compare(self, items: list[ClaimContext]) -> list[ContextualConflict]:
        groups = {}
        for item in items:
            claim = item.claim
            key = (self._key(claim.subject), self._key(claim.predicate), self._key(item.scope), self._key(item.conditions), self._key(item.unit))
            groups.setdefault(key, []).append(item)
        results = []
        for key, group in groups.items():
            values = {self._key(item.claim.value) for item in group}
            sources = tuple(sorted({item.claim.source_id for item in group}))
            if len(values) < 2 or len(sources) < 2:
                continue
            dates = tuple(sorted({item.observed_at.strip() for item in group if item.observed_at.strip()}))
            dated = all(item.observed_at.strip() for item in group)
            classification = "temporal_difference_needs_review" if dated and len(dates) > 1 else "potential_conflict"
            display_values = tuple(sorted({item.claim.value.strip() for item in group}, key=str.casefold))
            results.append(ContextualConflict(key[0], key[1], display_values, sources, "Different sources report different values in the same declared scope, conditions and unit. Inspect methods, uncertainty and provenance; no claim is selected as correct.", classification, dates))
        return sorted(results, key=lambda result: (result.subject, result.predicate, result.classification))

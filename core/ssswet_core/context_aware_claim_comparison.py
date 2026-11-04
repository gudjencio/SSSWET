"""Context-aware comparison for explicitly structured research claims."""
from dataclasses import asdict, dataclass
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
            key = (self._key(claim.subject), self._key(claim.predicate),
                   self._key(item.scope), self._key(item.conditions), self._key(item.unit))
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
            results.append(ContextualConflict(
                subject=group[0].claim.subject, predicate=group[0].claim.predicate,
                values=display_values, source_ids=sources,
                explanation="Claims share declared scope, conditions and units but assert different values.",
                classification=classification, observed_at_values=dates,
            ))
        return results

    def audit_contexts(self, items: list[ClaimContext]) -> dict:
        """Return comparable conflicts and separately identify context mismatches."""
        groups = {}
        for item in items:
            base = (self._key(item.claim.subject), self._key(item.claim.predicate))
            context = (self._key(item.scope), self._key(item.conditions), self._key(item.unit))
            groups.setdefault(base, {}).setdefault(context, []).append(item)
        separated = []
        for (subject, predicate), contexts in sorted(groups.items()):
            if len(contexts) < 2:
                continue
            context_rows = []
            for context, claims in sorted(contexts.items()):
                context_rows.append({
                    "scope": claims[0].scope, "conditions": claims[0].conditions, "unit": claims[0].unit,
                    "values": sorted({item.claim.value for item in claims}, key=str.casefold),
                    "source_ids": sorted({item.claim.source_id for item in claims}),
                })
            first_claim = next(iter(contexts.values()))[0].claim
            separated.append({
                "subject": first_claim.subject, "predicate": first_claim.predicate,
                "classification": "context_mismatch_not_compared", "contexts": context_rows,
                "automatic_adjudication": False,
            })
        return {
            "conflicts": [asdict(item) for item in self.compare(items)],
            "context_mismatches": separated, "claim_count": len(items),
            "claims_compared_only_within_matching_contexts": True,
            "scientific_validity_established": False, "automatic_adjudication": False,
        }

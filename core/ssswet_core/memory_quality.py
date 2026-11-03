from collections import Counter
from dataclasses import asdict
from .models import Finding
from .memory import MemoryItem


def deduplicate_memories(items: list[MemoryItem]) -> list[MemoryItem]:
    """Keep the newest item for each normalized statement while preserving validation."""
    chosen: dict[str, MemoryItem] = {}
    for item in items:
        key = " ".join(item.statement.casefold().split())
        current = chosen.get(key)
        if current is None or item.created_at >= current.created_at or (item.validated and not current.validated):
            chosen[key] = item
    return list(chosen.values())


def retrieval_quality(query: str, results: list[MemoryItem]) -> dict:
    q = {token for token in query.casefold().split() if token}
    hits = [r for r in results if q & set(r.statement.casefold().split())]
    validated = sum(r.validated for r in hits)
    return {
        "query_tokens": len(q),
        "result_count": len(results),
        "lexical_hit_count": len(hits),
        "validated_hit_count": validated,
        "validated_hit_rate": validated / len(hits) if hits else 0.0,
    }


def finding_evidence_coverage(finding: Finding) -> dict:
    sources = finding.metadata.get("independent_sources", [])
    groups = finding.metadata.get("independence_groups", {})
    distinct_groups = {groups[s] for s in sources if groups.get(s)}
    return {
        "evidence_count": len(finding.evidence),
        "source_count": len(sources),
        "distinct_provenance_groups": len(distinct_groups),
        "independent_threshold_met": len(distinct_groups) >= 2,
    }

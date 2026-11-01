"""Traceable, conservative retrieval for the shared research memory."""
from __future__ import annotations

import re
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Iterable


MEMORY_STATES = {"candidate", "reviewed", "rejected", "superseded"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _tokens(value: str) -> set[str]:
    return {
        token.casefold()
        for token in re.findall(r"[\w'-]{2,}", value, flags=re.UNICODE)
    }


@dataclass(frozen=True)
class CollectiveMemoryRecord:
    memory_id: str
    topic: str
    statement: str
    campaign_id: str = ""
    status: str = "candidate"
    source_ids: tuple[str, ...] = ()
    provenance_group: str = ""
    confidence: float = 0.0
    review_note: str = ""
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self) -> None:
        if not self.memory_id.strip():
            raise ValueError("A memory ID is required")
        if not self.topic.strip() or not self.statement.strip():
            raise ValueError("Memory topic and statement are required")
        if self.status not in MEMORY_STATES:
            raise ValueError(f"Unsupported memory state: {self.status}")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("Memory confidence must be between 0 and 1")
        if len(set(self.source_ids)) != len(self.source_ids):
            raise ValueError("Memory source IDs must be unique")

    @classmethod
    def create(
        cls, memory_id: str, topic: str, statement: str, *,
        campaign_id: str = "", source_ids: Iterable[str] = (),
        provenance_group: str = "", confidence: float = 0.0,
    ) -> "CollectiveMemoryRecord":
        timestamp = _now()
        return cls(
            memory_id=memory_id, topic=topic, statement=statement,
            campaign_id=campaign_id, source_ids=tuple(source_ids),
            provenance_group=provenance_group, confidence=confidence,
            created_at=timestamp, updated_at=timestamp,
        )


def review_memory(
    record: CollectiveMemoryRecord, status: str, note: str,
) -> CollectiveMemoryRecord:
    """Record an explicit human review decision; never infer scientific truth."""
    if status not in {"reviewed", "rejected", "superseded", "candidate"}:
        raise ValueError("Unsupported review decision")
    if not isinstance(note, str) or not note.strip():
        raise ValueError("A review note is required")
    return replace(
        record, status=status, review_note=note.strip(), updated_at=_now()
    )


def search_collective_memory(
    records: Iterable[dict], query: str, *, limit: int = 20,
    include_rejected: bool = True,
) -> list[dict]:
    """Rank stored records by transparent lexical overlap, not semantic truth."""
    query_tokens = _tokens(query)
    if not query_tokens:
        return []
    ranked = []
    for record in records:
        if not include_rejected and record.get("status") == "rejected":
            continue
        searchable = " ".join((
            str(record.get("topic", "")),
            str(record.get("statement", "")),
            str(record.get("campaign_id", "")),
            " ".join(record.get("source_ids", [])),
        ))
        record_tokens = _tokens(searchable)
        overlap = query_tokens & record_tokens
        if not overlap:
            continue
        coverage = len(overlap) / len(query_tokens)
        precision = len(overlap) / len(record_tokens) if record_tokens else 0.0
        score = round((0.7 * coverage) + (0.3 * precision), 4)
        ranked.append({
            **record,
            "retrieval_score": score,
            "matched_terms": sorted(overlap),
            "retrieval_method": "lexical_overlap",
            "scientific_validity_established": False,
        })
    ranked.sort(
        key=lambda item: (
            item["retrieval_score"],
            item.get("updated_at", ""),
            item.get("memory_id", ""),
        ),
        reverse=True,
    )
    return ranked[:max(1, min(int(limit), 100))]

"""Traceable shared research memory with field-aware lexical retrieval."""
from __future__ import annotations
import math
import re
from collections import Counter
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Iterable

MEMORY_STATES = {"candidate", "reviewed", "rejected", "superseded"}

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _tokens(value: str) -> list[str]:
    return [token.casefold() for token in re.findall(r"[\w'-]{2,}", value, flags=re.UNICODE)]

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
        if not isinstance(self.memory_id, str) or not self.memory_id.strip():
            raise ValueError("A memory ID is required")
        if not isinstance(self.topic, str) or not self.topic.strip():
            raise ValueError("Memory topic and statement are required")
        if not isinstance(self.statement, str) or not self.statement.strip():
            raise ValueError("Memory topic and statement are required")
        if self.status not in MEMORY_STATES:
            raise ValueError(f"Unsupported memory state: {self.status}")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("Memory confidence must be between 0 and 1")
        if len(set(self.source_ids)) != len(self.source_ids):
            raise ValueError("Memory source IDs must be unique")
        if any(not isinstance(item, str) or not item.strip() for item in self.source_ids):
            raise ValueError("Memory source IDs must be non-empty strings")

    @classmethod
    def create(cls, memory_id: str, topic: str, statement: str, *, campaign_id: str = "",
               source_ids: Iterable[str] = (), provenance_group: str = "", confidence: float = 0.0):
        timestamp = _now()
        return cls(memory_id=memory_id, topic=topic, statement=statement, campaign_id=campaign_id,
                   source_ids=tuple(source_ids), provenance_group=provenance_group,
                   confidence=confidence, created_at=timestamp, updated_at=timestamp)

def review_memory(record: CollectiveMemoryRecord, status: str, note: str) -> CollectiveMemoryRecord:
    """Record an explicit human review decision; never infer scientific truth."""
    if status not in {"reviewed", "rejected", "superseded", "candidate"}:
        raise ValueError("Unsupported review decision")
    if not isinstance(note, str) or not note.strip():
        raise ValueError("A review note is required")
    return replace(record, status=status, review_note=note.strip(), updated_at=_now())

def search_collective_memory(records: Iterable[dict], query: str, *, limit: int = 20,
                             include_rejected: bool = True, campaign_id: str | None = None,
                             provenance_group: str | None = None, source_id: str | None = None,
                             statuses: Iterable[str] | None = None) -> list[dict]:
    """Rank research text with weighted BM25; identifiers are exact filters, not prose.

    Topic terms receive more weight than statement terms. Opaque source IDs and
    campaign identifiers are deliberately excluded from lexical scoring so
    accidental token overlap cannot outrank evidence-bearing text.
    """
    if not isinstance(query, str):
        raise TypeError("query must be text")
    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
        raise ValueError("limit must be a positive integer")
    query_tokens = sorted(set(_tokens(query)))
    if not query_tokens:
        return []
    if statuses is not None and isinstance(statuses, (str, bytes)):
        raise TypeError("statuses must be a collection of workflow states")
    status_filter = set(statuses) if statuses is not None else None
    if status_filter is not None and not status_filter.issubset(MEMORY_STATES):
        raise ValueError("statuses contains an unsupported memory state")
    candidates = []
    for record in records:
        if not include_rejected and record.get("status") == "rejected":
            continue
        if status_filter is not None and record.get("status") not in status_filter:
            continue
        if campaign_id is not None and record.get("campaign_id") != campaign_id:
            continue
        if provenance_group is not None and record.get("provenance_group") != provenance_group:
            continue
        record_sources = record.get("source_ids", []) or []
        if isinstance(record_sources, str):
            record_sources = [record_sources]
        if source_id is not None and source_id not in record_sources:
            continue
        topic_tokens = _tokens(str(record.get("topic", "")))
        statement_tokens = _tokens(str(record.get("statement", "")))
        frequencies = Counter(topic_tokens)
        frequencies.update(statement_tokens)
        document_tokens = set(frequencies)
        if not document_tokens.intersection(query_tokens):
            continue
        candidates.append((record, topic_tokens, statement_tokens, frequencies, document_tokens))
    if not candidates:
        return []
    document_frequency = Counter()
    for _, _, _, _, terms in candidates:
        document_frequency.update(terms.intersection(query_tokens))
    average_length = sum(len(topic) + len(statement) for _, topic, statement, _, _ in candidates) / len(candidates)
    average_length = max(1.0, average_length)
    ranked = []
    for record, topic, statement, frequencies, document_tokens in candidates:
        document_length = max(1, len(topic) + len(statement))
        score = 0.0
        for term in query_tokens:
            tf = 2.0 * topic.count(term) + statement.count(term)
            if tf <= 0:
                continue
            df = document_frequency[term]
            idf = math.log(1.0 + (len(candidates) - df + 0.5) / (df + 0.5))
            denominator = tf + 1.2 * (0.25 + 0.75 * document_length / average_length)
            score += idf * (tf * 2.2) / denominator
        matched = sorted(document_tokens.intersection(query_tokens))
        normalized_query = " ".join(query_tokens)
        normalized_text = " ".join((str(record.get("topic", "")) + " " + str(record.get("statement", ""))).casefold().split())
        if normalized_query and normalized_query in normalized_text:
            score += 0.35
        ranked.append({
            **record, "retrieval_score": round(score, 6),
            "query_coverage": round(len(matched) / len(query_tokens), 4),
            "matched_terms": matched, "retrieval_method": "field_weighted_bm25",
            "retrieval_version": "bm25-field-weighted-v2",
            "scientific_validity_established": False,
        })
    ranked.sort(key=lambda item: (item["retrieval_score"], item["query_coverage"],
                                  item.get("updated_at", ""), item.get("memory_id", "")), reverse=True)
    return ranked[:min(limit, 100)]

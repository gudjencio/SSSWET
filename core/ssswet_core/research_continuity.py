"""Persistent research-continuity workflows over the SQLite collective memory."""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from .continuity_tools import (
    build_agent_handoff,
    build_memory_snapshot,
    candidate_memory_conflicts,
    compare_temporal_observations,
    group_exact_memory_duplicates,
    query_temporal_window,
    search_memory_records,
    temporal_coverage_gaps,
    validate_memory_snapshot,
)


class ResearchContinuityService:
    """Connect bounded continuity tools to the project's persistent research store.

    The service reads existing collective-memory records and never upgrades their
    review status. Timeline operations accept explicitly supplied observations.
    """

    def __init__(self, store: Any) -> None:
        if store is None or not callable(getattr(store, "collective_memory_items", None)):
            raise TypeError("a compatible persistent research store is required")
        self.store = store

    def records(self, *, campaign_id: str | None = None, limit: int = 500) -> list[dict]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 500:
            raise ValueError("limit must be between 1 and 500")
        return self.store.collective_memory_items(campaign_id=campaign_id, limit=limit)

    def search(self, query: str, *, campaign_id: str | None = None,
               statuses: Iterable[str] | None = None, limit: int = 20) -> list[dict]:
        return search_memory_records(
            self.records(), query, campaign_id=campaign_id,
            statuses=tuple(statuses) if statuses is not None else None, limit=limit,
        )

    def handoff(self, query: str, *, campaign_id: str | None = None,
                max_records: int = 8, max_chars: int = 24000) -> dict:
        return build_agent_handoff(
            self.records(), query, campaign_id=campaign_id,
            max_records=max_records, max_chars=max_chars,
        )

    def duplicate_groups(self, *, campaign_id: str | None = None) -> list[dict]:
        return group_exact_memory_duplicates(self.records(campaign_id=campaign_id))

    def conflict_candidates(self, *, campaign_id: str | None = None) -> list[dict]:
        return candidate_memory_conflicts(self.records(campaign_id=campaign_id))

    def snapshot(self, *, campaign_id: str | None = None) -> dict:
        return build_memory_snapshot(self.records(campaign_id=campaign_id))

    @staticmethod
    def validate_snapshot(snapshot: Mapping) -> dict:
        return validate_memory_snapshot(snapshot)

    @staticmethod
    def temporal_window(observations: Iterable[Mapping], **filters) -> list[dict]:
        return query_temporal_window(observations, **filters)

    @staticmethod
    def coverage_gaps(observations: Iterable[Mapping], **window) -> list[dict]:
        return temporal_coverage_gaps(observations, **window)

    @staticmethod
    def compare_timelines(left: Iterable[Mapping], right: Iterable[Mapping]) -> list[dict]:
        return compare_temporal_observations(left, right)

    def overview(self, *, campaign_id: str | None = None) -> dict:
        records = self.records(campaign_id=campaign_id)
        duplicates = group_exact_memory_duplicates(records)
        conflicts = candidate_memory_conflicts(records)
        snapshot = build_memory_snapshot(records)
        return {
            "record_count": len(records),
            "campaign_id": campaign_id,
            "status_counts": {
                status: sum(1 for item in records if item.get("status") == status)
                for status in sorted({str(item.get("status", "candidate")) for item in records})
            },
            "duplicate_group_count": len(duplicates),
            "potential_conflict_count": len(conflicts),
            "snapshot": {
                "schema_version": snapshot["schema_version"],
                "record_count": snapshot["record_count"],
                "sha256": snapshot["sha256"],
            },
            "scientific_validity_established": False,
            "conflicts_require_human_review": True,
        }

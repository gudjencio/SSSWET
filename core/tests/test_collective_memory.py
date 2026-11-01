import pytest

from ssswet_core.collective_memory import (
    CollectiveMemoryRecord,
    review_memory,
    search_collective_memory,
)
from ssswet_core.persistence import SQLiteResearchStore


def test_collective_memory_round_trip_preserves_provenance_and_state(tmp_path):
    store = SQLiteResearchStore(tmp_path / "collective.sqlite3")
    record = CollectiveMemoryRecord.create(
        "memory-1", "wave propagation",
        "A candidate method estimates wave speed from repeated observations",
        campaign_id="campaign-1", source_ids=("paper-1", "dataset-1"),
        provenance_group="lab-a", confidence=0.35,
    )
    store.save_collective_memory(record)
    saved = store.collective_memory_items()[0]

    assert saved["memory_id"] == "memory-1"
    assert saved["source_ids"] == ["paper-1", "dataset-1"]
    assert saved["status"] == "candidate"
    assert saved["confidence"] == 0.35


def test_memory_search_ranks_overlap_and_labels_lexical_method(tmp_path):
    store = SQLiteResearchStore(tmp_path / "search.sqlite3")
    store.save_collective_memory(CollectiveMemoryRecord.create(
        "memory-wave", "wave propagation",
        "Compare methods for measuring wave speed",
    ))
    store.save_collective_memory(CollectiveMemoryRecord.create(
        "memory-orbit", "orbital mechanics",
        "Review satellite trajectory estimates",
    ))

    matches = search_collective_memory(
        store.collective_memory_items(), "wave speed measurement"
    )

    assert matches[0]["memory_id"] == "memory-wave"
    assert matches[0]["retrieval_method"] == "lexical_overlap"
    assert matches[0]["scientific_validity_established"] is False


def test_memory_review_requires_a_note_and_keeps_explicit_status():
    record = CollectiveMemoryRecord.create("m", "topic", "candidate statement")
    with pytest.raises(ValueError, match="review note"):
        review_memory(record, "reviewed", "  ")

    reviewed = review_memory(record, "reviewed", "Sources checked; further testing needed")
    assert reviewed.status == "reviewed"
    assert reviewed.review_note == "Sources checked; further testing needed"
    assert reviewed.confidence == record.confidence


def test_rejected_memory_remains_retrievable_but_can_be_filtered():
    record = CollectiveMemoryRecord.create("m", "wave method", "Old wave method")
    rejected = review_memory(record, "rejected", "Method contradicted by later evidence")
    records = [rejected.__dict__]

    assert search_collective_memory(records, "wave method")
    assert search_collective_memory(
        records, "wave method", include_rejected=False
    ) == []


def test_memory_rejects_invalid_state_and_duplicate_sources():
    with pytest.raises(ValueError, match="Unsupported memory state"):
        CollectiveMemoryRecord("m", "topic", "statement", status="verified")
    with pytest.raises(ValueError, match="unique"):
        CollectiveMemoryRecord(
            "m2", "topic", "statement", source_ids=("paper", "paper")
        )

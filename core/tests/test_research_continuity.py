from __future__ import annotations

from types import SimpleNamespace

import pytest

from ssswet_core.research_continuity import ResearchContinuityService


class MemoryStore:
    def __init__(self, records):
        self._records = records

    def collective_memory_items(self, *, status=None, campaign_id=None, limit=200):
        records = self._records
        if status:
            records = [item for item in records if item["status"] == status]
        if campaign_id:
            records = [item for item in records if item["campaign_id"] == campaign_id]
        return [dict(item) for item in records[:limit]]


@pytest.fixture
def service():
    records = [
        {"memory_id":"m1","campaign_id":"c1","topic":"Thermal coating",
         "statement":"The coating is strong after cycling",
         "status":"reviewed","source_ids":["lab-a"],"provenance_group":"lab-a",
         "confidence":0.7,"review_note":"","created_at":"2026-01-01","updated_at":"2026-01-01"},
        {"memory_id":"m2","campaign_id":"c1","topic":"Thermal coating",
         "statement":"The coating is not strong after cycling",
         "status":"candidate","source_ids":["lab-b"],"provenance_group":"lab-b",
         "confidence":0.4,"review_note":"","created_at":"2026-01-02","updated_at":"2026-01-02"},
        {"memory_id":"m3","campaign_id":"c2","topic":"Battery",
         "statement":"Capacity measured at room temperature",
         "status":"rejected","source_ids":["lab-c"],"provenance_group":"lab-c",
         "confidence":0.1,"review_note":"","created_at":"2026-01-03","updated_at":"2026-01-03"},
    ]
    return ResearchContinuityService(MemoryStore(records))


def test_01_service_requires_persistent_store():
    with pytest.raises(TypeError):
        ResearchContinuityService(None)


def test_02_records_are_campaign_scoped_and_bounded(service):
    assert [x["memory_id"] for x in service.records(campaign_id="c1")] == ["m1", "m2"]
    with pytest.raises(ValueError):
        service.records(limit=0)


def test_03_search_uses_persistent_records_and_keeps_review_state(service):
    found = service.search("thermal coating", campaign_id="c1")
    assert found[0]["memory_id"] == "m1"
    assert found[0]["status"] == "reviewed"
    assert found[0]["scientific_validity_established"] is False


def test_04_handoff_preserves_sources_and_requires_review(service):
    packet = service.handoff("thermal coating", campaign_id="c1", max_records=1)
    assert packet["records"][0]["memory_id"] == "m1"
    assert packet["source_ids"] == ["lab-a"]
    assert packet["human_review_required"] is True


def test_05_duplicate_review_is_non_destructive(service):
    assert service.duplicate_groups() == []
    assert len(service.records()) == 3


def test_06_conflict_candidates_are_not_adjudications(service):
    result = service.conflict_candidates(campaign_id="c1")
    assert len(result) == 1
    assert result[0]["requires_human_review"] is True
    assert result[0]["scientific_contradiction_established"] is False


def test_07_snapshot_is_verifiable_and_scoped(service):
    snapshot = service.snapshot(campaign_id="c1")
    assert service.validate_snapshot(snapshot)["valid"] is True
    assert snapshot["record_count"] == 2


def test_08_temporal_window_uses_explicit_observations(service):
    result = service.temporal_window([
        {"timestamp":"2026-01-01T00:00:00Z","source_id":"a"},
        {"timestamp":"2026-01-03T00:00:00Z","source_id":"b"},
    ], start="2026-01-02", end="2026-01-04")
    assert [x["source_id"] for x in result] == ["b"]


def test_09_coverage_gaps_do_not_claim_event_absence(service):
    gaps = service.coverage_gaps(
        [{"timestamp":"2026-01-01T00:00:00Z"}],
        start="2026-01-01", end="2026-01-01T00:00:02Z",
        cadence_seconds=1,
    )
    assert len(gaps) == 2
    assert all(item["absence_of_event_established"] is False for item in gaps)


def test_10_timeline_comparison_retains_uncertainty(service):
    result = service.compare_timelines(
        [{"source_id":"sensor-1","timestamp":"2026-01-01T00:00:00Z","uncertainty_seconds":2}],
        [{"source_id":"sensor-1","timestamp":"2026-01-01T00:00:05Z","uncertainty_seconds":2}],
    )
    assert result[0]["delta_seconds"] == 5
    assert result[0]["combined_uncertainty_seconds"] == 4
    assert result[0]["difference_exceeds_combined_uncertainty"] is True


def test_11_overview_exposes_integrity_metadata_not_scientific_truth(service):
    report = service.overview(campaign_id="c1")
    assert report["record_count"] == 2
    assert report["potential_conflict_count"] == 1
    assert report["scientific_validity_established"] is False
    assert len(report["snapshot"]["sha256"]) == 64

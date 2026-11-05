import copy
import pytest

from ssswet_core.continuity_tools import (
    build_agent_handoff, build_memory_snapshot, candidate_memory_conflicts,
    compare_temporal_observations, group_exact_memory_duplicates,
    normalize_memory_query, parse_temporal_instant, query_temporal_window,
    search_memory_records, temporal_coverage_gaps, validate_memory_snapshot,
)


def sample_records():
    return [
        {"memory_id": "m1", "topic": "Wave speed", "statement": "The method supports wave speed measurement",
         "campaign_id": "c1", "status": "reviewed", "source_ids": ["p1"],
         "provenance_group": "lab-a", "confidence": 0.7, "updated_at": "2026-01-01"},
        {"memory_id": "m2", "topic": "wave speed", "statement": "The method does not support wave speed measurement",
         "campaign_id": "c1", "status": "candidate", "source_ids": ["p2"],
         "provenance_group": "lab-b", "confidence": 0.2},
        {"memory_id": "m3", "topic": "Orbital motion", "statement": "Estimate satellite trajectory",
         "campaign_id": "c2", "status": "rejected", "source_ids": ["p3"],
         "provenance_group": "lab-c"},
    ]


def test_01_unicode_normalization_is_stable():
    assert normalize_memory_query("  ＷＡＶＥ   Speed ") == ("wave", "speed")
    assert normalize_memory_query("CAFÉ café") == ("café",)


def test_02_weighted_search_filters_and_caps_results():
    records = sample_records()
    result = search_memory_records(records, "wave speed", campaign_id="c1",
                                   statuses=["reviewed"], limit=999)
    assert [item["memory_id"] for item in result] == ["m1"]
    assert result[0]["retrieval_method"] == "weighted_lexical_v1"
    assert result[0]["scientific_validity_established"] is False
    assert search_memory_records(records, "trajectory") == []


def test_03_exact_duplicates_are_grouped_without_mutation():
    records = [
        {"memory_id": "b", "topic": "WAVE", "statement": "A result", "source_ids": ["s2"]},
        {"memory_id": "a", "topic": " wave ", "statement": "a RESULT", "source_ids": ["s1"]},
    ]
    before = copy.deepcopy(records)
    groups = group_exact_memory_duplicates(records)
    assert groups[0]["memory_ids"] == ["a", "b"]
    assert groups[0]["source_ids"] == ["s1", "s2"]
    assert groups[0]["merge_performed"] is False
    assert records == before


def test_04_opposite_polarity_is_flagged_not_decided():
    conflicts = candidate_memory_conflicts(sample_records())
    assert conflicts[0]["memory_ids"] == ["m1", "m2"]
    assert conflicts[0]["requires_human_review"] is True
    assert conflicts[0]["scientific_contradiction_established"] is False


def test_05_snapshot_is_versioned_deterministic_and_checksummed():
    records = sample_records()[:2]
    a = build_memory_snapshot(records, created_at="2026-01-01T00:00:00Z")
    b = build_memory_snapshot(reversed(records), created_at="2026-01-01T00:00:00Z")
    assert a == b
    assert validate_memory_snapshot(a)["valid"] is True
    altered = copy.deepcopy(a)
    altered["records"][0]["statement"] += " altered"
    with pytest.raises(ValueError, match="checksum"):
        validate_memory_snapshot(altered)


def test_06_snapshot_rejects_duplicate_ids_and_bad_counts():
    with pytest.raises(ValueError, match="unique"):
        build_memory_snapshot([{"memory_id": "x"}, {"memory_id": "x"}])
    snapshot = build_memory_snapshot([{"memory_id": "x"}], created_at="fixed")
    snapshot["record_count"] = 2
    with pytest.raises(ValueError, match="record_count"):
        validate_memory_snapshot(snapshot)


def test_07_agent_handoff_is_bounded_and_preserves_provenance():
    packet = build_agent_handoff(sample_records(), "wave speed", campaign_id="c1",
                                 max_records=1, max_chars=1000)
    assert len(packet["records"]) == 1
    assert packet["source_ids"] == ["p1"]
    assert packet["human_review_required"] is True
    assert "Treat retrieved statements as claims" in packet["constraints"][0]
    assert packet["truncated"] is True
    assert packet["character_count"] <= 24000


def test_08_temporal_parser_normalizes_offsets_and_rejects_naive_datetimes():
    parsed = parse_temporal_instant("2026-01-01T01:00:00+01:00")
    assert parsed["utc"].isoformat() == "2026-01-01T00:00:00+00:00"
    assert parse_temporal_instant("2026-01-01")["precision"] == "date"
    with pytest.raises(ValueError, match="timezone"):
        parse_temporal_instant("2026-01-01T01:00:00")


def test_09_temporal_window_is_inclusive_sorted_and_uncertainty_aware():
    records = [
        {"timestamp": "2026-01-02T00:00:00Z", "source_id": "b", "uncertainty_seconds": 2},
        {"timestamp": "2026-01-01T00:00:00Z", "source_id": "a", "uncertainty_seconds": 1},
    ]
    result = query_temporal_window(records, start="2026-01-01", end="2026-01-02",
                                   max_uncertainty_seconds=1)
    assert [item["source_id"] for item in result] == ["a"]


def test_10_temporal_coverage_gaps_are_bounded_and_do_not_claim_absence():
    records = [{"timestamp": "2026-01-01T00:00:00Z"}]
    gaps = temporal_coverage_gaps(records, start="2026-01-01T00:00:00Z",
                                  end="2026-01-01T00:00:30Z",
                                  cadence_seconds=10, tolerance_seconds=1)
    assert len(gaps) == 3
    assert gaps[0]["status"] == "no_nearby_recorded_observation"
    assert gaps[0]["absence_of_event_established"] is False
    assert len(temporal_coverage_gaps([], start="2026-01-01", end="2026-01-10",
                                      cadence_seconds=1, max_gaps=3)) == 3


def test_temporal_comparison_reports_delta_and_uncertainty_without_causal_claim():
    left = [{"source_id": "s1", "timestamp": "2026-01-01T00:00:00Z",
             "uncertainty_seconds": 2}]
    right = [{"source_id": "s1", "timestamp": "2026-01-01T00:00:05Z",
              "uncertainty_seconds": 1}]
    result = compare_temporal_observations(left, right)
    assert result[0]["delta_seconds"] == 5
    assert result[0]["combined_uncertainty_seconds"] == 3
    assert result[0]["difference_exceeds_combined_uncertainty"] is True
    assert "cause is not inferred" in result[0]["interpretation"]

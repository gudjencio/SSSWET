from ssswet_core.memory_compaction import compact


def test_compaction_merges_provenance_and_keeps_newest_validated_record():
    records = [
        {"memory_id": "m1", "statement": "A claim", "validated": False,
         "updated_at": "2026-01-01", "source_ids": ["s1"],
         "experiment_ids": ["e1"], "status": "candidate"},
        {"memory_id": "m2", "statement": " a   claim ", "validated": True,
         "updated_at": "2026-01-02", "source_ids": ["s2", "s1"],
         "graph_node_ids": ["g1"], "status": "reviewed"},
    ]
    result = compact(records)
    assert result["retained_count"] == 1
    item = result["records"][0]
    assert item["memory_id"] == "m2"
    assert item["validated"] is True
    assert item["source_ids"] == ["s1", "s2"]
    assert item["experiment_ids"] == ["e1"]
    assert item["graph_node_ids"] == ["g1"]
    assert item["merged_memory_ids"] == ["m1", "m2"]
    assert item["review_states"] == ["candidate", "reviewed"]
    assert result["unbounded_growth"] is False


def test_compaction_preserves_all_unique_provenance_without_unbounded_records():
    records = [
        {"memory_id": f"m{i}", "statement": "same", "source_ids": [f"s{i}"]}
        for i in range(1500)
    ]
    result = compact(records, max_records=10)
    assert result["input_count"] == 1500
    assert result["retained_count"] == 1
    assert len(result["records"][0]["source_ids"]) == 1500
    assert result["dropped_count"] == 0


def test_compaction_rejects_malformed_provenance_and_records():
    import pytest
    with pytest.raises(ValueError, match="dictionary"):
        compact([None])
    with pytest.raises(ValueError, match="source_ids"):
        compact([{"statement": "claim", "source_ids": "not-a-list"}])
    with pytest.raises(ValueError, match="positive"):
        compact([], max_records=0)

from ssswet_core.bounded_retention import RetentionPolicy, compact_records


def test_retention_deduplicates_and_bounds_storage():
    records = [{"key": "a", "v": 1}, {"key": "b", "v": 1}, {"key": "a", "v": 2}]
    result = compact_records(records, policy=RetentionPolicy(max_items=2))
    assert result == [{"key": "b", "v": 1}, {"key": "a", "v": 2}]

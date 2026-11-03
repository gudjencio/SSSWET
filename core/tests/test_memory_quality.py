from ssswet_core.memory import MemoryItem
from ssswet_core.memory_quality import deduplicate_memories, retrieval_quality


def test_deduplication_prefers_validated_item():
    a = MemoryItem("a", "Fusion storage", "s1", False, "2026-01-01T00:00:00+00:00")
    b = MemoryItem("b", "Fusion storage", "s2", True, "2026-01-02T00:00:00+00:00")
    result = deduplicate_memories([a, b])
    assert len(result) == 1 and result[0].validated


def test_retrieval_quality_reports_validation_rate():
    items = [MemoryItem("a", "fusion storage", "s1", True), MemoryItem("b", "fusion grid", "s2", False)]
    metrics = retrieval_quality("fusion", items)
    assert metrics["lexical_hit_count"] == 2
    assert metrics["validated_hit_rate"] == 0.5

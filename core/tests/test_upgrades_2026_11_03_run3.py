from ssswet_core.unit_normalization import convert
from ssswet_core.sensitivity_analysis import one_at_a_time
from ssswet_core.data_quality import profile
from ssswet_core.safety_gate import assess
from ssswet_core.provenance_graph import build
from ssswet_core.experiment_design import grid
from ssswet_core.result_cache import ResultCache
from ssswet_core.localization_fallback import resolve
from ssswet_core.validation_report import summarize
from ssswet_core.schema_versioning import check


def test_units_are_deterministic():
    assert convert(100, "cm", "m") == 1.0


def test_sensitivity_is_bounded_and_repeatable():
    result = one_at_a_time({"x": 2}, {"x": 2}, lambda p: p["x"] * 3)
    assert result[0]["delta"] > 0


def test_data_quality_counts_duplicates_and_missing():
    report = profile([{"id": "a", "x": 1}, {"id": "a", "x": None}], ("x",))
    assert report["duplicate_ids"] == 1
    assert report["missing"]["x"] == 1


def test_safety_gate_blocks_sensitive_work_without_approval():
    assert not assess(["human_subjects"])["allowed_to_proceed"]
    assert assess(["human_subjects"], human_approval=True)["allowed_to_proceed"]


def test_provenance_discards_invalid_edges_and_finds_roots():
    report = build([{"id": "a"}, {"id": "b"}], [("a", "b"), ("x", "b")])
    assert report["roots"] == ["a"]
    assert report["invalid_edge_count"] == 1


def test_experiment_grid_has_hard_run_bound():
    assert len(grid({"a": [1, 2], "b": [1, 2]}, max_runs=3)) == 3


def test_cache_never_exceeds_bound():
    cache = ResultCache(max_entries=2)
    cache.put({"x": 1}, "a")
    cache.put({"x": 2}, "b")
    cache.put({"x": 3}, "c")
    assert cache.stats()["entries"] == 2


def test_localization_fallback_is_explicit():
    result = resolve("fr-CA", ["en", "fr"])
    assert result["selected"] == "fr"
    assert not result["translation_invented"]


def test_validation_summary_is_not_truth_claim():
    result = summarize([{"passed": True}, {"passed": False}])
    assert result["pass_ratio"] == 0.5
    assert not result["scientific_truth_established"]


def test_schema_versioning_rejects_missing_fields():
    assert not check({"schema_version": 1}, 1, ("id",))["compatible"]

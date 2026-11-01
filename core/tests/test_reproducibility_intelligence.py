import hashlib
import json

import pytest

from ssswet_core.reproducibility_intelligence import ReproducibilityIntelligence


def _run(run_id, campaign, provenance, source_ids=(), dataset_ids=()):
    item = {
        "run_id": run_id, "protocol_id": "protocol-a", "protocol_version": 1,
        "campaign_id": campaign, "kind": "simulation", "parameters": {"seed": 1},
        "outputs": {"value": 42}, "method": "fixed method", "environment": {"python": "3"},
        "code_or_model_reference": "model@v1", "provenance_group": provenance,
        "independence_declared": True, "limitations": [], "recorded_at": "2026-01-01T00:00:00+00:00",
        "source_ids": list(source_ids), "dataset_ids": list(dataset_ids), "record_hash": "",
    }
    canonical = json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    item["record_hash"] = hashlib.sha256(canonical.encode()).hexdigest()
    return item


class FakeStore:
    def __init__(self, runs=(), comparisons=()):
        self.runs = list(runs)
        self.comparisons = list(comparisons)

    def lab_protocol_history(self, limit=200):
        return [{"protocol_id": "protocol-a", "version": 1, "title": "Protocol A"}]

    def lab_run_history(self, limit=200):
        return self.runs[:limit]

    def lab_comparison_history(self, limit=200):
        return self.comparisons[:limit]


def _comparison(**overrides):
    item = {
        "comparison_id": "comparison-1", "left_run_id": "run-a", "right_run_id": "run-b",
        "comparable": True, "outputs_match_within_tolerance": True,
        "different_campaigns": True, "provenance_groups_distinct": True,
        "shared_source_ids": [], "shared_dataset_ids": [],
        "independence_independently_verified": False,
    }
    item.update(overrides)
    return item


def test_matching_outputs_are_not_mistaken_for_independent_verification():
    store = FakeStore(
        [_run("run-a", "campaign-a", "origin-a"), _run("run-b", "campaign-b", "origin-b")],
        [_comparison()],
    )
    report = ReproducibilityIntelligence(store).build()
    protocol = report["protocols"][0]
    assert protocol["status"] == "matching_outputs_not_independently_verified"
    assert protocol["reproducibility_evidence_index"] == 80
    assert protocol["scientific_validity_established"] is False
    assert report["automatic_experiment_execution"] is False


def test_recorded_divergence_is_reported_and_reduces_evidence_index():
    store = FakeStore(
        [_run("run-a", "campaign-a", "origin-a"), _run("run-b", "campaign-b", "origin-b")],
        [_comparison(outputs_match_within_tolerance=False)],
    )
    protocol = ReproducibilityIntelligence(store).build()["protocols"][0]
    assert protocol["status"] == "recorded_output_divergence"
    assert protocol["comparisons"][0]["classification"] == "recorded_output_divergence"
    assert protocol["reproducibility_evidence_index"] == 60


def test_shared_sources_prevent_provenance_separation_credit():
    store = FakeStore(
        [_run("run-a", "campaign-a", "origin-a", source_ids=("paper-1",)),
         _run("run-b", "campaign-b", "origin-b", source_ids=("paper-1",))],
        [_comparison()],
    )
    protocol = ReproducibilityIntelligence(store).build()["protocols"][0]
    assert protocol["reproducibility_evidence_index"] == 60
    assert protocol["comparisons"][0]["components"]["provenance_separation"] == 0


def test_no_comparisons_means_no_index_not_zero():
    report = ReproducibilityIntelligence(FakeStore()).build()
    protocol = report["protocols"][0]
    assert protocol["status"] == "no_recorded_comparisons"
    assert protocol["reproducibility_evidence_index"] is None


def test_invalid_limits_are_rejected():
    with pytest.raises(ValueError):
        ReproducibilityIntelligence(FakeStore()).build(limit=0)
    with pytest.raises(ValueError):
        ReproducibilityIntelligence(FakeStore()).build(limit=True)

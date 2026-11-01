import math
import pytest

from ssswet_core.lab_statistics import LabStatisticalSummarizer


class FakeStore:
    def __init__(self, runs):
        self.runs = runs

    def lab_run_history(self, limit=200):
        return self.runs[:limit]


def run(run_id, value, campaign="campaign-a", **extra):
    return {
        "run_id": run_id,
        "protocol_id": "protocol-alpha",
        "protocol_version": 2,
        "campaign_id": campaign,
        "kind": "simulation",
        "outputs": {"response": value, "label": "not numeric", "valid": True},
        "provenance_group": extra.get("provenance_group", "group-a"),
        "independence_declared": extra.get("independence_declared", False),
    }


def test_numeric_outputs_are_summarized_without_inference_or_exclusion():
    store = FakeStore([
        run("r1", 1.0),
        run("r2", 2.0, "campaign-b", provenance_group="group-b", independence_declared=True),
        run("r3", 3.0, "campaign-c", provenance_group="group-c"),
        run("r4", 4.0, "campaign-d", provenance_group="group-d"),
    ])
    result = LabStatisticalSummarizer(store).build()
    summary = result["summaries"][0]
    assert summary["sample_size"] == 4
    assert summary["mean"] == 2.5
    assert summary["median"] == 2.5
    assert summary["minimum"] == 1.0
    assert summary["maximum"] == 4.0
    assert summary["sample_standard_deviation"] == pytest.approx(math.sqrt(5 / 3))
    assert summary["distinct_campaign_count"] == 4
    assert summary["declared_independent_run_count"] == 1
    assert summary["classification"] == "descriptive_only"
    assert summary["inferential_test_performed"] is False
    assert summary["causal_effect_established"] is False
    assert result["automatic_data_exclusion"] is False
    assert result["non_numeric_or_invalid_values_ignored"] == 8


def test_outlier_is_flagged_but_never_removed():
    store = FakeStore([run("r1", 1), run("r2", 1), run("r3", 1), run("r4", 100)])
    summary = LabStatisticalSummarizer(store).build()["summaries"][0]
    assert summary["sample_size"] == 4
    assert summary["outlier_candidates"] == [{
        "run_id": "r4", "value": 100.0, "reason": "outside_1_5_iqr_fence"
    }]


def test_single_observation_has_no_sample_standard_deviation():
    summary = LabStatisticalSummarizer(FakeStore([run("r1", 7)])).build()["summaries"][0]
    assert summary["sample_size"] == 1
    assert summary["sample_standard_deviation"] is None
    assert summary["classification"] == "single_observation"


def test_boolean_and_non_finite_values_are_ignored():
    item = run("r1", 1)
    item["outputs"].update({"nan": float("nan"), "inf": float("inf"), "flag": True})
    result = LabStatisticalSummarizer(FakeStore([item])).build()
    assert len(result["summaries"]) == 1
    assert result["summaries"][0]["output_name"] == "response"
    assert result["non_numeric_or_invalid_values_ignored"] == 5


@pytest.mark.parametrize("limit", [0, 501, True, "10"])
def test_invalid_limit_is_rejected(limit):
    with pytest.raises(ValueError, match="limit"):
        LabStatisticalSummarizer(FakeStore([])).build(limit=limit)

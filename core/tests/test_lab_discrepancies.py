from ssswet_core.lab_discrepancies import LabDiscrepancyAnalyzer


class FakeStore:
    def __init__(self, comparisons, runs):
        self.comparisons = comparisons
        self.runs = runs

    def lab_comparison_history(self, limit=200):
        return self.comparisons[:limit]

    def lab_run_history(self, limit=200):
        return self.runs[:limit]


def _run(run_id, campaign, kind="simulation"):
    return {
        "run_id": run_id, "campaign_id": campaign,
        "protocol_id": "protocol-a", "protocol_version": 2, "kind": kind,
    }


def _comparison(identifier, comparable, matches):
    return {
        "comparison_id": identifier, "left_run_id": "run-a",
        "right_run_id": "run-b", "comparable": comparable,
        "outputs_match_within_tolerance": matches,
        "tolerance": 0.01, "differences": [{"path": "energy", "delta": 2.0}],
    }


def test_comparable_output_divergence_is_a_review_lead_only():
    store = FakeStore(
        [_comparison("cmp-1", True, False)],
        [_run("run-a", "campaign-a"), _run("run-b", "campaign-b")],
    )
    first = LabDiscrepancyAnalyzer(store).build()
    second = LabDiscrepancyAnalyzer(store).build()
    finding = first["findings"][0]
    assert finding["classification"] == "recorded_result_divergence"
    assert finding["left_campaign_id"] != finding["right_campaign_id"]
    assert finding["scientific_contradiction_established"] is False
    assert first == second
    assert store.comparisons == [_comparison("cmp-1", True, False)]


def test_incompatible_conditions_are_not_called_divergences():
    store = FakeStore([_comparison("cmp-2", False, False)], [])
    finding = LabDiscrepancyAnalyzer(store).build()["findings"][0]
    assert finding["classification"] == "incompatible_conditions"


def test_missing_comparison_fields_are_incomplete_not_a_contradiction():
    store = FakeStore(
        [{"comparison_id": "cmp-3", "left_run_id": "run-a", "right_run_id": "run-b"}],
        [],
    )
    finding = LabDiscrepancyAnalyzer(store).build()["findings"][0]
    assert finding["classification"] == "incomplete_comparison_data"
    assert finding["scientific_contradiction_established"] is False


def test_matching_comparable_outputs_produce_no_finding():
    store = FakeStore([_comparison("cmp-4", True, True)], [])
    assert LabDiscrepancyAnalyzer(store).build()["findings"] == []


def test_limit_is_validated():
    import pytest
    with pytest.raises(ValueError):
        LabDiscrepancyAnalyzer(FakeStore([], [])).build(limit=0)

from ssswet_core.lab_verification import LabVerificationPlanner


class FakeStore:
    def __init__(self, comparisons, runs):
        self.comparisons = comparisons
        self.runs = runs

    def lab_comparison_history(self, limit=200):
        return self.comparisons[:limit]

    def lab_run_history(self, limit=200):
        return self.runs[:limit]


def _run(run_id, campaign):
    return {
        "run_id": run_id, "campaign_id": campaign, "protocol_id": "p",
        "protocol_version": 1, "kind": "simulation",
    }


def test_divergence_plan_contains_targeted_review_checks_and_is_read_only():
    comparison = {
        "comparison_id": "cmp", "left_run_id": "a", "right_run_id": "b",
        "comparable": True, "outputs_match_within_tolerance": False,
        "same_environment": False, "same_code_or_model_reference": False,
        "independence_independently_verified": False,
        "shared_dataset_ids": ["dataset-1"], "shared_source_ids": ["source-1"],
    }
    store = FakeStore([comparison], [_run("a", "team-a"), _run("b", "team-b")])
    result = LabVerificationPlanner(store).build()
    plan = result["plans"][0]
    codes = {item["code"] for item in plan["checks"]}
    assert {"environment", "implementation", "independence", "dataset_provenance",
            "source_provenance", "measurement_and_tolerance", "independent_repeat"} <= codes
    assert plan["automatic_execution"] is False
    assert plan["scientific_validity_established"] is False
    assert store.comparisons == [comparison]


def test_incompatible_comparison_gets_alignment_check_not_repeat_claim():
    comparison = {
        "comparison_id": "cmp-2", "left_run_id": "a", "right_run_id": "b",
        "comparable": False, "outputs_match_within_tolerance": False,
    }
    plan = LabVerificationPlanner(FakeStore([comparison], [])).build()["plans"][0]
    codes = {item["code"] for item in plan["checks"]}
    assert "align_conditions" in codes
    assert "independent_repeat" not in codes
    assert "recover_run_records" in codes


def test_empty_registry_returns_no_plans():
    result = LabVerificationPlanner(FakeStore([], [])).build()
    assert result["plans"] == []
    assert result["automatic_task_creation"] is False

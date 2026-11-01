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


class ReviewStore(FakeStore):
    def __init__(self, comparisons, runs):
        super().__init__(comparisons, runs)
        self.events = []

    def lab_verification_event_history(self, plan_id=None, limit=500):
        items = [event for event in self.events if not plan_id or event["plan_id"] == plan_id]
        return items[:limit]

    def append_lab_verification_event(self, event):
        if any(item["event_id"] == event["event_id"] for item in self.events):
            raise ValueError("duplicate event")
        self.events.append(dict(event))


def test_review_lifecycle_appends_history_and_closes_completed_check():
    comparison = {
        "comparison_id": "cmp-life", "left_run_id": "a", "right_run_id": "b",
        "comparable": True, "outputs_match_within_tolerance": False,
    }
    store = ReviewStore([comparison], [_run("a", "team-a"), _run("b", "team-b")])
    planner = LabVerificationPlanner(store)
    plan = planner.build()["plans"][0]
    code = next(item["code"] for item in plan["checks"] if item["code"] == "measurement_and_tolerance")
    first = planner.record_check_review(plan["plan_id"], code, "in_progress", "Reviewing units and tolerance.", "reviewer-1")
    second = planner.record_check_review(plan["plan_id"], code, "completed", "Units and tolerance reviewed.", "reviewer-2")
    assert first["event_id"] != second["event_id"]
    assert len(store.events) == 2
    refreshed = planner.build()["plans"][0]
    check = next(item for item in refreshed["checks"] if item["code"] == code)
    assert check["review_state"] == "completed"
    assert len(check["review_history"]) == 2
    try:
        planner.record_check_review(plan["plan_id"], code, "blocked", "Reopen", "reviewer-3")
    except ValueError as error:
        assert "closed" in str(error)
    else:
        raise AssertionError("Completed checks must be closed")


def test_review_lifecycle_rejects_unknown_check_and_empty_note():
    store = ReviewStore([{
        "comparison_id": "cmp-invalid", "left_run_id": "a", "right_run_id": "b",
        "comparable": False,
    }], [])
    planner = LabVerificationPlanner(store)
    plan_id = planner.build()["plans"][0]["plan_id"]
    for code, note in (("not-a-check", "Note"), ("align_conditions", "  ")):
        try:
            planner.record_check_review(plan_id, code, "completed", note, "reviewer")
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid review event must be rejected")
    assert store.events == []

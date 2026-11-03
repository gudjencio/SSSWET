from ssswet_core.rescue_workflow import build_rescue_workflow


def test_rescue_workflow_requires_human_approval_for_evacuation():
    result = build_rescue_workflow(["remote_sensing", "evacuation_support"])
    assert result["requires_human_approval"]
    assert not result["rejected"]


def test_rescue_workflow_rejects_unknown_actions():
    result = build_rescue_workflow(["weapon_targeting"])
    assert result["rejected"]
    assert not result["actions"]

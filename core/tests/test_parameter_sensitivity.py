import pytest
from dataclasses import replace

from ssswet_core.digital_lab import DigitalLabService
from ssswet_core.parameter_sensitivity import ParameterSensitivityPlanner
from test_digital_lab import make_protocol, setup


def valid_design():
    return {
        "input": {
            "unit": "unitless",
            "range": {"minimum": 0, "maximum": 10},
            "baseline": 5,
            "levels": [0, 5, 10],
            "measurement_uncertainty": {"value": 0.01, "unit": "unitless"},
            "replicates": 2,
            "safety_constraints": "Computational values only; no physical execution.",
            "rationale": "Assess the documented numerical input range.",
        }
    }


def test_complete_design_builds_repeatable_oat_scenarios(tmp_path):
    store, _ = setup(tmp_path)
    protocol = replace(make_protocol(), parameter_sensitivity=valid_design())
    # Re-publish in a separate store because published versions are immutable.
    store2, _ = setup(tmp_path / "second")
    from ssswet_core.campaigns import CampaignMilestone, create_campaign, set_campaign_state
    campaign = create_campaign(
        "campaign-source", "campaign-source", "Digital laboratory research",
        "computational science",
        [CampaignMilestone("m1", "Review", "Review protocol")],
    )
    store2.save_campaign(set_campaign_state(campaign, "active"))
    DigitalLabService(store2).publish_protocol(protocol)

    report = ParameterSensitivityPlanner(store2).build()
    assert report["count"] == 1
    plan = report["plans"][0]
    assert plan["classification"] == "ready_for_human_review"
    assert plan["design_type"] == "one_factor_at_a_time"
    assert plan["scenario_count"] == 6
    assert len({item["scenario_id"] for item in plan["scenarios"]}) == 6
    assert all(item["execution_authorized"] is False for item in plan["scenarios"])
    assert plan["parameter_interactions"] == "not_assessed"
    assert plan["causal_effects_established"] is False
    assert report["automatic_execution"] is False
    assert report["scientific_validity_established"] is False


def test_missing_parameter_design_is_blocked_without_scenarios(tmp_path):
    store, _ = setup(tmp_path)
    report = ParameterSensitivityPlanner(store).build()
    plan = report["plans"][0]
    assert plan["classification"] == "incomplete_design"
    assert plan["scenarios"] == []
    assert "input" in plan["missing_or_invalid_designs"]


@pytest.mark.parametrize("limit", [0, 501, True, "10"])
def test_invalid_limits_are_rejected(tmp_path, limit):
    store, _ = setup(tmp_path)
    with pytest.raises(ValueError, match="limit"):
        ParameterSensitivityPlanner(store).build(limit=limit)


def test_invalid_units_and_measurement_uncertainty_are_reported(tmp_path):
    store, _ = setup(tmp_path)
    design = valid_design()
    design["input"]["unit"] = "metres"
    design["input"]["measurement_uncertainty"]["unit"] = "seconds"
    protocol = replace(make_protocol(), parameter_sensitivity=design)
    store2, _ = setup(tmp_path / "unit-check")
    from ssswet_core.campaigns import CampaignMilestone, create_campaign, set_campaign_state
    campaign = create_campaign(
        "campaign-source", "campaign-source", "Digital laboratory research",
        "computational science",
        [CampaignMilestone("m1", "Review", "Review protocol")],
    )
    store2.save_campaign(set_campaign_state(campaign, "active"))
    DigitalLabService(store2).publish_protocol(protocol)
    plan = ParameterSensitivityPlanner(store2).build()["plans"][0]
    assert plan["classification"] == "incomplete_design"
    errors = " ".join(plan["missing_or_invalid_designs"]["input"])
    assert "unit" in errors

import pytest
from dataclasses import replace

from ssswet_core.digital_lab import DigitalLabService, LabProtocol
from ssswet_core.parameter_sensitivity import ParameterSensitivityPlanner
from ssswet_core.persistence import SQLiteResearchStore
from ssswet_core.campaigns import CampaignMilestone, create_campaign, set_campaign_state


def make_protocol(version=1, parameter_sensitivity=None):
    return LabProtocol(
        "sensitivity-protocol", version, "Simple numerical model",
        "Compare a documented numerical output", "campaign-source",
        ("Record input", "Apply declared equation", "Record output"),
        ("input",), ("output",), {"input": "unitless", "output": "unitless"},
        ("same initial condition",), ("Illustrative model only",),
        ("No physical execution is performed by SSSWET",),
        "published", "reviewer", "Reviewed for clarity and reproducibility.",
        parameter_sensitivity=parameter_sensitivity or {},
    )


def setup(tmp_path):
    store = SQLiteResearchStore(tmp_path / "sensitivity.sqlite3")
    campaign = create_campaign(
        "campaign-source", "campaign-source", "Digital laboratory research",
        "computational science",
        [CampaignMilestone("m1", "Protocol review", "Review the shared protocol")],
    )
    store.save_campaign(set_campaign_state(campaign, "active"))
    return store


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
    store = setup(tmp_path)
    DigitalLabService(store).publish_protocol(
        make_protocol(parameter_sensitivity=valid_design())
    )
    report = ParameterSensitivityPlanner(store).build()
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
    store = setup(tmp_path)
    DigitalLabService(store).publish_protocol(make_protocol())
    plan = ParameterSensitivityPlanner(store).build()["plans"][0]
    assert plan["classification"] == "incomplete_design"
    assert plan["scenarios"] == []
    assert "input" in plan["missing_or_invalid_designs"]


@pytest.mark.parametrize("limit", [0, 501, True, "10"])
def test_invalid_limits_are_rejected(tmp_path, limit):
    store = setup(tmp_path)
    with pytest.raises(ValueError, match="limit"):
        ParameterSensitivityPlanner(store).build(limit=limit)


def test_invalid_units_and_measurement_uncertainty_are_reported(tmp_path):
    store = setup(tmp_path)
    design = valid_design()
    design["input"]["unit"] = "metres"
    design["input"]["measurement_uncertainty"]["unit"] = "seconds"
    DigitalLabService(store).publish_protocol(
        make_protocol(parameter_sensitivity=design)
    )
    plan = ParameterSensitivityPlanner(store).build()["plans"][0]
    assert plan["classification"] == "incomplete_design"
    errors = " ".join(plan["missing_or_invalid_designs"]["input"])
    assert "unit" in errors

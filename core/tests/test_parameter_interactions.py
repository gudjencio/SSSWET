import pytest

from ssswet_core.campaigns import CampaignMilestone, create_campaign, set_campaign_state
from ssswet_core.digital_lab import DigitalLabService, LabProtocol
from ssswet_core.parameter_interactions import ParameterInteractionPlanner
from ssswet_core.persistence import SQLiteResearchStore


def make_protocol(metadata):
    return LabProtocol(
        "interaction-protocol", 1, "Two-factor computational model",
        "Explore a documented numerical model", "campaign-interaction",
        ("Set inputs", "Run model", "Record outputs"),
        ("alpha", "beta", "gamma"), ("response",),
        {"alpha": "unitless", "beta": "unitless", "gamma": "unitless", "response": "unitless"},
        ("same initial conditions",), ("Illustrative computational model",),
        ("No physical execution",), "published", "reviewer",
        "Reviewed for documentation and reproducibility.",
        parameter_sensitivity=metadata,
    )


def valid_factor(unit="unitless"):
    return {
        "unit": unit,
        "range": {"minimum": 0, "maximum": 2},
        "baseline": 1,
        "levels": [0, 1, 2],
        "measurement_uncertainty": {"value": 0.01, "unit": unit},
        "replicates": 2,
        "safety_constraints": "Computational model only; no physical execution.",
        "rationale": "Explore a documented numerical range.",
    }


def setup(tmp_path, metadata):
    store = SQLiteResearchStore(tmp_path / "interaction.sqlite3")
    campaign = create_campaign(
        "campaign-interaction", "campaign-interaction", "Interaction planning",
        "computational science",
        [CampaignMilestone("review", "Review", "Review the protocol")],
    )
    store.save_campaign(set_campaign_state(campaign, "active"))
    DigitalLabService(store).publish_protocol(make_protocol(metadata))
    return store


def metadata():
    return {
        "alpha": valid_factor(),
        "beta": valid_factor(),
        "gamma": valid_factor(),
        "interaction_candidates": [{
            "parameters": ["alpha", "beta"],
            "replicates": 2,
            "rationale": "Test whether the two documented inputs may interact.",
        }],
    }


def test_pairwise_factorial_grid_holds_other_parameters_at_baseline(tmp_path):
    store = setup(tmp_path, metadata())
    report = ParameterInteractionPlanner(store).build()
    plan = report["plans"][0]
    pair = plan["pair_plans"][0]
    assert plan["classification"] == "ready_for_human_review"
    assert pair["design_type"] == "balanced_two_factor_full_factorial"
    assert pair["scenario_count"] == 18
    assert pair["other_parameters_held_at_baseline"] == ["gamma"]
    assert all(item["parameters"]["gamma"] == 1 for item in pair["scenarios"])
    assert len({item["scenario_id"] for item in pair["scenarios"]}) == 18
    assert all(item["execution_authorized"] is False for item in pair["scenarios"])
    assert pair["interaction_effect_estimated"] is False
    assert plan["causal_effects_established"] is False
    assert plan["randomization_required_before_execution"] is True
    assert report["automatic_execution"] is False


def test_incomplete_factor_metadata_blocks_pair_without_scenarios(tmp_path):
    data = metadata()
    del data["beta"]
    store = setup(tmp_path, data)
    pair = ParameterInteractionPlanner(store).build()["plans"][0]["pair_plans"][0]
    assert pair["classification"] == "incomplete_factor_metadata"
    assert pair["scenarios"] == []
    assert "beta" in pair["errors"]


def test_pairwise_grid_is_capped_before_scenario_generation(tmp_path):
    data = metadata()
    data["interaction_candidates"][0]["replicates"] = 100
    store = setup(tmp_path, data)
    pair = ParameterInteractionPlanner(store).build()["plans"][0]["pair_plans"][0]
    assert pair["classification"] == "scenario_limit_exceeded"
    assert pair["scenarios"] == []
    assert pair["scenario_count"] == 0


def test_invalid_candidate_pairs_are_reported(tmp_path):
    data = metadata()
    data["interaction_candidates"] = [{
        "parameters": ["alpha", "unknown"],
        "replicates": 2,
        "rationale": "Invalid candidate should not be inferred.",
    }]
    store = setup(tmp_path, data)
    plan = ParameterInteractionPlanner(store).build()["plans"][0]
    assert plan["classification"] == "incomplete_or_limited"
    assert plan["pair_plans"] == []
    assert plan["errors"]


@pytest.mark.parametrize("limit", [0, 501, True, "10"])
def test_invalid_limits_are_rejected(tmp_path, limit):
    store = setup(tmp_path, metadata())
    with pytest.raises(ValueError, match="limit"):
        ParameterInteractionPlanner(store).build(limit=limit)

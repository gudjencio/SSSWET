import pytest

from ssswet_core.digital_lab import DigitalLabService, LabProtocol, LabRun
from ssswet_core.persistence import SQLiteResearchStore
from ssswet_core.campaigns import CampaignMilestone, create_campaign, set_campaign_state


def make_protocol(state="published"):
    return LabProtocol(
        "protocol-1", 1, "Simple numerical model", "Compare a documented numerical output",
        "campaign-source", ("Record input", "Apply declared equation", "Record output"),
        ("input",), ("output",), {"input": "unitless", "output": "unitless"},
        ("same initial condition",), ("Illustrative model only",),
        ("No physical execution is performed by SSSWET",),
        state, "reviewer", "Reviewed for clarity and reproducibility.",
    )


def make_run(run_id, campaign, output, kind="simulation", independent=True):
    return LabRun(
        run_id, "protocol-1", 1, campaign, kind, {"input": 2}, {"output": output},
        "Declared equation y=2x", {"runtime": "Python", "version": "3"},
        "model-reference-v1", campaign + "-provenance", independent,
        ("Illustrative computation; not a physical observation",),
    )


def setup(tmp_path):
    store = SQLiteResearchStore(tmp_path / "digital-lab.sqlite3")
    for campaign_id in ("campaign-source", "campaign-a", "campaign-b", "campaign-x"):
        campaign = create_campaign(
            campaign_id, campaign_id, "Digital laboratory research", "computational science",
            [CampaignMilestone("m1", "Protocol review", "Review shared protocol")],
        )
        store.save_campaign(set_campaign_state(campaign, "active"))
    service = DigitalLabService(store)
    service.publish_protocol(make_protocol())
    return store, service


def test_protocol_and_run_are_persisted_with_explicit_provenance(tmp_path):
    store, service = setup(tmp_path)
    run = make_run("run-a", "campaign-a", 4)
    saved = service.record_run(run)
    assert saved["run_id"] == "run-a"
    assert store.get_lab_protocol("protocol-1", 1)["review_note"]
    assert store.get_lab_run("run-a")["environment"]["runtime"] == "Python"


def test_reproduction_comparison_records_matching_conditions_and_outputs(tmp_path):
    _, service = setup(tmp_path)
    service.record_run(make_run("run-a", "campaign-a", 4))
    service.record_run(make_run("run-b", "campaign-b", 4.0001))
    result = service.compare_runs("run-a", "run-b", tolerance=0.001)
    assert result["comparable"] is True
    assert result["outputs_match_within_tolerance"] is True
    assert result["different_campaigns"] is True
    assert result["independence_declared_by_both"] is True
    assert result["independence_independently_verified"] is False
    assert result["scientific_validity_established"] is False


def test_parameter_or_protocol_mismatch_prevents_reproduction_claim(tmp_path):
    _, service = setup(tmp_path)
    service.record_run(make_run("run-a", "campaign-a", 4))
    second = make_run("run-b", "campaign-b", 4)
    from dataclasses import replace
    service.record_run(replace(second, parameters={"input": 3}))
    result = service.compare_runs("run-a", "run-b")
    assert result["comparable"] is False
    assert result["outputs_match_within_tolerance"] is False
    assert result["same_parameters"] is False


def test_only_published_reviewed_protocols_can_be_shared(tmp_path):
    store = SQLiteResearchStore(tmp_path / "draft.sqlite3")
    service = DigitalLabService(store)
    draft = make_protocol("draft")
    with pytest.raises(ValueError, match="published"):
        service.publish_protocol(draft)
    with pytest.raises(ValueError, match="reviewer"):
        LabProtocol(
            "bad", 1, "Title", "Objective", "campaign-source", ("step",),
            ("x",), ("y",), {}, ("control",), ("limit",), (), "published",
        )


def test_run_requires_published_protocol_and_foreign_campaign(tmp_path):
    _, service = setup(tmp_path)
    with pytest.raises(ValueError, match="another campaign"):
        service.record_run(make_run("same-team", "campaign-source", 4))
    with pytest.raises(ValueError, match="missing required"):
        from dataclasses import replace
        service.record_run(replace(make_run("missing", "campaign-x", 4), parameters={}))


def test_kind_mismatch_and_nested_output_differences_are_reported(tmp_path):
    _, service = setup(tmp_path)
    service.record_run(make_run("run-a", "campaign-a", {"values": [1, 2]}, "simulation"))
    service.record_run(make_run("run-b", "campaign-b", {"values": [1, 3]}, "real_observation"))
    result = service.compare_runs("run-a", "run-b")
    assert result["same_execution_kind"] is False
    assert result["comparable"] is False
    assert result["differences"][0]["field"] == "output.values[1]"


def test_duplicate_run_ids_and_immutable_records(tmp_path):
    store, service = setup(tmp_path)
    service.record_run(make_run("run-a", "campaign-a", 4))
    with pytest.raises(ValueError):
        service.record_run(make_run("run-a", "campaign-a", 4))
    with pytest.raises(Exception):
        with store._connect() as connection:
            connection.execute("UPDATE lab_runs SET run_json='{}' WHERE run_id='run-a'")


def test_negative_tolerance_is_rejected(tmp_path):
    _, service = setup(tmp_path)
    service.record_run(make_run("run-a", "campaign-a", 4))
    service.record_run(make_run("run-b", "campaign-b", 4))
    with pytest.raises(ValueError, match="non-negative"):
        service.compare_runs("run-a", "run-b", -0.1)

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
    assert len(saved["record_hash"]) == 64
    assert len(store.get_lab_protocol("protocol-1", 1)["content_hash"]) == 64
    assert store.get_lab_protocol("protocol-1", 1)["review_note"]
    assert store.get_lab_run("run-a")["environment"]["runtime"] == "Python"


def test_reproduction_comparison_records_matching_conditions_and_outputs(tmp_path):
    store, service = setup(tmp_path)
    service.record_run(make_run("run-a", "campaign-a", 4))
    service.record_run(make_run("run-b", "campaign-b", 4.0001))
    result = service.compare_runs("run-a", "run-b", tolerance=0.001)
    assert result["comparable"] is True
    assert result["outputs_match_within_tolerance"] is True
    assert result["different_campaigns"] is True
    assert result["independence_declared_by_both"] is True
    assert result["independent_reproduction_candidate"] is True
    assert result["independence_independently_verified"] is False
    assert result["scientific_validity_established"] is False
    assert len(store.lab_comparison_history()) == 1
    assert service.overview()["comparison_count"] == 1


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


def test_shared_dataset_prevents_independent_reproduction_candidate(tmp_path):
    from dataclasses import replace

    _, service = setup(tmp_path)
    left = replace(make_run("run-a", "campaign-a", 4), dataset_ids=("shared-dataset",))
    right = replace(make_run("run-b", "campaign-b", 4), dataset_ids=("shared-dataset",))
    service.record_run(left)
    service.record_run(right)
    result = service.compare_runs("run-a", "run-b")
    assert result["comparable"] is True
    assert result["shared_dataset_ids"] == ["shared-dataset"]
    assert result["independent_reproduction_candidate"] is False



def test_protocol_fingerprint_detects_database_tampering(tmp_path):
    store, service = setup(tmp_path)
    with store._connect() as connection:
        connection.execute("DROP TRIGGER lab_protocols_no_update")
        row = connection.execute(
            "SELECT protocol_json FROM lab_protocols WHERE protocol_id='protocol-1' AND version=1"
        ).fetchone()
        import json
        payload = json.loads(row["protocol_json"])
        payload["objective"] = "altered after publication"
        connection.execute(
            "UPDATE lab_protocols SET protocol_json=? WHERE protocol_id='protocol-1' AND version=1",
            (json.dumps(payload),),
        )
    with pytest.raises(ValueError, match="fingerprint check failed"):
        service.record_run(make_run("run-tampered-protocol", "campaign-a", 4))


def test_run_fingerprint_detects_database_tampering_before_comparison(tmp_path):
    store, service = setup(tmp_path)
    service.record_run(make_run("run-a", "campaign-a", 4))
    service.record_run(make_run("run-b", "campaign-b", 4))
    with store._connect() as connection:
        connection.execute("DROP TRIGGER lab_runs_no_update")
        row = connection.execute(
            "SELECT run_json FROM lab_runs WHERE run_id='run-a'"
        ).fetchone()
        import json
        payload = json.loads(row["run_json"])
        payload["outputs"]["output"] = 999
        connection.execute(
            "UPDATE lab_runs SET run_json=? WHERE run_id='run-a'",
            (json.dumps(payload),),
        )
    with pytest.raises(ValueError, match="fingerprint check failed"):
        service.compare_runs("run-a", "run-b")


@pytest.mark.parametrize("tolerance", [float("nan"), float("inf"), -float("inf"), True, "0.1"])
def test_non_finite_or_invalid_tolerances_are_rejected(tmp_path, tolerance):
    _, service = setup(tmp_path)
    with pytest.raises(ValueError, match="finite, non-negative"):
        service.compare_runs("missing-a", "missing-b", tolerance=tolerance)


def test_overview_reports_fingerprint_integrity(tmp_path):
    _, service = setup(tmp_path)
    service.record_run(make_run("run-a", "campaign-a", 4))
    report = service.overview()
    assert report["integrity"]["all_intact"] is True
    assert report["integrity"]["protocols_checked"] == 1
    assert report["integrity"]["runs_checked"] == 1


def test_reproduction_matrix_tracks_cross_campaign_pairs_without_running_comparisons(tmp_path):
    _, service = setup(tmp_path)
    service.record_run(make_run("run-a", "campaign-a", 4))
    service.record_run(make_run("run-b", "campaign-b", 4))
    service.record_run(make_run("run-x", "campaign-x", 4))
    report = service.reproduction_matrix()
    group = report["protocol_groups"][0]
    assert group["distinct_campaign_count"] == 3
    assert group["run_count"] == 3
    assert len(group["cross_campaign_pairs"]) == 3
    assert group["pending_comparison_count"] == 3
    assert report["automatic_comparisons_executed"] is False
    service.compare_runs("run-a", "run-b")
    updated = service.reproduction_matrix()["protocol_groups"][0]
    assert updated["pending_comparison_count"] == 2
    assert any(pair["comparison_recorded"] for pair in updated["cross_campaign_pairs"])


def test_run_comparison_exposes_environment_and_model_reference_differences(tmp_path):
    from dataclasses import replace

    _, service = setup(tmp_path)
    service.record_run(make_run("run-a", "campaign-a", 4))
    other = replace(
        make_run("run-b", "campaign-b", 4),
        environment={"runtime": "Python", "version": "3.12"},
        code_or_model_reference="model-reference-v2",
    )
    service.record_run(other)
    report = service.compare_runs("run-a", "run-b")
    assert report["comparable"] is True
    assert report["same_environment"] is False
    assert report["environment_differences"][0]["field"] == "version"
    assert report["same_code_or_model_reference"] is False
    assert report["independent_reproduction_candidate"] is True


def test_protocol_proposal_acceptance_creates_new_immutable_version(tmp_path):
    from ssswet_core.protocol_proposals import ProtocolProposalService

    store, _ = setup(tmp_path)
    service = ProtocolProposalService(store)
    proposal = service.submit(
        "proposal-1", "protocol-1", 1, "campaign-a",
        {"objective": "Compare a revised documented numerical output",
         "limitations": ["Illustrative model only", "No physical execution"]},
        "Clarify the objective and state the simulation boundary.",
    )
    assert proposal["status"] == "pending"
    accepted = service.decide(
        "proposal-1", "campaign-source", "accepted",
        "Reviewed wording and limitations; accept as version 2.",
    )
    assert accepted["status"] == "accepted"
    assert accepted["resulting_version"] == 2
    assert len(accepted["events"]) == 2
    assert store.get_lab_protocol("protocol-1", 1)["objective"] == "Compare a documented numerical output"
    version_two = store.get_lab_protocol("protocol-1", 2)
    assert version_two["objective"] == "Compare a revised documented numerical output"
    assert version_two["reviewed_by"] == "campaign-source"
    assert version_two["content_hash"]


def test_protocol_proposal_rejection_preserves_published_protocol(tmp_path):
    from ssswet_core.protocol_proposals import ProtocolProposalService

    store, _ = setup(tmp_path)
    service = ProtocolProposalService(store)
    service.submit(
        "proposal-reject", "protocol-1", 1, "campaign-b",
        {"title": "Alternative title"},
        "Suggest a title change.",
    )
    result = service.decide(
        "proposal-reject", "campaign-source", "rejected",
        "The current title is retained for consistency.",
    )
    assert result["status"] == "rejected"
    assert result["resulting_version"] == 0
    assert store.get_lab_protocol("protocol-1", 2) is None
    assert store.get_lab_protocol("protocol-1", 1)["title"] == "Simple numerical model"


def test_protocol_proposals_require_owner_review_and_latest_base(tmp_path):
    from ssswet_core.protocol_proposals import ProtocolProposalService

    store, _ = setup(tmp_path)
    service = ProtocolProposalService(store)
    service.submit(
        "proposal-auth", "protocol-1", 1, "campaign-a",
        {"title": "Revised title"}, "A rationale.",
    )
    with pytest.raises(ValueError, match="owner campaign"):
        service.decide("proposal-auth", "campaign-b", "accepted", "Review note.")
    with pytest.raises(ValueError, match="review note"):
        service.decide("proposal-auth", "campaign-source", "rejected", " ")


def test_protocol_proposal_rejects_unsafe_or_unknown_patch_fields(tmp_path):
    from ssswet_core.protocol_proposals import ProtocolProposalService

    _, _ = setup(tmp_path)
    service = ProtocolProposalService(_)
    with pytest.raises(ValueError, match="Unsupported protocol fields"):
        service.submit(
            "proposal-bad", "protocol-1", 1, "campaign-a",
            {"owner_campaign_id": "campaign-a"}, "Change ownership.",
        )

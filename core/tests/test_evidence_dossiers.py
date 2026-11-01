import json

import pytest

from ssswet_core.campaigns import CampaignMilestone, create_campaign, set_campaign_state
from ssswet_core.digital_lab import DigitalLabService, LabProtocol, LabRun
from ssswet_core.evidence_dossiers import EvidenceDossierService
from ssswet_core.persistence import SQLiteResearchStore


def setup(tmp_path):
    store = SQLiteResearchStore(tmp_path / "evidence.sqlite3")
    for campaign_id in ("campaign-source", "campaign-a", "campaign-b"):
        campaign = create_campaign(
            campaign_id, campaign_id, "Evidence review", "computational science",
            [CampaignMilestone("m1", "Review", "Review evidence")],
        )
        store.save_campaign(set_campaign_state(campaign, "active"))
    lab = DigitalLabService(store)
    protocol = LabProtocol(
        "protocol-1", 1, "Documented numerical model", "Compare a numerical output",
        "campaign-source", ("Record input", "Apply equation", "Record output"),
        ("input",), ("output",), {"input": "unitless", "output": "unitless"},
        ("same input",), ("Illustrative model",),
        ("No physical execution",), "published", "campaign-source", "Reviewed for reproducibility.",
    )
    lab.publish_protocol(protocol)
    run = LabRun(
        "run-a", "protocol-1", 1, "campaign-a", "simulation", {"input": 2}, {"output": 4},
        "y=2x", {"runtime": "Python", "version": "3"}, "model-v1", "campaign-a-proof",
        True, ("Simulation only",),
    )
    run_b = LabRun(
        "run-b", "protocol-1", 1, "campaign-b", "simulation", {"input": 2}, {"output": 4},
        "y=2x", {"runtime": "Python", "version": "3"}, "model-v1", "campaign-b-proof",
        True, ("Simulation only",),
    )
    lab.record_run(run)
    lab.record_run(run_b)
    comparison = lab.compare_runs("run-a", "run-b")
    with store._connect() as connection:
        connection.execute(
            "INSERT INTO sources(source_id,title,source_type,authors,institutions,dataset_ids,related_source_ids,metadata) VALUES(?,?,?,?,?,?,?,?)",
            ("source-1", "Reference method", "literature", "Author", "Institution", "[]", "[]", "{}"),
        )
        connection.execute(
            "INSERT INTO lab_datasets(dataset_id,version,record_json,content_fingerprint,registered_at) VALUES(?,?,?,?,CURRENT_TIMESTAMP)",
            ("dataset-1", 1, json.dumps({"name": "example"}), "a" * 64),
        )
    return store, comparison


def test_assemble_captures_traceable_snapshot(tmp_path):
    store, comparison = setup(tmp_path)
    service = EvidenceDossierService(store)
    dossier = service.assemble(
        "dossier-1", "Numerical reproduction evidence", "Two campaigns produced the same declared output.",
        protocol_refs=[{"protocol_id": "protocol-1", "version": 1}],
        run_ids=["run-a", "run-b"],
        dataset_refs=[{"dataset_id": "dataset-1", "version": 1}],
        comparison_ids=[comparison["comparison_id"]],
        source_ids=["source-1"],
        objections=["The result is a simulation, not a physical observation."],
    )
    assert dossier["verification_state"] == "unverified"
    assert dossier["scientific_validity_established"] is False
    assert len(dossier["runs"]) == 2
    assert len(dossier["sources"]) == 1
    assert len(dossier["events"]) == 1
    assert len(dossier["content_hash"]) == 64


def test_dossier_rejects_unknown_references(tmp_path):
    store, _ = setup(tmp_path)
    service = EvidenceDossierService(store)
    with pytest.raises(ValueError, match="unknown run reference"):
        service.assemble("bad", "Bad dossier", "Summary", run_ids=["missing-run"])


def test_dossier_and_events_are_immutable(tmp_path):
    store, _ = setup(tmp_path)
    service = EvidenceDossierService(store)
    service.assemble("dossier-1", "Evidence", "Summary")
    with pytest.raises(Exception):
        with store._connect() as connection:
            connection.execute("UPDATE evidence_dossiers SET title='tampered' WHERE dossier_id='dossier-1'")
    with pytest.raises(Exception):
        with store._connect() as connection:
            connection.execute("DELETE FROM evidence_dossier_events WHERE dossier_id='dossier-1'")


def test_review_is_append_only_and_does_not_verify_science(tmp_path):
    store, _ = setup(tmp_path)
    service = EvidenceDossierService(store)
    service.assemble("dossier-1", "Evidence", "Summary")
    reviewed = service.review("dossier-1", "campaign-b", "accepted_for_review", "Ready for substantive scientific review.")
    assert reviewed["events"][-1]["decision"] == "accepted_for_review"
    assert reviewed["scientific_validity_established"] is False
    assert reviewed["verification_state"] == "unverified"
    assert len(reviewed["events"]) == 2


def test_invalid_review_decision_and_duplicate_dossier_are_rejected(tmp_path):
    store, _ = setup(tmp_path)
    service = EvidenceDossierService(store)
    service.assemble("dossier-1", "Evidence", "Summary")
    with pytest.raises(ValueError, match="decision"):
        service.review("dossier-1", "campaign-b", "verified", "No")
    with pytest.raises(ValueError, match="already exists"):
        service.assemble("dossier-1", "Evidence", "Summary")


def test_overview_exposes_traceability_counts(tmp_path):
    store, _ = setup(tmp_path)
    service = EvidenceDossierService(store)
    service.assemble("dossier-1", "Evidence", "Summary", run_ids=["run-a"], source_ids=["source-1"])
    report = service.overview()
    assert report["count"] == 1
    assert report["dossiers"][0]["run_count"] == 1
    assert report["dossiers"][0]["source_count"] == 1
    assert report["review_is_separate_from_verification"] is True

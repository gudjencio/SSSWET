import pytest

from ssswet_core.reproducibility_monitor import ResearchReproducibilityMonitor


def complete_run(run_id, fingerprint):
    return {
        "run_id": run_id,
        "protocol_id": "protocol-a",
        "protocol_version": 2,
        "dataset_id": "dataset-a",
        "dataset_version": 3,
        "parameters": {"iterations": 100, "seed": 7},
        "environment": {"software": "simulator-1.2", "hardware": "cpu"},
        "result_fingerprint": fingerprint,
    }


def test_flags_incomplete_run_metadata_without_inventing_values():
    report = ResearchReproducibilityMonitor().analyze([{"run_id": "run-a"}])
    finding = report["findings"][0]
    assert finding["category"] == "incomplete_run_metadata"
    assert "environment" in finding["missing_fields"]
    assert report["reproducibility_established"] is False


def test_flags_different_outputs_for_matching_recorded_conditions():
    report = ResearchReproducibilityMonitor().analyze([
        complete_run("run-a", "hash-1"),
        complete_run("run-b", "hash-2"),
    ])
    assert any(item["category"] == "different_outputs_under_matching_recorded_conditions"
               for item in report["findings"])
    assert report["experiments_executed"] is False


def test_matching_fingerprints_are_not_claimed_as_reproduction():
    report = ResearchReproducibilityMonitor().analyze([
        complete_run("run-a", "hash-1"),
        complete_run("run-b", "hash-1"),
    ])
    assert report["findings"] == []
    assert report["reproducibility_established"] is False
    assert "do not prove" in report["notice"]


def test_duplicate_run_identifiers_are_flagged():
    report = ResearchReproducibilityMonitor().analyze([
        complete_run("run-a", "hash-1"),
        complete_run("run-a", "hash-1"),
    ])
    assert "duplicate_run_identifier" in {
        item["category"] for item in report["findings"]
    }


def test_rejects_malformed_input():
    monitor = ResearchReproducibilityMonitor()
    with pytest.raises(ValueError, match="runs"):
        monitor.analyze({})
    with pytest.raises(ValueError, match="dictionary"):
        monitor.analyze([None])

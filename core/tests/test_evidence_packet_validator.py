import pytest

from ssswet_core.evidence_packet_validator import (
    MAX_BATCH_SIZE, validate_packet, validate_packets,
)


def packet(**updates):
    value = {
        "packet_id": "packet-001",
        "title": "Thermal insulation comparison",
        "summary": "A bounded comparison of two insulation concepts.",
        "source_ids": ["source-a", "source-b"],
        "method": "Compare normalized thermal conductivity under documented conditions.",
        "limitations": ["Small sample set", "No long-duration field validation"],
        "protocol_id": "protocol-1",
        "dataset_ids": ["dataset-1"],
        "run_ids": ["run-1"],
    }
    value.update(updates)
    return value


def sources():
    return [
        {"source_id": "source-a", "provenance_group": "journal-a"},
        {"source_id": "source-b", "provenance_group": "institution-b"},
    ]


def test_valid_packet_preserves_legacy_contract_and_adds_quality_metrics():
    result = validate_packet(packet())
    assert result["valid_for_review"] is True
    assert result["source_count"] == 2
    assert result["scientific_validity_established"] is False
    assert result["automatic_adjudication"] is False
    assert result["packet_fingerprint_sha256"]
    assert result["review_readiness_total"] == 4


def test_required_fields_and_non_object_are_reported():
    result = validate_packet({"title": "Only a title"})
    assert result["valid_for_review"] is False
    assert set(result["missing"]) >= {"summary", "source_ids", "method", "limitations"}
    malformed = validate_packet([])
    assert "packet_must_be_an_object" in malformed["errors"]


def test_text_fields_are_bounded_and_non_empty():
    result = validate_packet(packet(title=" " * 3, summary="x" * 8001))
    assert "title_must_be_text_within_length_limit" in result["errors"]
    assert "summary_must_be_text_within_length_limit" in result["errors"]


def test_limitations_accept_string_or_structured_list():
    assert validate_packet(packet(limitations="Limited sample size"))["valid_for_review"]
    result = validate_packet(packet(limitations=["Valid limit", "", 7]))
    assert "limitations_items_must_be_non_empty_strings" in result["errors"]
    assert result["valid_for_review"] is False


def test_source_ids_must_be_unique_and_well_formed():
    duplicate = validate_packet(packet(source_ids=["source-a", "source-a"]))
    assert duplicate["duplicate_sources"] is True
    assert "duplicate_source_ids" in duplicate["errors"]
    invalid = validate_packet(packet(source_ids=["", "../unsafe"]))
    assert "source_ids_must_be_valid_non_empty_identifiers" in invalid["errors"]


def test_source_records_reconcile_against_referenced_ids():
    missing = validate_packet(packet(), source_records=[sources()[0]])
    assert "source_ids_without_matching_source_records" in missing["errors"]
    complete = validate_packet(packet(), source_records=sources())
    assert complete["valid_for_review"] is True
    assert complete["source_record_count"] == 2


def test_duplicate_source_records_are_rejected():
    duplicated = sources() + [sources()[0]]
    result = validate_packet(packet(), source_records=duplicated)
    assert any(item.startswith("duplicate_source_record:") for item in result["errors"])


def test_provenance_group_count_is_reported_without_claiming_independence():
    same_group = [
        {"source_id": "source-a", "provenance_group": "same-origin"},
        {"source_id": "source-b", "provenance_group": "same-origin"},
    ]
    result = validate_packet(packet(), source_records=same_group)
    assert result["independent_provenance_group_count"] == 1
    assert result["provenance_groups_are_metadata_not_proof_of_independence"] is True


def test_reproducibility_links_are_explicit_and_actionable():
    result = validate_packet(packet(protocol_id="", dataset_ids=[], run_ids=[]))
    assert result["reproducibility"]["protocol_linked"] is False
    assert result["reproducibility"]["datasets_linked"] is False
    assert result["reproducibility"]["runs_linked"] is False
    assert {"protocol_not_linked", "datasets_not_linked", "runs_not_linked"} <= set(result["warnings"])


def test_packet_fingerprint_is_stable_and_content_sensitive():
    first = validate_packet(packet())
    second = validate_packet(packet())
    changed = validate_packet(packet(summary="A different summary."))
    assert first["packet_fingerprint_sha256"] == second["packet_fingerprint_sha256"]
    assert first["packet_fingerprint_sha256"] != changed["packet_fingerprint_sha256"]


def test_non_json_and_oversized_packets_are_blocked():
    non_json = validate_packet(packet(extra=object()))
    assert "packet_is_not_json_serializable_or_exceeds_64kb" in non_json["errors"]
    oversized = validate_packet(packet(summary="x" * 70000))
    assert oversized["valid_for_review"] is False


def test_source_record_mismatch_is_a_blocker_when_records_are_supplied():
    result = validate_packet(packet(), source_records=[
        {"source_id": "source-a", "provenance_group": "a"},
        {"source_id": "source-c", "provenance_group": "c"},
    ])
    assert result["valid_for_review"] is False
    assert "source_ids_without_matching_source_records" in result["errors"]
    assert "unreferenced_source_records_present" in result["warnings"]


def test_batch_validation_aggregates_blockers_and_duplicate_packet_ids():
    result = validate_packets([packet(), packet(summary="")])
    assert result["packet_count"] == 2
    assert result["valid_for_review_count"] == 1
    assert result["blocked_count"] == 1
    assert result["batch_valid_for_review"] is False
    duplicates = validate_packets([packet(), packet()])
    assert duplicates["duplicate_packet_ids"] == ["packet-001"]
    assert duplicates["batch_valid_for_review"] is False


def test_batch_validation_is_bounded_and_rejects_invalid_limits():
    with pytest.raises(ValueError, match="max_packets"):
        validate_packets([], max_packets=0)
    with pytest.raises(ValueError, match="configured limit"):
        validate_packets([packet(), packet()], max_packets=1)
    with pytest.raises(ValueError, match="500"):
        validate_packets([], max_packets=MAX_BATCH_SIZE + 1)
    with pytest.raises(ValueError, match="packets"):
        validate_packets({})


def test_basic_legacy_packet_without_source_records_remains_reviewable():
    legacy = {
        "title": "Legacy packet",
        "summary": "Existing callers supply only source identifiers.",
        "source_ids": ["legacy-source-1"],
        "method": "Review published measurements.",
        "limitations": "No independent replication supplied.",
    }
    result = validate_packet(legacy)
    assert result["valid_for_review"] is True
    assert "source_records_not_supplied_source_identity_not_independently_checked" in result["warnings"]

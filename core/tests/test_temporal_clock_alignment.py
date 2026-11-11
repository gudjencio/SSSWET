import hashlib
import json

import pytest

from ssswet_core.temporal_clock_alignment import (
    ALIGNMENT_METHOD,
    UNCERTAINTY_METHOD,
    align_events,
    build_clock_model,
    verify_clock_model,
)


def _digest(payload):
    canonical = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _anchors():
    return [
        {
            "anchor_id": "camera-end",
            "session_id": "session-1",
            "source_id": "camera-a",
            "source_timestamp": "2026-11-11T10:10:00+00:00",
            "reference_timestamp": "2026-11-11T10:11:00+00:00",
            "uncertainty_seconds": 2.0,
            "reference_evidence_ref": "camera-log:end",
        },
        {
            "anchor_id": "camera-start",
            "session_id": "session-1",
            "source_id": "camera-a",
            "source_timestamp": "2026-11-11T10:00:00+00:00",
            "reference_timestamp": "2026-11-11T10:01:00+00:00",
            "uncertainty_seconds": 1.0,
            "reference_evidence_ref": "camera-log:start",
        },
    ]


def test_clock_alignment_is_deterministic_and_retains_anchor_provenance():
    anchors = _anchors()
    first = build_clock_model(anchors)
    second = build_clock_model(list(reversed(anchors)))

    assert first["schema_version"] == 2
    assert first["model_sha256"] == second["model_sha256"]
    assert [item["anchor_id"] for item in first["anchors"]] == [
        "camera-start", "camera-end"
    ]
    assert first["anchor_evidence_ref_count"] == 2
    assert first["all_anchor_uncertainties_declared"] is True
    assert first["alignment_method"] == ALIGNMENT_METHOD
    assert first["uncertainty_method"] == UNCERTAINTY_METHOD
    assert first["uncertainty_is_confidence_interval"] is False
    assert first["drift_intervals"][0]["from_anchor_id"] == "camera-start"
    assert first["drift_intervals"][0]["to_anchor_id"] == "camera-end"
    assert first["drift_intervals"][0]["drift_ppm"] == 0.0
    assert verify_clock_model(first)["valid"] is True

    result = align_events(first, [{
        "event_id": "frame-300",
        "session_id": "session-1",
        "source_id": "camera-a",
        "timestamp": "2026-11-11T10:05:00+00:00",
        "uncertainty_seconds": 0.25,
    }])
    event = result["events"][0]
    assert event["aligned_at"] == "2026-11-11T10:06:00+00:00"
    assert event["left_anchor_id"] == "camera-start"
    assert event["right_anchor_id"] == "camera-end"
    assert event["interpolation_fraction"] == 0.5
    assert event["anchor_reference_evidence_refs"] == [
        "camera-log:start", "camera-log:end"
    ]
    assert event["anchor_provenance_complete"] is True
    assert event["anchor_uncertainty_seconds"] == 1.5
    assert event["event_uncertainty_seconds"] == 0.25
    assert event["uncertainty_seconds"] == 1.75
    assert event["uncertainty_bound_complete"] is True
    assert event["uncertainty_is_confidence_interval"] is False
    assert event["extrapolation_used"] is False
    assert result["unrecorded_history_recovered"] is False


def test_missing_uncertainty_is_not_silently_reported_as_zero():
    anchors = [
        {key: value for key, value in item.items() if key != "uncertainty_seconds"}
        for item in _anchors()
    ]
    model = build_clock_model(anchors)
    assert model["all_anchor_uncertainties_declared"] is False

    result = align_events(model, [{
        "event_id": "frame-unknown",
        "session_id": "session-1",
        "source_id": "camera-a",
        "timestamp": "2026-11-11T10:05:00+00:00",
    }])
    event = result["events"][0]
    assert event["anchor_uncertainty_seconds"] is None
    assert event["event_uncertainty_seconds"] is None
    assert event["uncertainty_seconds"] is None
    assert event["uncertainty_bound_complete"] is False
    assert result["complete_uncertainty_bound_count"] == 0


def test_exact_anchor_uses_one_provenance_reference_without_duplication():
    model = build_clock_model(_anchors())
    result = align_events(model, [{
        "event_id": "exact-start",
        "session_id": "session-1",
        "source_id": "camera-a",
        "timestamp": "2026-11-11T10:00:00+00:00",
        "uncertainty_seconds": 0.0,
    }])
    event = result["events"][0]
    assert event["left_anchor_id"] == event["right_anchor_id"] == "camera-start"
    assert event["anchor_reference_evidence_refs"] == ["camera-log:start"]
    assert event["anchor_provenance_complete"] is True
    assert event["interpolation_fraction"] == 0.0
    assert event["anchor_interval_seconds"] == 0.0
    assert event["uncertainty_seconds"] == 1.0


def test_model_verifier_rejects_semantic_flags_even_when_digest_is_recomputed():
    model = build_clock_model(_anchors())
    payload = {key: value for key, value in model.items() if key != "model_sha256"}
    payload["extrapolation_permitted"] = True
    tampered = {**payload, "model_sha256": _digest(payload)}
    assert verify_clock_model(tampered)["valid"] is False

    payload = {key: value for key, value in model.items() if key != "model_sha256"}
    payload["uncertainty_is_confidence_interval"] = True
    tampered = {**payload, "model_sha256": _digest(payload)}
    assert verify_clock_model(tampered)["valid"] is False


def test_anchor_identifiers_and_evidence_references_are_bounded_and_unique():
    duplicate = _anchors()
    duplicate[1]["anchor_id"] = duplicate[0]["anchor_id"]
    with pytest.raises(ValueError):
        build_clock_model(duplicate)

    oversized = _anchors()
    oversized[0]["reference_evidence_ref"] = "r" * 501
    with pytest.raises(ValueError):
        build_clock_model(oversized)

    oversized_id = _anchors()
    oversized_id[0]["anchor_id"] = "a" * 161
    with pytest.raises(ValueError):
        build_clock_model(oversized_id)


def test_legacy_schema_one_models_remain_verifiable_but_do_not_claim_complete_bounds():
    payload = {
        "schema_version": 1,
        "session_id": "legacy-session",
        "source_id": "legacy-camera",
        "anchors": [
            {
                "source_timestamp": "2026-11-11T10:00:00+00:00",
                "reference_timestamp": "2026-11-11T10:01:00+00:00",
                "uncertainty_seconds": 1.0,
            },
            {
                "source_timestamp": "2026-11-11T10:10:00+00:00",
                "reference_timestamp": "2026-11-11T10:11:00+00:00",
                "uncertainty_seconds": 2.0,
            },
        ],
        "anchor_count": 2,
        "max_absolute_drift_ppm": 0.0,
        "drift_is_diagnostic_only": True,
        "extrapolation_permitted": False,
    }
    model = {**payload, "model_sha256": _digest(payload)}
    assert verify_clock_model(model)["valid"] is True

    result = align_events(model, [{
        "event_id": "legacy-frame",
        "session_id": "legacy-session",
        "source_id": "legacy-camera",
        "timestamp": "2026-11-11T10:05:00+00:00",
        "uncertainty_seconds": 0.1,
    }])
    event = result["events"][0]
    assert event["aligned_at"] == "2026-11-11T10:06:00+00:00"
    assert event["uncertainty_seconds"] is None
    assert event["uncertainty_bound_complete"] is False
    assert event["anchor_provenance_complete"] is False

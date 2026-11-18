from datetime import datetime, timedelta, timezone

import pytest

from ssswet_core.energy_storage_assurance import (
    MAX_SAMPLES,
    build_evidence_packet,
    capacity_fade,
    cell_imbalance,
    compare_protocols,
    detect_signal_anomalies,
    integrate_capacity,
    integrate_energy,
    round_trip_efficiency,
    segment_cycles,
    temperature_excursions,
    validate_energy_samples,
    verify_evidence_packet,
)


BASE = datetime(2026, 1, 1, tzinfo=timezone.utc)


def make_sample(
    index,
    mode="discharge",
    *,
    seconds=None,
    session="session-1",
    cycle="cycle-1",
    current=1.0,
    voltage=10.0,
    temperature=25.0,
    cells=(4.10, 4.09, 4.11),
    source="sensor-source-1",
    calibration_refs=("cal-1",),
    extra=None,
):
    stamp = BASE + timedelta(seconds=index * 60 if seconds is None else seconds)
    row = {
        "sample_id": f"sample-{index}-{session}",
        "session_id": session,
        "cycle_id": cycle,
        "source_id": source,
        "timestamp_utc": stamp.isoformat(),
        "mode": mode,
        "current_a": current,
        "voltage_v": voltage,
        "temperature_c": temperature,
        "cell_voltages_v": list(cells) if cells is not None else None,
        "calibration_refs": list(calibration_refs),
    }
    if extra:
        row.update(extra)
    return row


def one_hour_cycle():
    return [
        make_sample(0, "charge", seconds=0, current=2.0, voltage=10.0),
        make_sample(1, "charge", seconds=3600, current=2.0, voltage=10.0),
        make_sample(2, "discharge", seconds=7200, current=1.0, voltage=10.0),
        make_sample(3, "discharge", seconds=10800, current=1.0, voltage=10.0),
    ]


def test_validation_normalizes_timezone_and_drops_unknown_fields():
    row = make_sample(0, extra={"private_note": "must not enter normalized output"})
    row["timestamp_utc"] = "2026-01-01T01:00:00+01:00"
    result = validate_energy_samples([row])
    assert result[0]["timestamp_utc"] == "2026-01-01T00:00:00.000000Z"
    assert "private_note" not in result[0]
    assert result[0]["source_id"] == "sensor-source-1"


def test_validation_rejects_naive_timestamps():
    row = make_sample(0)
    row["timestamp_utc"] = "2026-01-01T00:00:00"
    with pytest.raises(ValueError, match="explicit timezone"):
        validate_energy_samples([row])


def test_validation_rejects_duplicate_sample_ids():
    first = make_sample(0)
    second = make_sample(1)
    second["sample_id"] = first["sample_id"]
    with pytest.raises(ValueError, match="unique"):
        validate_energy_samples([first, second])


def test_validation_rejects_non_monotonic_session_time():
    with pytest.raises(ValueError, match="strictly increase"):
        validate_energy_samples([make_sample(2), make_sample(1)])


def test_validation_rejects_non_finite_and_negative_current():
    row = make_sample(0, current=float("nan"))
    with pytest.raises(ValueError, match="finite"):
        validate_energy_samples([row])
    row = make_sample(0, current=-0.1)
    with pytest.raises(ValueError, match="at least"):
        validate_energy_samples([row])


def test_validation_is_bounded_before_record_processing():
    with pytest.raises(ValueError, match=str(MAX_SAMPLES)):
        validate_energy_samples([{}] * (MAX_SAMPLES + 1))


def test_validation_bounds_cell_count():
    row = make_sample(0, cells=[4.0] * 129)
    with pytest.raises(ValueError, match="at most 128"):
        validate_energy_samples([row])


def test_cycle_segmentation_preserves_complete_and_incomplete_groups():
    rows = [
        make_sample(0, "charge"),
        make_sample(1, "rest"),
        make_sample(2, "discharge"),
        make_sample(3, "discharge", cycle="cycle-2"),
    ]
    result = segment_cycles(rows)
    assert result[0]["complete_charge_discharge_pair"] is True
    assert result[0]["review_flags"] == []
    assert result[0]["calibration_refs"] == ["cal-1"]
    assert result[1]["complete_charge_discharge_pair"] is False
    assert "charge_observations_missing" in result[1]["review_flags"]
    assert result[1]["sample_ids"] == [rows[3]["sample_id"]]


def test_cycle_segmentation_flags_unexpected_order_without_rewriting_it():
    rows = [
        make_sample(0, "discharge"),
        make_sample(1, "charge"),
    ]
    result = segment_cycles(rows)[0]
    assert result["mode_sequence"] == ["discharge", "charge"]
    assert "unexpected_charge_discharge_order" in result["review_flags"]


def test_capacity_integration_uses_trapezoids_and_provenance():
    result = integrate_capacity(one_hour_cycle(), "cycle-1", max_gap_seconds=4000)
    assert result["metric"] == pytest.approx(1.0)
    assert result["unit"] == "Ah"
    assert result["integrated_intervals"] == 1
    assert result["source_ids"] == ["sensor-source-1"]
    assert result["calibration_refs"] == ["cal-1"]


def test_energy_integration_uses_voltage_times_current():
    result = integrate_energy(one_hour_cycle(), "cycle-1", mode="charge", max_gap_seconds=4000)
    assert result["metric"] == pytest.approx(20.0)
    assert result["unit"] == "Wh"


def test_integration_rejects_long_gaps():
    with pytest.raises(ValueError, match="gap exceeds"):
        integrate_capacity(one_hour_cycle(), "cycle-1")


def test_integration_does_not_bridge_rest_or_opposite_mode_samples():
    rows = [
        make_sample(0, "charge", seconds=0),
        make_sample(1, "rest", seconds=60),
        make_sample(2, "charge", seconds=120),
    ]
    with pytest.raises(ValueError, match="cannot bridge"):
        integrate_capacity(rows, "cycle-1", mode="charge")


def test_cycle_id_reused_across_sessions_requires_explicit_session():
    rows = [
        make_sample(0, "discharge", session="s1", seconds=0),
        make_sample(1, "discharge", session="s1", seconds=60),
        make_sample(0, "discharge", session="s2", seconds=0),
        make_sample(1, "discharge", session="s2", seconds=60),
    ]
    with pytest.raises(ValueError, match="multiple sessions"):
        integrate_capacity(rows, "cycle-1")


def test_round_trip_efficiency_compares_measured_energy_without_clipping():
    result = round_trip_efficiency(one_hour_cycle(), "cycle-1", max_gap_seconds=4000)
    assert result["charge_energy_wh"] == pytest.approx(20.0)
    assert result["discharge_energy_wh"] == pytest.approx(10.0)
    assert result["round_trip_efficiency_percent"] == pytest.approx(50.0)


def test_round_trip_efficiency_flags_ratio_above_100_without_hiding_it():
    rows = one_hour_cycle()
    rows[2]["current_a"] = 3.0
    rows[3]["current_a"] = 3.0
    result = round_trip_efficiency(rows, "cycle-1", max_gap_seconds=4000)
    assert result["round_trip_efficiency_percent"] == pytest.approx(150.0)
    assert "efficiency_above_100_percent_review" in result["review_flags"]


def test_capacity_fade_reports_descriptive_linear_trend():
    result = capacity_fade([
        {"cycle_number": 1, "capacity_ah": 10, "source_id": "cycler-a", "evidence_refs": ["test-1"], "uncertainty_ah": 0.1},
        {"cycle_number": 2, "capacity_ah": 9, "source_id": "cycler-a", "evidence_refs": ["test-2"], "uncertainty_ah": 0.1},
        {"cycle_number": 3, "capacity_ah": 8, "source_id": "cycler-b", "evidence_refs": ["test-3"], "uncertainty_ah": 0.2},
    ])
    assert result["slope_ah_per_cycle"] == pytest.approx(-1.0)
    assert result["relative_change_percent"] == pytest.approx(-20.0)
    assert result["r_squared_descriptive"] == pytest.approx(1.0)
    assert result["source_ids"] == ["cycler-a", "cycler-b"]
    assert result["evidence_refs"] == ["test-1", "test-2", "test-3"]
    assert len(result["uncertainty_ah_by_cycle"]) == 3
    assert result["extrapolation_performed"] is False


def test_capacity_fade_requires_three_unique_cycles():
    with pytest.raises(ValueError, match="three unique"):
        capacity_fade([
            {"cycle_number": 1, "capacity_ah": 10},
            {"cycle_number": 2, "capacity_ah": 9},
        ])
    with pytest.raises(ValueError, match="unique"):
        capacity_fade([
            {"cycle_number": 1, "capacity_ah": 10},
            {"cycle_number": 1, "capacity_ah": 9},
            {"cycle_number": 2, "capacity_ah": 8},
        ])


def test_temperature_excursion_counts_and_only_sums_confirmed_spans():
    rows = [
        make_sample(0, seconds=0, temperature=42),
        make_sample(1, seconds=300, temperature=41),
        make_sample(2, seconds=600, temperature=25),
    ]
    result = temperature_excursions(rows, minimum_c=0, maximum_c=40)
    assert result["above_limit_count"] == 2
    assert result["confirmed_out_of_range_span_seconds"] == pytest.approx(300)
    assert result["source_ids"] == ["sensor-source-1"]
    assert result["calibration_refs"] == ["cal-1"]
    assert result["out_of_range_sources"][0]["sample_id"] == rows[0]["sample_id"]
    assert result["safety_clearance_established"] is False


def test_temperature_excursion_rejects_inverted_limits_and_missing_data():
    with pytest.raises(ValueError, match="less than"):
        temperature_excursions([make_sample(0)], 40, 0)
    with pytest.raises(ValueError, match="at least one"):
        temperature_excursions([make_sample(0, temperature=None)], 0, 40)


def test_cell_imbalance_uses_caller_threshold_and_keeps_each_sample():
    rows = [
        make_sample(0, cells=(4.10, 4.00, 4.09)),
        make_sample(1, cells=(4.10, 4.09, 4.11)),
    ]
    result = cell_imbalance(rows, review_spread_v=0.05)
    assert result["maximum_spread_v"] == pytest.approx(0.10)
    assert result["samples"][0]["review_flag"] == "spread_above_supplied_limit"
    assert result["samples"][0]["source_id"] == "sensor-source-1"
    assert result["samples"][1]["review_flag"] is None


def test_cell_imbalance_reports_insufficient_cell_observations():
    result = cell_imbalance([make_sample(0, cells=(4.0,))], 0.1)
    assert result["samples"][0]["review_flag"] == "fewer_than_two_cell_measurements"


def test_mad_screen_flags_outlier_without_removing_observations():
    rows = [make_sample(i, current=value) for i, value in enumerate([1, 1, 1, 1, 10])]
    result = detect_signal_anomalies(rows, fields=("current_a",))
    assert [item["sample_id"] for item in result["anomalies"]] == [rows[-1]["sample_id"]]
    assert result["anomalies"][0]["source_id"] == "sensor-source-1"
    assert result["source_observations_removed"] == 0


def test_mad_screen_marks_small_samples_as_insufficient():
    result = detect_signal_anomalies([make_sample(0)], fields=("current_a",))
    assert result["fields"][0]["status"] == "insufficient_samples"


def test_protocol_comparison_reports_added_removed_and_changed_paths():
    previous = {"limits": {"minimum": 0, "maximum": 40}, "sample_rate_hz": 10, "removed": True}
    current = {"limits": {"minimum": 0, "maximum": 38}, "sample_rate_hz": 20, "new_field": "review"}
    result = compare_protocols(previous, current)
    assert result["added_paths"] == ["new_field"]
    assert result["removed_paths"] == ["removed"]
    assert [item["path"] for item in result["changed_paths"]] == ["limits.maximum", "sample_rate_hz"]
    assert result["same_revision"] is False


def test_protocol_comparison_is_deterministic_for_key_order():
    assert compare_protocols({"b": 2, "a": 1}, {"a": 1, "b": 2})["same_revision"] is True


def test_protocol_comparison_rejects_non_string_keys():
    with pytest.raises(ValueError, match="protocol keys"):
        compare_protocols({"valid": 1}, {1: "invalid"})


def test_evidence_packet_is_deterministic_and_retains_provenance():
    rows = [make_sample(0)]
    protocol = {"version": 1, "cutoff": 42}
    metrics = {"capacity_ah": 1.2, "review": "pending"}
    first = build_evidence_packet(rows, protocol, metrics, ["cal-1"])
    second = build_evidence_packet(rows, protocol, metrics, ["cal-1"])
    assert first == second
    assert first["source_ids"] == ["sensor-source-1"]
    assert first["calibration_refs"] == ["cal-1"]
    assert first["unresolved_calibration_refs"] == []
    assert first["release_authorized"] is False
    assert verify_evidence_packet(first, rows)["valid"] is True


def test_evidence_packet_reports_unresolved_calibration_references():
    packet = build_evidence_packet([make_sample(0)], {}, {}, [])
    assert packet["unresolved_calibration_refs"] == ["cal-1"]


def test_evidence_packet_verifier_detects_manifest_tampering():
    packet = build_evidence_packet([make_sample(0)], {}, {})
    packet["metrics"]["capacity_ah"] = 999
    result = verify_evidence_packet(packet)
    assert result["valid"] is False
    assert "packet_digest_mismatch" in result["issues"]


def test_evidence_packet_verifier_detects_changed_source_samples():
    rows = [make_sample(0)]
    packet = build_evidence_packet(rows, {}, {})
    changed = [make_sample(0, current=2.0)]
    result = verify_evidence_packet(packet, changed)
    assert result["valid"] is False
    assert "source_sample_digest_mismatch" in result["issues"]


def test_evidence_packet_rejects_empty_samples():
    with pytest.raises(ValueError, match="at least one"):
        build_evidence_packet([], {}, {})

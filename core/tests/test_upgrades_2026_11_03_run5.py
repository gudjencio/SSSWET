import pytest
from ssswet_core.sample_size import estimate_mean
from ssswet_core.multiple_testing import adjust
from ssswet_core.calibration_metrics import evaluate
from ssswet_core.missingness_analysis import analyze
from ssswet_core.outlier_review import flag_iqr
from ssswet_core.split_leakage import inspect as inspect_splits
from ssswet_core.preregistration import freeze
from ssswet_core.privacy_minimization import audit_fields
from ssswet_core.dependency_scheduler import order
from ssswet_core.numeric_drift import compare

def test_sample_size_is_rounded_up_and_explicit():
    result = estimate_mean(standard_deviation=10, margin_of_error=2)
    assert result["required_sample_size"] == 97
    assert result["finite_population_correction_applied"] is False

def test_multiple_testing_preserves_input_order_and_monotonicity():
    assert adjust([0.01, 0.04, 0.03], "holm") == pytest.approx([0.03, 0.06, 0.06])

def test_calibration_metrics_count_every_observation():
    result = evaluate([0.1, 0.9, 1.0], [0, 1, 1], bins=2)
    assert result["count"] == 3
    assert result["brier_score"] == pytest.approx(0.0066666667)

def test_missingness_profile_does_not_modify_rows():
    rows = [{"a": 1}, {"a": None, "b": 2}]
    result = analyze(rows)
    assert result["columns"]["a"]["missing_count"] == 1
    assert result["incomplete_row_count"] == 1
    assert rows == [{"a": 1}, {"a": None, "b": 2}]

def test_outliers_are_flagged_not_removed():
    result = flag_iqr([1, 2, 3, 4, 100])
    assert result["flagged_count"] == 1
    assert result["observations_removed"] == 0

def test_split_overlap_is_detected():
    result = inspect_splits({"train": [{"id": "a"}], "test": [{"id": "a"}]})
    assert result["leakage_detected"] and result["overlap_count"] == 1

def test_preregistration_fingerprint_is_stable():
    plan = {"research_question": "Q", "hypotheses": "H", "primary_outcome": "O", "method": "M", "analysis_plan": "A", "stopping_rule": "S"}
    assert freeze(plan)["fingerprint"] == freeze(dict(reversed(list(plan.items()))))["fingerprint"]

def test_privacy_audit_checks_names_without_reading_values():
    result = audit_fields(["email_address", "measurement", "gps_latitude"])
    assert result["flagged_count"] == 2 and result["values_inspected"] is False

def test_dependency_order_is_stable_and_detects_cycles():
    assert order([{"id": "b", "depends_on": ["a"]}, {"id": "a"}])["order"] == ["a", "b"]
    cycle = order([{"id": "a", "depends_on": ["b"]}, {"id": "b", "depends_on": ["a"]}])
    assert not cycle["valid"] and cycle["cycle_members"] == ["a", "b"]

def test_numeric_drift_is_measured_without_causal_claims():
    result = compare({"x": [1, 2, 3]}, {"x": [10, 11, 12]})
    assert result["shifted_feature_count"] == 1 and result["causal_change_inferred"] is False

def test_virtual_time_confidence_thresholds_are_conservative():
    from ssswet_core.virtual_time_confidence import assess
    assert assess([{"source_id": "s", "timestamp": "1"}] * 10)["label"] == "medium"
    assert assess([{"source_id": "s", "timestamp": str(i)} for i in range(20)])["label"] == "high"

def test_invalid_inputs_are_rejected():
    with pytest.raises(ValueError): adjust([0.1, 1.2])
    with pytest.raises(ValueError): evaluate([0.1], [2])
    with pytest.raises(ValueError): inspect_splits({"train": [{"id": "x"}], "test": [{"id": "x"}], "extra": []}, max_records=1)

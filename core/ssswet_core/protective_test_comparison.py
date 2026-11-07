"""Compare protective-equipment test records only under matching conditions.

This is a comparability aid, not a certification, safety rating or pass/fail gate.
"""
from __future__ import annotations
from math import isfinite
from statistics import mean, stdev

MAX_RECORDS = 500
_UNITS = {
    "Pa": ("pressure", 1.0), "kPa": ("pressure", 1000.0), "MPa": ("pressure", 1_000_000.0),
    "J": ("energy", 1.0), "kJ": ("energy", 1000.0),
    "m": ("length", 1.0), "cm": ("length", 0.01), "mm": ("length", 0.001),
    "N": ("force", 1.0), "kN": ("force", 1000.0),
}
_REQUIRED = ("test_id", "test_method", "configuration", "conditioning", "orientation", "metric", "unit", "value", "replicates", "source_ref")

def _finite(value, field, *, minimum=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError(f"{field} must be finite")
    if minimum is not None and value < minimum:
        raise ValueError(f"{field} must be at least {minimum}")
    return float(value)

def compare_protective_tests(records: list[dict]) -> dict:
    if not isinstance(records, list) or len(records) > MAX_RECORDS:
        raise ValueError(f"records must be a list of at most {MAX_RECORDS} tests")
    groups, seen = {}, set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError("each test record must be an object")
        missing = [field for field in _REQUIRED if field not in record]
        if missing:
            raise ValueError(f"test record {index} is missing: {', '.join(missing)}")
        test_id = record["test_id"]
        if not isinstance(test_id, str) or not test_id.strip() or test_id in seen:
            raise ValueError("test_id values must be unique non-empty strings")
        seen.add(test_id)
        for field in ("test_method", "configuration", "conditioning", "orientation", "metric", "source_ref"):
            if not isinstance(record[field], str) or not record[field].strip():
                raise ValueError(f"{field} must be non-empty text")
        unit = record["unit"]
        if unit not in _UNITS:
            raise ValueError(f"unsupported unit: {unit}")
        dimension, factor = _UNITS[unit]
        value = _finite(record["value"], "value") * factor
        uncertainty_declared = "uncertainty" in record and record["uncertainty"] is not None
        uncertainty = _finite(record["uncertainty"], "uncertainty", minimum=0) * factor if uncertainty_declared else None
        replicates = record["replicates"]
        if isinstance(replicates, bool) or not isinstance(replicates, int) or not 1 <= replicates <= 10000:
            raise ValueError("replicates must be an integer from 1 to 10000")
        key = (record["test_method"], record["configuration"], record["conditioning"], record["orientation"], record["metric"], dimension)
        groups.setdefault(key, []).append({
            "test_id": test_id, "value_base_unit": value,
            "uncertainty_base_unit": uncertainty, "uncertainty_declared": uncertainty_declared,
            "replicates": replicates, "source_ref": record["source_ref"],
        })
    reports = []
    for key, values in sorted(groups.items()):
        observed = [item["value_base_unit"] for item in values]
        replicate_count = sum(item["replicates"] for item in values)
        weighted_mean = sum(item["value_base_unit"] * item["replicates"] for item in values) / replicate_count if replicate_count else None
        declared = [item for item in values if item["uncertainty_declared"]]
        declared_replicates = sum(item["replicates"] for item in declared)
        weighted_uncertainty = (
            sum(item["uncertainty_base_unit"] * item["replicates"] for item in declared) / declared_replicates
            if declared_replicates else None
        )
        reports.append({
            "conditions": {
                "test_method": key[0], "configuration": key[1], "conditioning": key[2],
                "orientation": key[3], "metric": key[4], "unit_dimension": key[5],
            },
            "test_ids": [item["test_id"] for item in values],
            "source_refs": [item["source_ref"] for item in values],
            "record_count": len(values), "replicate_count": replicate_count,
            "mean_base_unit": round(weighted_mean, 8) if weighted_mean is not None else None,
            "mean_record_value_base_unit": round(mean(observed), 8) if observed else None,
            "between_record_sample_sd_base_unit": round(stdev(observed), 8) if len(observed) > 1 else None,
            "mean_declared_measurement_uncertainty_base_unit": round(weighted_uncertainty, 8) if weighted_uncertainty is not None else None,
            "uncertainty_declared_record_count": len(declared),
            "uncertainty_declared_for_all_records": len(declared) == len(values),
            "replicate_weighting_uses_reported_counts_not_raw_replicate_data": True,
            "comparable_records_present": len(values) > 1,
        })
    return {
        "groups": reports, "group_count": len(reports),
        "comparable_group_count": sum(item["comparable_records_present"] for item in reports),
        "records_compared": len(records), "unit_normalization": "SI base units within declared dimensions",
        "comparability_requires_matching_method_configuration_conditioning_orientation_metric_and_dimension": True,
        "certification_or_safety_rating_established": False, "pass_fail_decision_made": False,
    }

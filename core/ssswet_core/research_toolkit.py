"""Bounded local API dispatcher for the ten research-toolkit services."""
from __future__ import annotations
from .accessibility_contrast import audit_contrast_pairs
from .agent_benchmark import evaluate_agent_benchmark
from .dataset_drift import compare_dataset_summaries
from .locale_fallback import resolve_locale
from .memory_retrieval import rank_memories, evaluate_retrieval, benchmark_retrieval
from .protective_test_comparison import compare_protective_tests
from .protocol_quality import assess_protocol_quality
from .rescue_inventory import plan_fresh_inventory
from .spatiotemporal_mapping import SpatialObservation, segment_track, interpolate_between
from .storage_health import inspect_sqlite

TOOLKIT_OPERATIONS = {
    "memory_retrieval": "Bounded, provenance-preserving search and labelled retrieval evaluation.",
    "agent_benchmark": "Reviewer-scored, versioned capability benchmark with calibration metrics.",
    "dataset_drift": "Aggregate-only numeric and categorical distribution drift review.",
    "spatiotemporal_track": "GPS quality segmentation and bounded interpolation between observations.",
    "rescue_inventory": "Expiry-, inspection- and quarantine-aware civil-rescue stock planning.",
    "protective_test_comparison": "Condition-matched protective-equipment test comparability.",
    "protocol_quality": "Structured preregistration completeness review.",
    "storage_health": "Read-only SQLite health and integrity diagnostics.",
    "accessibility_contrast": "WCAG contrast checks for explicit rendered color pairs.",
    "locale_resolve": "BCP-47 locale fallback and text-direction resolution.",
}

def toolkit_catalogue() -> dict:
    return {"operations": TOOLKIT_OPERATIONS, "operation_count": len(TOOLKIT_OPERATIONS),
            "local_only": True, "mutates_research_records": False, "scientific_validity_established": False}

def execute_toolkit(payload: dict, *, database_path=None) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("payload must be a JSON object")
    operation = payload.get("tool")
    if operation not in TOOLKIT_OPERATIONS:
        raise ValueError("unknown research-toolkit operation")
    if operation == "memory_retrieval":
        if payload.get("mode", "search") == "evaluate":
            return evaluate_retrieval(payload.get("cases"), k=payload.get("k", 10))
        records, queries = payload.get("records"), payload.get("queries")
        if isinstance(queries, list):
            return benchmark_retrieval(records, queries, repeats=payload.get("repeats", 5), limit=payload.get("limit", 20))
        return rank_memories(records, payload.get("query", ""), limit=payload.get("limit", 20))
    if operation == "agent_benchmark":
        return evaluate_agent_benchmark(benchmark_id=payload.get("benchmark_id", ""), version=payload.get("version", ""),
                                       cases=payload.get("cases"), reviews=payload.get("reviews", []))
    if operation == "dataset_drift":
        return compare_dataset_summaries(payload.get("baseline"), payload.get("current"),
            numeric_shift_threshold=payload.get("numeric_shift_threshold", 0.5),
            categorical_js_threshold=payload.get("categorical_js_threshold", 0.1))
    if operation == "spatiotemporal_track":
        observations = [SpatialObservation(**item) for item in payload.get("observations", [])]
        if payload.get("interpolation"):
            interpolation = payload["interpolation"]
            left, right = SpatialObservation(**interpolation["left"]), SpatialObservation(**interpolation["right"])
            return interpolate_between(left, right, interpolation["timestamp"], max_gap_seconds=interpolation.get("max_gap_seconds", 300))
        return segment_track(observations, max_gap_seconds=payload.get("max_gap_seconds", 900),
            max_accuracy_m=payload.get("max_accuracy_m", 150), max_jump_m=payload.get("max_jump_m", 5000),
            max_speed_mps=payload.get("max_speed_mps", 70))
    if operation == "rescue_inventory":
        return plan_fresh_inventory(payload.get("lots"), payload.get("requests"), as_of=payload.get("as_of", ""),
                                    max_inspection_age_days=payload.get("max_inspection_age_days", 30))
    if operation == "protective_test_comparison":
        return compare_protective_tests(payload.get("records"))
    if operation == "protocol_quality":
        return assess_protocol_quality(payload.get("protocol"))
    if operation == "storage_health":
        if database_path is None:
            raise ValueError("local research database path is not configured")
        return inspect_sqlite(database_path)
    if operation == "accessibility_contrast":
        return audit_contrast_pairs(payload.get("pairs"))
    if operation == "locale_resolve":
        return resolve_locale(payload.get("requested", ""), payload.get("available"), fallback=payload.get("fallback", "en"))
    raise ValueError("unknown research-toolkit operation")

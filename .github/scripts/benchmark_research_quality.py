"""Bounded performance probes for the research workflow utilities.

Run from the repository root: python .github/scripts/benchmark_research_quality.py
Synthetic workloads are regression probes, not scientific or intelligence evaluations.
"""
from __future__ import annotations
import json
import math
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "core"))

from ssswet_core.localization_quality import audit_translation_catalogue  # noqa: E402
from ssswet_core.provenance_graph import build as build_graph  # noqa: E402
from ssswet_core.virtual_time_mapping import TemporalObservation, VirtualTimeMap  # noqa: E402
from ssswet_core.dataset_governance import (  # noqa: E402
    assess_consent_scope, assess_license_use, audit_field_release_policy,
    audit_group_time_splits, audit_lineage_graph, build_release_manifest,
    build_release_readiness, compare_dataset_schemas, plan_retention_reviews,
    screen_aggregate_disclosure,
)


def measure(function, repeats: int = 5) -> dict:
    samples = []
    for _ in range(repeats):
        started = time.perf_counter()
        function()
        samples.append((time.perf_counter() - started) * 1000)
    ordered = sorted(samples)
    p95 = ordered[min(len(ordered) - 1, math.ceil(len(ordered) * 0.95) - 1)]
    return {"median_ms": round(statistics.median(samples), 3), "p95_ms": round(p95, 3), "samples": repeats}


def main() -> None:
    nodes = [{"id": f"n{index:04d}"} for index in range(1200)]
    edges = [(f"n{index:04d}", f"n{index + 1:04d}") for index in range(1199)]
    graph = measure(lambda: build_graph(nodes, edges))
    assert graph["p95_ms"] < 2000

    mapping = VirtualTimeMap()
    for index in range(1500):
        mapping.add(TemporalObservation(
            f"2026-01-01T00:{index // 60:02d}:{index % 60:02d}Z",
            f"observation-{index}", f"source-{index}", 2.0,
        ))
    temporal = measure(mapping.temporal_clusters)
    assert temporal["p95_ms"] < 2000

    source = {f"key-{index:03d}": f"Research label {index} {{value}}" for index in range(300)}
    translations = {
        language: {key: f"{language.upper()} label {index} {{value}}" for index, key in enumerate(source)}
        for language in ("en", "fr", "es", "pt", "it", "de", "nl", "ja", "ko", "zh", "gcf", "ku", "da", "sv", "jv")
    }
    translations["en"] = source
    locale = measure(lambda: audit_translation_catalogue(source, translations))
    assert locale["p95_ms"] < 2000

    legacy_dataset_record = {
        "dataset_id": "benchmark-dataset", "version": 1, "title": "Sample",
        "description": "Synthetic metadata record", "campaign_id": "benchmark",
        "license": "CC-BY-4.0", "source_ids": ["source-1"],
    }
    governed_dataset_record = {
        **legacy_dataset_record, "privacy_classification": "public",
        "consent_status": "not_required", "retention_policy": "review annually",
        "access_scope": "public",
    }
    legacy_bytes = len(json.dumps(legacy_dataset_record, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    governed_bytes = len(json.dumps(governed_dataset_record, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    metadata_delta = governed_bytes - legacy_bytes

    license_policy = {"license_id": "CC-BY-4.0", "review_status": "approved", "reviewer_ref": "review:1",
                      "reviewed_at": "2026-11-10T00:00:00Z", "permitted_uses": ["research"]}
    consent = {"status": "documented", "permitted_purposes": ["research"],
               "consent_evidence_ref": "consent:1", "reviewer_ref": "review:1"}
    fields = [{"name": f"measure_{i}", "classification": "public", "release_action": "include"} for i in range(1000)]
    cells = [{"cell_id": f"c{i}", "group_id": f"g{i // 10}", "count": (i % 30) + 1} for i in range(10000)]
    old_schema = {f"f{i}": {"type": "number", "nullable": True, "required": False} for i in range(1000)}
    new_schema = {**old_schema, "added": {"type": "string", "nullable": True, "required": False}}
    governance_nodes = [{"id": f"n{i:05d}"} for i in range(5000)]
    governance_edges = [{"from": "n00000", "to": f"n{i:05d}"} for i in range(1, 5000)]
    splits = {"train": [], "validation": [], "test": []}
    for index in range(30000):
        split = "train" if index < 10000 else "validation" if index < 20000 else "test"
        month = 1 if split == "train" else 2 if split == "validation" else 3
        splits[split].append({"group": f"g{index}", "when": f"2026-{month:02d}-01T00:00:00Z"})
    retention = [{"dataset_id": f"d{i}", "retention_start": "2025-01-01", "retention_days": 365,
                  "policy_ref": "policy:1"} for i in range(5000)]
    readiness_inputs = {name: {"policy_gate_passed": True} for name in (
        "license", "consent", "field_privacy", "disclosure", "schema", "lineage", "split_integrity", "retention")}
    readiness = build_release_readiness(readiness_inputs)
    manifest_args = {
        "dataset_id": "benchmark", "dataset_version": 1, "schema_digest": "a" * 64,
        "artifact_digests": {f"artifact-{i}": "b" * 64 for i in range(100)},
        "source_refs": [f"source:{i}" for i in range(100)],
        "review_refs": [f"review:{i}" for i in range(100)],
        "readiness_report": readiness, "software_version": "0.2.0",
    }
    governance_workloads = {
        "license_policy": lambda: assess_license_use(license_policy, "research"),
        "consent_scope": lambda: assess_consent_scope(consent, "research"),
        "field_privacy_1000": lambda: audit_field_release_policy(fields),
        "aggregate_disclosure_10000": lambda: screen_aggregate_disclosure(cells),
        "schema_diff_1000": lambda: compare_dataset_schemas(old_schema, new_schema),
        "lineage_5000": lambda: audit_lineage_graph(governance_nodes, governance_edges),
        "group_time_splits_30000": lambda: audit_group_time_splits(
            splits, group_field="group", time_field="when", split_order=["train", "validation", "test"]
        ),
        "retention_5000": lambda: plan_retention_reviews(retention, "2026-11-10"),
        "release_readiness": lambda: build_release_readiness(readiness_inputs),
        "manifest_100_artifacts": lambda: build_release_manifest(**manifest_args),
    }
    governance = {name: measure(function) for name, function in governance_workloads.items()}
    for name, result in governance.items():
        assert result["p95_ms"] < 5000, f"{name} exceeded the 5000 ms p95 guard"

    print(json.dumps({
        "workloads": {
            "provenance_graph": {"nodes": len(nodes), "edges": len(edges), **graph},
            "temporal_mapping": {"observations": 1500, **temporal},
            "localization_audit": {"source_keys": len(source), "locales": len(translations), **locale},
            "dataset_governance": governance,
        },
        "dataset_governance_metadata": {
            "legacy_json_bytes": legacy_bytes,
            "governed_json_bytes": governed_bytes,
            "additional_json_bytes_per_record": metadata_delta,
            "sample_only_not_a_database_measurement": True,
        },
        "acceptance_threshold_ms_p95": {"existing": 2000, "dataset_governance": 5000},
        "synthetic_benchmark_only": True,
        "scientific_validity_or_agent_intelligence_established": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()

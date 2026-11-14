#!/usr/bin/env python3
"""Repeatable latency and retention benchmark for the public-media workbench."""
from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "core"))

from ssswet_core.public_media_research_workbench import (
    build_audit_chain, cluster_exact_content, plan_intake_budget,
    prepare_public_media_batch, score_topic_relevance,
)
from ssswet_core.public_media_ingestion import normalize_public_record

REPEATS = 3
BUDGET_SECONDS = 5.0


def records_fixture():
    items = []
    for index in range(250):
        platform = "youtube" if index % 2 == 0 else "x"
        host = "https://www.youtube.com/watch?v=" if platform == "youtube" else "https://x.com/post/"
        text_field = "title" if platform == "youtube" else "text"
        items.append({
            "platform": platform, "visibility": "public",
            "access_mode": "official_api", "source_url": host + str(index),
            "captured_at": "2026-11-14T08:00:00+00:00",
            "provider_item_id": f"item-{index:04d}",
            "content_type": "video" if platform == "youtube" else "post",
            "metadata": {
                text_field: f"Materials science research record {index}",
                "language": "en", "captions_available": index % 2 == 0,
            },
        })
    return items


def workloads():
    records = records_fixture()
    normalized = [normalize_public_record(item) for item in records]
    events = [{
        "event_id": f"event-{index:04d}", "event_type": "captured",
        "record_id": f"source-{index:04d}",
        "occurred_at": "2026-11-14T08:00:00+00:00",
        "payload_sha256": "a" * 64,
    } for index in range(250)]
    return records, normalized, events, [
        ("batch_intake_250", lambda: prepare_public_media_batch(records, "materials science research")),
        ("exact_dedup_250", lambda: cluster_exact_content(normalized)),
        ("fair_budget_250", lambda: plan_intake_budget(records)),
        ("audit_chain_250", lambda: build_audit_chain(events)),
    ]


def main():
    results = []
    records, normalized, events, measured_workloads = workloads()
    for name, workload in measured_workloads:
        durations, measurement = [], None
        for _ in range(REPEATS):
            started = time.perf_counter()
            measurement = workload()
            durations.append(time.perf_counter() - started)
        maximum = max(durations)
        if "manifest_sha256" in measurement:
            output_count = len(measurement["records"])
        elif "source_count" in measurement:
            output_count = measurement["source_count"]
        elif "selected_record_count" in measurement:
            output_count = measurement["selected_record_count"]
        else:
            output_count = measurement["event_count"]
        results.append({
            "workload": name, "repeats": REPEATS,
            "median_ms": round(statistics.median(durations) * 1000, 3),
            "maximum_ms": round(maximum * 1000, 3),
            "budget_ms": int(BUDGET_SECONDS * 1000),
            "within_budget": maximum <= BUDGET_SECONDS,
            "output_count": output_count,
            "measurement": "synthetic metadata only; no network or media download",
        })
    # Controlled relevance fixture: 50 relevant records, 50 one-token near-misses,
    # and 150 unrelated records. This measures deterministic retrieval behavior
    # on a known fixture, not real-world semantic relevance.
    relevance_records = []
    expected_relevant = set()
    for index, item in enumerate(records):
        copied = json.loads(json.dumps(item))
        field = "title" if copied["platform"] == "youtube" else "text"
        if index % 5 == 0:
            copied["metadata"][field] = f"Alloy fatigue thermal cycling experiment {index}"
            expected_relevant.add(f"{copied['platform']}:{copied['provider_item_id']}")
        elif index % 5 == 1:
            copied["metadata"][field] = f"Alloy maintenance announcement {index}"
        else:
            copied["metadata"][field] = f"Community event announcement {index}"
        relevance_records.append(normalize_public_record(copied))
    relevance_rows = [{
        "source_id": item["source_id"],
        "score": score_topic_relevance(item, "alloy fatigue thermal cycling")["lexical_overlap_score"],
    } for item in relevance_records]
    relevance_rows.sort(key=lambda row: (-row["score"], row["source_id"]))
    top_k = len(expected_relevant)
    retrieved = {row["source_id"] for row in relevance_rows[:top_k]}
    true_positives = len(retrieved & expected_relevant)
    precision_at_k = true_positives / top_k if top_k else 0.0
    recall_at_k = true_positives / len(expected_relevant) if expected_relevant else 0.0

    dedup = cluster_exact_content(normalized)
    retained_ids = set(dedup["unclustered_source_ids"])
    for cluster in dedup["clusters"]:
        retained_ids.update(member["source_id"] for member in cluster["members"])
    provenance_retention = len(retained_ids) / len(normalized) if normalized else 1.0

    chain_125 = build_audit_chain(events[:125])
    chain_250 = build_audit_chain(events)
    bytes_125 = len(json.dumps(chain_125, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    bytes_250 = len(json.dumps(chain_250, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    quality_and_retention = {
        "synthetic_retrieval_fixture": {
            "known_relevant_records": len(expected_relevant),
            "precision_at_k": round(precision_at_k, 4),
            "recall_at_k": round(recall_at_k, 4),
            "k": top_k,
            "semantic_accuracy_established": False,
        },
        "provenance_retention": {
            "input_records": len(normalized),
            "retained_source_ids": len(retained_ids),
            "retention_rate": round(provenance_retention, 4),
            "records_merged_or_deleted": False,
        },
        "audit_serialized_storage": {
            "events_125_bytes": bytes_125,
            "events_250_bytes": bytes_250,
            "bytes_per_event_at_250": round(bytes_250 / 250, 2),
            "growth_ratio_125_to_250": round(bytes_250 / bytes_125, 4) if bytes_125 else None,
            "heap_or_database_size_measured": False,
        },
        "contradiction_adjudication": False,
    }
    print(json.dumps({
        "benchmark": "SSSWET public media research workbench",
        "results": results,
        "quality_and_retention": quality_and_retention,
        "retention_note": "Audit chain is bounded at 1000 events; benchmark stores no raw media.",
    }, indent=2))
    if precision_at_k < 0.95 or recall_at_k < 0.95 or provenance_retention < 1.0:
        raise SystemExit("Synthetic retrieval or provenance-retention acceptance threshold failed")
    failed = [item["workload"] for item in results if not item["within_budget"]]
    if failed:
        raise SystemExit("Latency budget exceeded: " + ", ".join(failed))


if __name__ == "__main__":
    main()

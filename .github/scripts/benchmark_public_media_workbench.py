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
    prepare_public_media_batch,
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
    return [
        ("batch_intake_250", lambda: prepare_public_media_batch(records, "materials science research")),
        ("exact_dedup_250", lambda: cluster_exact_content(normalized)),
        ("fair_budget_250", lambda: plan_intake_budget(records)),
        ("audit_chain_250", lambda: build_audit_chain(events)),
    ]


def main():
    results = []
    for name, workload in workloads():
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
    print(json.dumps({
        "benchmark": "SSSWET public media research workbench",
        "results": results,
        "retention_note": "Audit chain is bounded at 1000 events; benchmark stores no raw media.",
    }, indent=2))
    failed = [item["workload"] for item in results if not item["within_budget"]]
    if failed:
        raise SystemExit("Latency budget exceeded: " + ", ".join(failed))


if __name__ == "__main__":
    main()

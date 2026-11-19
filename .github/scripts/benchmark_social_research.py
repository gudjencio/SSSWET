"""Synthetic benchmark for bounded social discovery and bibliographic review."""
from __future__ import annotations

import json
import statistics
import time

from ssswet_core.bibliographic_integrity import analyze_bibliographic_integrity
from ssswet_core.social_research import SocialItem, query_relevance, triage_social_item


def measure(fn, repeats=7):
    values = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        values.append((time.perf_counter() - start) * 1000)
    ordered = sorted(values)
    return {
        "median_ms": round(statistics.median(ordered), 3),
        "p95_ms": round(ordered[min(len(ordered) - 1, int(0.95 * len(ordered)))], 3),
    }


def main():
    items = [
        SocialItem(
            "bluesky", f"bluesky:{i}", f"Battery research {i}",
            "Experimental measurements and reproducibility",
            f"https://bsky.app/profile/lab.example/post/{i}",
            metadata={"language": "en"},
        )
        for i in range(250)
    ]
    records = [
        {
            "source_id": f"source:{i}", "title": f"Battery paper {i}",
            "doi": f"10.1000/example-{i}", "year": 2020 + i % 6,
            "authors": ["Researcher"], "venue": "Journal",
        }
        for i in range(500)
    ]
    results = {
        "schema_version": 1,
        "synthetic_only": True,
        "workloads": {
            "query_relevance_250": measure(lambda: [
                query_relevance("battery research", item.title + " " + item.text) for item in items
            ]),
            "triage_250": measure(lambda: [triage_social_item(item) for item in items]),
            "bibliographic_integrity_500": measure(lambda: analyze_bibliographic_integrity(records)),
        },
        "limitations": [
            "Synthetic microbenchmarks are not production latency or provider-availability guarantees.",
            "No scientific accuracy or misinformation-classification accuracy is measured.",
        ],
    }
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()

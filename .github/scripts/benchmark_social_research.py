"""Synthetic benchmark for bounded social discovery and bibliographic review."""
from __future__ import annotations

import json
import statistics
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "core"))

from ssswet_core.bibliographic_integrity import analyze_bibliographic_integrity
from ssswet_core.social_research import (
    SocialItem, SocialResearchProvider, query_relevance, triage_social_item,
)


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
    relevance_fixture = [
        (SocialItem("bluesky", f"relevant:{i}", f"Battery research {i}",
                    "Battery chemistry and reproducible measurements",
                    f"https://bsky.app/profile/lab.example/post/r{i}"), True)
        for i in range(100)
    ] + [
        (SocialItem("bluesky", f"irrelevant:{i}", f"Football match {i}",
                    "League standings and goalkeeper performance",
                    f"https://bsky.app/profile/sports.example/post/i{i}"), False)
        for i in range(150)
    ]
    records = [
        {
            "source_id": f"source:{i}", "title": f"Battery paper {i}",
            "doi": f"10.1000/example-{i}", "year": 2020 + i % 6,
            "authors": ["Researcher"], "venue": "Journal",
        }
        for i in range(500)
    ]

    class StaticProvider:
        def __init__(self, name, records):
            self.name, self.records = name, records
        def search(self, query):
            return self.records

    left = [
        SocialItem("bluesky", f"shared:{i}" if i < 5 else f"bluesky:{i}",
                   f"Battery research {i}", "Reproducible battery measurements",
                   f"https://bsky.app/profile/lab.example/post/{i}")
        for i in range(10)
    ]
    right = [
        SocialItem("qiita", f"shared:{i}" if i < 5 else f"qiita:{i}",
                   f"Battery research {i}", "Reproducible battery measurements",
                   f"https://qiita.com/lab/items/{i}")
        for i in range(10)
    ]
    fused_provider = SocialResearchProvider(
        [StaticProvider("bluesky-fixture", left), StaticProvider("qiita-fixture", right)],
        max_results=10,
    )

    scored = [
        (query_relevance("battery research", item.title + " " + item.text)[0] > 0, expected)
        for item, expected in relevance_fixture
    ]
    true_positive = sum(predicted and expected for predicted, expected in scored)
    false_positive = sum(predicted and not expected for predicted, expected in scored)
    false_negative = sum(not predicted and expected for predicted, expected in scored)
    precision = true_positive / max(1, true_positive + false_positive)
    recall = true_positive / max(1, true_positive + false_negative)
    fused_items, fused_errors = fused_provider.search("battery research")
    platform_counts = {}
    for item in fused_items:
        platform_counts[item.platform] = platform_counts.get(item.platform, 0) + 1
    if precision != 1.0 or recall != 1.0 or len(fused_items) != 10:
        raise SystemExit("Synthetic relevance or provider-fusion acceptance check failed.")
    if len({item.source_id for item in fused_items}) != len(fused_items) or len(platform_counts) < 2:
        raise SystemExit("Synthetic deduplication or platform-diversity acceptance check failed.")

    workloads = {
        "query_relevance_250": measure(lambda: [
            query_relevance("battery research", item.title + " " + item.text) for item in items
        ]),
        "triage_250": measure(lambda: [triage_social_item(item) for item in items]),
        "bibliographic_integrity_500": measure(lambda: analyze_bibliographic_integrity(records)),
        "provider_fusion_15": measure(lambda: fused_provider.search("battery research")),
    }
    budgets = {
        "query_relevance_250": 500.0,
        "triage_250": 500.0,
        "bibliographic_integrity_500": 1000.0,
        "provider_fusion_15": 1000.0,
    }
    for name, result in workloads.items():
        if result["p95_ms"] > budgets[name]:
            raise SystemExit(f"{name} exceeded p95 budget: {result['p95_ms']} ms > {budgets[name]} ms")
    results = {
        "schema_version": 1,
        "synthetic_only": True,
        "budgets_p95_ms": budgets,
        "workloads": workloads,
        "synthetic_retrieval_quality": {
            "candidate_count": len(relevance_fixture),
            "relevant_candidates": sum(expected for _, expected in relevance_fixture),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "provider_fusion_results": len(fused_items),
            "unique_source_ids": len({item.source_id for item in fused_items}),
            "platform_counts": platform_counts,
            "feed_errors": list(fused_errors),
            "all_results_have_https_source_urls": all(item.url.startswith("https://") for item in fused_items),
        },
        "limitations": [
            "Synthetic microbenchmarks are not production latency or provider-availability guarantees.",
            "No scientific accuracy or misinformation-classification accuracy is measured.",
        ],
    }
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()

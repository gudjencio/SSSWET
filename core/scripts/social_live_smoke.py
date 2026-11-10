"""Live, read-only smoke checks for public multilingual social discovery.

This script intentionally uses only public Bluesky and Qiita endpoints. It
stores bounded metadata (not full post/article bodies) in a JSON report.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys

# Make the core package importable when this file is executed directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ssswet_core.social_expansion import BlueskySearchProvider, QiitaSearchProvider

QUERIES = {
    "en": "battery",
    "fr": "batterie",
    "ja": "全固体電池",
    "zh": "固态电池",
}


def main() -> int:
    providers = (
        ("bluesky", BlueskySearchProvider(max_results=5)),
        ("qiita", QiitaSearchProvider(max_results=5)),
    )
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "public_read_only_smoke_test",
        "queries": {},
        "limitations": [
            "A successful API response does not establish scientific validity.",
            "No private content, scraping, login automation, or transcript access is used.",
            "Zero matches for a query are not considered an API failure.",
            "Only bounded public metadata is retained in this report.",
        ],
    }
    successful_requests = 0
    failed_requests = 0
    for language, query in QUERIES.items():
        report["queries"][language] = {"query": query, "providers": {}}
        for name, provider in providers:
            entry = {"status": "ok", "count": 0, "items": []}
            try:
                items = provider.search(query)
                successful_requests += 1
                entry["count"] = len(items)
                entry["items"] = [
                    {
                        "platform": item.platform,
                        "source_id": item.source_id[:220],
                        "title": item.title[:300],
                        "url": item.url[:1500],
                        "author": item.author[:120],
                        "published_at": item.published_at[:40],
                        "language_hint": str(item.metadata.get("language") or "")[:12],
                        "triage": "not_verified",
                    }
                    for item in items[:5]
                ]
            except Exception as exc:  # report provider outages without leaking credentials
                failed_requests += 1
                entry["status"] = "error"
                entry["error"] = type(exc).__name__
                entry["detail"] = str(exc)[:180]
            report["queries"][language]["providers"][name] = entry

    report["summary"] = {
        "successful_requests": successful_requests,
        "failed_requests": failed_requests,
        "languages_tested": list(QUERIES),
        "providers_tested": [name for name, _ in providers],
    }
    output = Path("social-live-smoke-report.json")
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False))
    # Partial platform outages remain visible in the artifact. Fail only when
    # every attempted request failed, so one provider cannot mask the other.
    return 1 if successful_requests == 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())

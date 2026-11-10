"""Live, read-only smoke checks for public multilingual social discovery."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ssswet_core.social_expansion import BlueskySearchProvider, QiitaSearchProvider

QUERIES = {
    "en": {"query": "solid-state battery", "terms": ("solid-state battery", "solid state battery")},
    "fr": {"query": "batterie à l'état solide", "terms": ("batterie à l'état solide", "batterie solide")},
    "ja": {"query": "全固体電池", "terms": ("全固体電池",)},
    "zh": {"query": "固态电池", "terms": ("固态电池",)},
}


def main() -> int:
    providers = (
        ("bluesky", BlueskySearchProvider(max_results=3)),
        ("qiita", QiitaSearchProvider(max_results=1)),
    )
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "public_read_only_smoke_test",
        "queries": {},
        "limitations": [
            "A successful API response does not establish scientific validity.",
            "Only public content is queried; no scraping or login automation is used.",
            "Zero relevant matches are not considered an API failure.",
            "Results are filtered by literal topic terms and are not a scientific quality assessment.",
            "Only bounded public metadata is retained in this report.",
        ],
    }
    successful_requests = failed_requests = 0
    for language, config in QUERIES.items():
        query = config["query"]
        terms = tuple(term.casefold() for term in config["terms"])
        report["queries"][language] = {"query": query, "providers": {}}
        for name, provider in providers:
            entry = {"status": "ok", "count": 0, "raw_count": 0, "items": []}
            try:
                items = provider.search(query)
                successful_requests += 1
                relevant = [
                    item for item in items
                    if any(term in (item.title + " " + item.text).casefold() for term in terms)
                ]
                entry["raw_count"] = len(items)
                entry["count"] = len(relevant)
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
                    for item in relevant[:3]
                ]
            except Exception as exc:
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
    Path("social-live-smoke-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report["summary"], ensure_ascii=False))
    return 1 if successful_requests == 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())

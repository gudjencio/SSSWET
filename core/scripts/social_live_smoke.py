"""Live, read-only smoke checks for multilingual scholarly and social discovery."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ssswet_core.providers import MultiSourceLiteratureProvider
from ssswet_core.social_expansion import BlueskySearchProvider, QiitaSearchProvider

QUERIES = {
    "en": "solid-state battery",
    "fr": "batterie à l'état solide",
    "ja": "全固体電池",
    "zh": "固态电池",
}


def main() -> int:
    social_providers = (
        ("bluesky", BlueskySearchProvider(max_results=3)),
        ("qiita", QiitaSearchProvider(max_results=1)),
    )
    scholarly = MultiSourceLiteratureProvider(max_results=3)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "public_read_only_multilingual_smoke_test",
        "queries": {},
        "limitations": [
            "Bibliographic metadata and social posts are discovery leads, not scientific validation.",
            "Crossref and OpenAlex records must be checked against the original publication.",
            "Qiita and Bluesky are community discovery sources, not peer-reviewed literature indexes.",
            "Zero results are reported as zero results, never replaced with invented matches.",
            "Only bounded metadata and bibliographic snippets are retained; no full papers are downloaded.",
        ],
    }
    successful_requests = failed_requests = 0
    for language, query in QUERIES.items():
        report["queries"][language] = {"query": query, "providers": {}}

        try:
            result = scholarly.investigate(query, "multilingual live smoke test")
            successful_requests += 1
            report["queries"][language]["providers"]["crossref_openalex"] = {
                "status": "ok" if result.source_ids else "no_records",
                "count": len(result.source_ids),
                "records": [
                    {
                        "source_id": source_id[:240],
                        "citation": evidence[:900],
                        "verification_status": "not_verified",
                    }
                    for source_id, evidence in zip(result.source_ids[:6], result.evidence[:6])
                ],
                "summary": result.summary[:500],
            }
        except Exception as exc:
            failed_requests += 1
            report["queries"][language]["providers"]["crossref_openalex"] = {
                "status": "error", "error": type(exc).__name__, "detail": str(exc)[:180]
            }

        for name, provider in social_providers:
            entry = {"status": "ok", "count": 0, "raw_count": 0, "items": []}
            try:
                items = provider.search(query)
                successful_requests += 1
                entry["raw_count"] = len(items)
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
                    for item in items[:3]
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
        "providers_tested": ["Crossref", "OpenAlex", "Bluesky", "Qiita"],
    }
    Path("social-live-smoke-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report["summary"], ensure_ascii=False))
    return 1 if successful_requests == 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())

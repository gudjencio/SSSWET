"""Run a one-shot scholarly metadata watch against Crossref and OpenAlex."""
from __future__ import annotations
import argparse
import json
from .literature_watch import LiteratureWatchService
from .persistence import SQLiteResearchStore
from .providers import MultiSourceLiteratureProvider


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a SSSWET scholarly metadata watch")
    parser.add_argument("--query", required=True, help="Research topic or search query")
    parser.add_argument("--database", default=".ssswet/ssswet.sqlite3")
    parser.add_argument("--mailto", default="", help="Optional contact email for scholarly APIs")
    parser.add_argument("--max-results", type=int, default=5)
    args = parser.parse_args()
    store = SQLiteResearchStore(args.database)
    provider = MultiSourceLiteratureProvider(
        max_results=max(1, min(args.max_results, 20)), mailto=args.mailto
    )
    report = LiteratureWatchService(provider, store).run(args.query)
    print(json.dumps({
        "watch_id": report.watch_id,
        "query": report.query,
        "provider": report.provider,
        "candidate_count": len(report.candidates),
        "candidates": [
            {
                "title": item.title,
                "source_id": item.source_id,
                "doi": item.doi,
                "classification": item.classification,
                "duplicate_source_ids": list(item.duplicate_source_ids),
                "similar_source_ids": list(item.similar_source_ids),
                "related_memory_ids": list(item.related_memory_ids),
                "url": item.url,
                "note": item.note,
            } for item in report.candidates
        ],
        "scientific_validity_established": False,
        "memory_changed": False,
        "campaign_changed": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

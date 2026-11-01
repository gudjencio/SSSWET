"""Execute due campaign literature-watch subscriptions once."""
from __future__ import annotations
import argparse
import json

from .campaign_literature_watch import CampaignLiteratureWatch
from .persistence import SQLiteResearchStore
from .providers import MultiSourceLiteratureProvider


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run due SSSWET campaign literature-watch subscriptions"
    )
    parser.add_argument("--database", default=".ssswet/ssswet.sqlite3")
    parser.add_argument("--mailto", default="")
    parser.add_argument("--max-results", type=int, default=5)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    store = SQLiteResearchStore(args.database)
    provider = MultiSourceLiteratureProvider(
        max_results=max(1, min(args.max_results, 20)), mailto=args.mailto
    )
    runs = CampaignLiteratureWatch(store, provider).run_due(
        limit=max(1, min(args.limit, 100))
    )
    print(json.dumps({
        "runs": [
            {
                "campaign_id": run.campaign_id,
                "query": run.query,
                "candidate_count": run.candidate_count,
                "new_candidate_ids": list(run.new_candidate_ids),
                "previously_seen_ids": list(run.previously_seen_ids),
                "error": run.error,
                "scientific_validity_established": False,
                "memory_changed": False,
                "campaign_changed": False,
            } for run in runs
        ],
        "due_subscriptions_processed": len(runs),
        "note": "This is a one-shot scheduler pass. Invoke periodically using an OS scheduler if desired.",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

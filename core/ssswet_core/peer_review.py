"""Cross-campaign peer review records with explicit independence declarations.

Reviews are immutable assessments. They do not verify, reject, or rewrite the
underlying scientific claim.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Iterable
import hashlib


REVIEW_OUTCOMES = {"supports", "challenges", "inconclusive", "unable_to_assess"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class PeerReviewRequest:
    review_id: str
    source_campaign_id: str
    node_id: str
    reviewer_campaign_ids: tuple[str, ...]
    requested_by: str
    question: str
    status: str = "open"
    created_at: str = ""
    closed_at: str = ""

    def __post_init__(self):
        required = (self.review_id, self.source_campaign_id, self.node_id,
                    self.requested_by, self.question)
        if any(not isinstance(value, str) or not value.strip() for value in required):
            raise ValueError("Review ID, source campaign, node, requester and question are required")
        if not self.reviewer_campaign_ids or len(set(self.reviewer_campaign_ids)) != len(self.reviewer_campaign_ids):
            raise ValueError("At least one unique reviewer campaign is required")
        if self.source_campaign_id in self.reviewer_campaign_ids:
            raise ValueError("Peer review must come from a different campaign")
        if self.status not in {"open", "completed", "cancelled"}:
            raise ValueError("Unsupported peer-review state")


@dataclass(frozen=True)
class PeerReviewSubmission:
    submission_id: str
    review_id: str
    reviewer_campaign_id: str
    outcome: str
    assessment: str
    method: str
    source_ids: tuple[str, ...]
    provenance_group: str
    independence_confirmed: bool = False
    limitations: str = ""
    submitted_at: str = ""

    def __post_init__(self):
        required = (self.submission_id, self.review_id, self.reviewer_campaign_id,
                    self.assessment, self.method)
        if any(not isinstance(value, str) or not value.strip() for value in required):
            raise ValueError("Submission identifiers, assessment and method are required")
        if self.outcome not in REVIEW_OUTCOMES:
            raise ValueError("Unsupported peer-review outcome")
        if not isinstance(self.independence_confirmed, bool):
            raise ValueError("Independence must be explicitly declared")
        if len(set(self.source_ids)) != len(self.source_ids) or any(not item.strip() for item in self.source_ids):
            raise ValueError("Source identifiers must be unique and non-empty")


class PeerReviewService:
    def __init__(self, store):
        self.store = store

    def request(
        self, review_id: str, source_campaign_id: str, node_id: str,
        reviewer_campaign_ids: Iterable[str], requested_by: str, question: str,
    ) -> dict:
        request = PeerReviewRequest(
            review_id, source_campaign_id, node_id,
            tuple(reviewer_campaign_ids), requested_by, question,
            created_at=_now(),
        )
        return self.store.create_peer_review_request(request)

    def submit(
        self, submission_id: str, review_id: str, reviewer_campaign_id: str,
        outcome: str, assessment: str, method: str, *,
        source_ids: Iterable[str] = (), provenance_group: str = "",
        independence_confirmed: bool, limitations: str = "",
    ) -> dict:
        submission = PeerReviewSubmission(
            submission_id, review_id, reviewer_campaign_id, outcome,
            assessment, method, tuple(source_ids), provenance_group,
            independence_confirmed, limitations, _now(),
        )
        return self.store.add_peer_review_submission(submission)

    def report(self, limit: int = 200) -> dict:
        cases = self.store.peer_review_history(limit=limit)
        for case in cases:
            submissions = case.get("submissions", [])
            case["submission_count"] = len(submissions)
            outcomes = [item["outcome"] for item in submissions]
            outcome_counts = {
                outcome: outcomes.count(outcome)
                for outcome in sorted(REVIEW_OUTCOMES)
            }
            source_usage: dict[str, int] = {}
            provenance_usage: dict[str, int] = {}
            for item in submissions:
                for source_id in item.get("source_ids", []):
                    source_usage[source_id] = source_usage.get(source_id, 0) + 1
                provenance = item.get("provenance_group", "").strip()
                if provenance:
                    provenance_usage[provenance] = provenance_usage.get(provenance, 0) + 1
            repeated_sources = sorted(
                source_id for source_id, count in source_usage.items() if count > 1
            )
            repeated_provenance = sorted(
                group for group, count in provenance_usage.items() if count > 1
            )
            distinct_outcomes = sorted(set(outcomes))
            case["outcome_summary"] = outcome_counts
            case["all_reviewers_declared_independence"] = bool(submissions) and all(
                item["independence_confirmed"] for item in submissions
            )
            case["independence_independently_verified"] = False
            case["review_synthesis"] = {
                "outcome_pattern": (
                    "no_submissions" if not submissions else
                    "unanimous" if len(distinct_outcomes) == 1 else "mixed"
                ),
                "distinct_outcomes": distinct_outcomes,
                "reviewer_campaign_count": len({
                    item["reviewer_campaign_id"] for item in submissions
                }),
                "distinct_methods": sorted({
                    item["method"].strip() for item in submissions if item.get("method", "").strip()
                }),
                "shared_source_ids": repeated_sources,
                "shared_provenance_groups": repeated_provenance,
                "submissions_with_limitations": sum(
                    1 for item in submissions if item.get("limitations", "").strip()
                ),
                "interpretation": (
                    "Descriptive comparison only. Outcome patterns, reviewer declarations "
                    "and method counts do not establish independence or scientific validity."
                ),
                "majority_vote_used_for_adjudication": False,
            }
            case["scientific_validity_established"] = False
        return {
            "reviews": cases,
            "review_count": len(cases),
            "scientific_validity_established": False,
            "automatic_adjudication": False,
            "majority_vote_used_for_adjudication": False,
        }

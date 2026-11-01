"""Explainable cross-campaign collaboration recommendations.

Recommendations are review leads only. They do not create transfers, alter
campaigns, or change the verification state of knowledge graph nodes.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import re
import uuid
from datetime import datetime, timezone

from .collaboration import create_transfer


_STOP = {
    "the", "and", "for", "with", "from", "this", "that", "into", "using",
    "les", "des", "une", "pour", "dans", "avec", "sur", "par", "aux",
    "and", "the", "of", "to", "in", "on", "de", "du", "la", "le",
}


def _terms(value: str) -> set[str]:
    return {
        token for token in re.findall(r"[\w-]{3,}", value.casefold())
        if token not in _STOP
    }


@dataclass(frozen=True)
class CollaborationRecommendation:
    recommendation_id: str
    source_campaign_id: str
    target_campaign_id: str
    node_id: str
    node_label: str
    target_campaign_title: str
    score: float
    matched_terms: tuple[str, ...]
    rationale: str
    verification_state: str
    requires_human_review: bool = True
    transfer_created: bool = False


class CollaborationRecommender:
    """Find active campaigns whose stated objectives overlap a campaign node."""

    def __init__(self, store: object):
        self.store = store

    def recommend(
        self, *, source_campaign_id: str | None = None,
        min_score: float = 0.15, limit: int = 100,
    ) -> list[CollaborationRecommendation]:
        if not 0.0 <= min_score <= 1.0:
            raise ValueError("min_score must be between 0 and 1")
        bounded_limit = max(1, min(int(limit), 500))
        campaigns = self.store.campaign_history(limit=500)
        by_id = {item["campaign_id"]: item for item in campaigns}
        nodes = self.store.knowledge_graph(limit=2000)["nodes"]
        transfers = self.store.knowledge_transfer_history(limit=500)
        already_pending = {
            (item["node_id"], item["target_campaign_id"])
            for item in transfers if item.get("state") == "pending"
        }
        recommendations = []
        for node in nodes:
            metadata = node.get("metadata") or {}
            source_id = metadata.get("campaign_id")
            if not source_id or source_id not in by_id:
                continue
            if source_campaign_id and source_id != source_campaign_id:
                continue
            source = by_id[source_id]
            if source.get("state") != "active":
                continue
            node_text = " ".join((
                node.get("label", ""), node.get("description", ""),
                metadata.get("topic", ""), metadata.get("domain", ""),
            ))
            node_terms = _terms(node_text)
            if not node_terms:
                continue
            for target in campaigns:
                target_id = target["campaign_id"]
                if target_id == source_id or target.get("state") != "active":
                    continue
                if (node["node_id"], target_id) in already_pending:
                    continue
                target_text = " ".join((
                    target.get("title", ""), target.get("objective", ""),
                    target.get("domain", ""),
                    " ".join(
                        milestone.get("title", "") + " " + milestone.get("objective", "")
                        for milestone in target.get("milestones", [])
                    ),
                ))
                target_terms = _terms(target_text)
                overlap = node_terms & target_terms
                if not overlap:
                    continue
                # Coverage: how much of the node's topic is represented by the target.
                score = len(overlap) / len(node_terms)
                if score < min_score:
                    continue
                ordered = tuple(sorted(overlap))
                rationale = (
                    "Shared vocabulary between the knowledge item and the target "
                    "campaign's declared objectives: " + ", ".join(ordered) + "."
                )
                recommendations.append(CollaborationRecommendation(
                    recommendation_id=str(uuid.uuid4()),
                    source_campaign_id=source_id,
                    target_campaign_id=target_id,
                    node_id=node["node_id"],
                    node_label=node["label"],
                    target_campaign_title=target["title"],
                    score=round(score, 4),
                    matched_terms=ordered,
                    rationale=rationale,
                    verification_state=node.get("verification_state", "unverified"),
                ))
        recommendations.sort(
            key=lambda item: (-item.score, item.source_campaign_id,
                              item.target_campaign_id, item.node_id)
        )
        return recommendations[:bounded_limit]

    def create_transfer(
        self, recommendation_id: str, requester: str,
        *, source_campaign_id: str | None = None,
    ) -> dict:
        matches = [
            item for item in self.recommend(
                source_campaign_id=source_campaign_id, min_score=0.0, limit=500
            )
            if item.recommendation_id == recommendation_id
        ]
        if not matches:
            raise ValueError("Unknown or no longer eligible recommendation")
        item = matches[0]
        transfer = create_transfer(
            transfer_id=str(uuid.uuid4()),
            source_campaign_id=item.source_campaign_id,
            target_campaign_id=item.target_campaign_id,
            node_id=item.node_id,
            requested_by=requester,
        )
        self.store.create_knowledge_transfer(transfer)
        return asdict(transfer)


def recommendation_to_dict(item: CollaborationRecommendation) -> dict:
    return asdict(item)

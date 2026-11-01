"""Auditable knowledge hand-offs between research campaigns.

A transfer records a proposal to share an existing knowledge-graph node.
It never upgrades verification state or copies a claim into verified knowledge.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone


TRANSFER_STATES = {"pending", "accepted", "rejected"}


@dataclass(frozen=True)
class KnowledgeTransfer:
    transfer_id: str
    source_campaign_id: str
    target_campaign_id: str
    node_id: str
    requested_by: str
    state: str = "pending"
    decision_note: str = ""
    created_at: str = ""
    decided_at: str = ""


def create_transfer(
    transfer_id: str,
    source_campaign_id: str,
    target_campaign_id: str,
    node_id: str,
    requested_by: str,
) -> KnowledgeTransfer:
    values = (transfer_id, source_campaign_id, target_campaign_id, node_id, requested_by)
    if any(not isinstance(value, str) or not value.strip() for value in values):
        raise ValueError("Transfer ID, both campaigns, node ID and requester are required")
    if source_campaign_id == target_campaign_id:
        raise ValueError("Knowledge transfer requires two different campaigns")
    return KnowledgeTransfer(
        transfer_id.strip(), source_campaign_id.strip(), target_campaign_id.strip(),
        node_id.strip(), requested_by.strip(),
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def decide_transfer(
    transfer: KnowledgeTransfer, decision: str, note: str = ""
) -> KnowledgeTransfer:
    if transfer.state != "pending":
        raise ValueError("Only pending transfers can be decided")
    if decision not in {"accepted", "rejected"}:
        raise ValueError("Decision must be accepted or rejected")
    return KnowledgeTransfer(
        transfer.transfer_id, transfer.source_campaign_id,
        transfer.target_campaign_id, transfer.node_id, transfer.requested_by,
        decision, note.strip(), transfer.created_at,
        datetime.now(timezone.utc).isoformat(),
    )


def transfer_to_dict(transfer: KnowledgeTransfer) -> dict:
    return asdict(transfer)

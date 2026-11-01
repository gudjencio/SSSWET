"""Review workflow for immutable, versioned digital-lab protocols."""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any

from .digital_lab import DigitalLabService, LabProtocol, _verify_fingerprint

EDITABLE_FIELDS = {
    "title", "objective", "procedure", "required_parameters",
    "expected_outputs", "units", "controls", "limitations", "safety_notes",
}
LIST_FIELDS = {
    "procedure", "required_parameters", "expected_outputs",
    "controls", "limitations", "safety_notes",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ProtocolProposalService:
    """Collect proposals and let the protocol-owning campaign review them."""

    def __init__(self, store):
        self.store = store
        self.lab = DigitalLabService(store)

    def submit(self, proposal_id: str, protocol_id: str, base_version: int,
               proposer_campaign_id: str, changes: dict[str, Any],
               rationale: str) -> dict:
        if not all(isinstance(value, str) and value.strip() for value in
                   (proposal_id, protocol_id, proposer_campaign_id, rationale)):
            raise ValueError("Proposal identifiers and rationale are required")
        if not isinstance(base_version, int) or isinstance(base_version, bool) or base_version < 1:
            raise ValueError("Base protocol version must be a positive integer")
        if not isinstance(changes, dict) or not changes:
            raise ValueError("At least one proposed protocol change is required")
        unknown = set(changes) - EDITABLE_FIELDS
        if unknown:
            raise ValueError("Unsupported protocol fields: " + ", ".join(sorted(unknown)))
        base = self.store.get_lab_protocol(protocol_id, base_version)
        if base is None or base.get("state") != "published":
            raise ValueError("A published base protocol version is required")
        if not _verify_fingerprint(base, "content_hash"):
            raise ValueError("Base protocol fingerprint check failed")
        if proposer_campaign_id == base["owner_campaign_id"]:
            raise ValueError("Proposals must come from a different campaign")
        normalized = dict(changes)
        for field in LIST_FIELDS & set(normalized):
            value = normalized[field]
            if not isinstance(value, (list, tuple)) or not value:
                raise ValueError(f"{field} must be a non-empty list")
            if any(not isinstance(item, str) or not item.strip() for item in value):
                raise ValueError(f"{field} must contain non-empty text values")
            normalized[field] = list(value)
        for field in ("title", "objective"):
            if field in normalized and (
                not isinstance(normalized[field], str) or not normalized[field].strip()
            ):
                raise ValueError(f"{field} must be non-empty text")
        if "units" in normalized and (
            not isinstance(normalized["units"], dict)
            or any(not isinstance(k, str) or not isinstance(v, str)
                   for k, v in normalized["units"].items())
        ):
            raise ValueError("units must be an object containing text keys and values")
        return self.store.save_lab_protocol_proposal({
            "proposal_id": proposal_id,
            "protocol_id": protocol_id,
            "base_version": base_version,
            "proposer_campaign_id": proposer_campaign_id,
            "changes": normalized,
            "rationale": rationale.strip(),
            "status": "pending",
            "created_at": _now(),
            "reviewer_campaign_id": "",
            "review_note": "",
            "decided_at": "",
            "resulting_version": 0,
            "scientific_validity_established": False,
        })

    def decide(self, proposal_id: str, reviewer_campaign_id: str,
               decision: str, note: str) -> dict:
        if decision not in {"accepted", "rejected"}:
            raise ValueError("Decision must be accepted or rejected")
        if not isinstance(note, str) or not note.strip():
            raise ValueError("A review note is required")
        proposal = self.store.get_lab_protocol_proposal(proposal_id)
        if proposal is None:
            raise ValueError("Protocol proposal does not exist")
        if proposal["status"] != "pending":
            raise ValueError("Only pending proposals can be reviewed")
        base = self.store.get_lab_protocol(proposal["protocol_id"], proposal["base_version"])
        if base is None or not _verify_fingerprint(base, "content_hash"):
            raise ValueError("Base protocol is missing or its fingerprint check failed")
        resulting_version = 0
        if decision == "accepted":
            history = [
                item for item in self.store.lab_protocol_history(limit=500)
                if item["protocol_id"] == proposal["protocol_id"]
            ]
            latest = max((item["version"] for item in history), default=0)
            if latest != proposal["base_version"]:
                raise ValueError("Protocol has advanced; submit a new proposal against the latest version")
            changes = dict(proposal["changes"])
            for field in LIST_FIELDS & set(changes):
                changes[field] = tuple(changes[field])
            updated = dict(base)
            updated.update(changes)
            updated.update({
                "version": latest + 1,
                "state": "published",
                "reviewed_by": reviewer_campaign_id,
                "review_note": note.strip(),
                "created_at": "",
                "content_hash": "",
            })
            resulting_version = self.lab.publish_protocol(LabProtocol(**updated))["version"]
        return self.store.decide_lab_protocol_proposal(
            proposal_id, decision, reviewer_campaign_id, note.strip(),
            _now(), resulting_version,
        )

    def overview(self, limit: int = 200) -> dict:
        proposals = self.store.lab_protocol_proposal_history(limit=limit)
        return {
            "proposals": proposals,
            "pending_count": sum(item["status"] == "pending" for item in proposals),
            "accepted_count": sum(item["status"] == "accepted" for item in proposals),
            "rejected_count": sum(item["status"] == "rejected" for item in proposals),
            "decisions_require_owner_campaign_review": True,
            "proposal_acceptance_establishes_scientific_validity": False,
        }

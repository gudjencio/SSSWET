"""Auditable review workflow for explicitly contradictory knowledge-graph claims.

Detection identifies recorded contradiction edges; it does not decide which
claim is correct. Reviews require a human note and never modify graph claims.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib


DISPUTE_STATES = {"open", "reviewing", "resolved", "unresolved", "insufficient_evidence"}


@dataclass(frozen=True)
class DisputeCase:
    case_id: str
    left_node_id: str
    right_node_id: str
    left_label: str
    right_label: str
    left_campaign_id: str
    right_campaign_id: str
    edge_note: str
    edge_confidence: float
    state: str = "open"
    review_note: str = ""
    reviewer: str = ""
    created_at: str = ""
    reviewed_at: str = ""
    source_ids: tuple[str, ...] = ()
    provenance_warnings: tuple[str, ...] = ()


def detect_disputes(graph: dict) -> list[dict]:
    nodes = {node["node_id"]: node for node in graph.get("nodes", [])}
    disputes = []
    for edge in graph.get("edges", []):
        if edge.get("relation") != "contradicts":
            continue
        left, right = nodes.get(edge.get("source_id")), nodes.get(edge.get("target_id"))
        if left is None or right is None:
            continue
        lm, rm = left.get("metadata") or {}, right.get("metadata") or {}
        source_ids = tuple(sorted(set(
            list(lm.get("source_ids", [])) + list(rm.get("source_ids", []))
        )))
        identity = "|".join(sorted((left["node_id"], right["node_id"])))
        case_id = "dispute:" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:24]
        disputes.append({
            "case_id": case_id,
            "left_node_id": left["node_id"], "right_node_id": right["node_id"],
            "left_label": left["label"], "right_label": right["label"],
            "left_campaign_id": lm.get("campaign_id", ""),
            "right_campaign_id": rm.get("campaign_id", ""),
            "edge_note": edge.get("note", ""),
            "edge_confidence": edge.get("confidence", 0.0),
            "source_ids": list(source_ids),
            "verification_states": [
                left.get("verification_state", "unverified"),
                right.get("verification_state", "unverified"),
            ],
            "requires_human_review": True,
            "scientific_conclusion": None,
        })
    return sorted(disputes, key=lambda item: item["case_id"])


class DisputeResolutionService:
    def __init__(self, store: object):
        self.store = store

    def detected(self) -> list[dict]:
        return detect_disputes(self.store.knowledge_graph(limit=2000))

    def open_case(self, case_id: str) -> dict:
        candidate = next((x for x in self.detected() if x["case_id"] == case_id), None)
        if candidate is None:
            raise ValueError("Unknown or no longer detected contradiction")
        from_history = {x["case_id"] for x in self.store.dispute_history(limit=1000)}
        if case_id in from_history:
            raise ValueError("A review case already exists for this contradiction")
        case = DisputeCase(
            case_id=candidate["case_id"],
            left_node_id=candidate["left_node_id"], right_node_id=candidate["right_node_id"],
            left_label=candidate["left_label"], right_label=candidate["right_label"],
            left_campaign_id=candidate["left_campaign_id"],
            right_campaign_id=candidate["right_campaign_id"],
            edge_note=candidate["edge_note"],
            edge_confidence=candidate["edge_confidence"],
            created_at=datetime.now(timezone.utc).isoformat(),
            source_ids=tuple(candidate["source_ids"]),
            provenance_warnings=tuple(
                ["Source provenance has not been independently assessed."]
                if candidate["source_ids"] else
                ["No source identifiers are attached to one or both claims."]
            ),
        )
        self.store.save_dispute_case(asdict(case))
        return asdict(case)

    def review(
        self, case_id: str, state: str, note: str, reviewer: str,
    ) -> dict:
        if state not in DISPUTE_STATES:
            raise ValueError("Unsupported dispute review state")
        if state == "open":
            raise ValueError("A review cannot transition back to open")
        if not isinstance(note, str) or not note.strip():
            raise ValueError("A substantive review note is required")
        if not isinstance(reviewer, str) or not reviewer.strip():
            raise ValueError("Reviewer identity is required")
        current = next(
            (x for x in self.store.dispute_history(limit=1000) if x["case_id"] == case_id),
            None,
        )
        if current is None:
            raise ValueError("Unknown dispute case")
        if current["state"] in {"resolved", "unresolved", "insufficient_evidence"}:
            raise ValueError("A closed review case cannot be changed")
        updated = {
            **current, "state": state, "review_note": note.strip(),
            "reviewer": reviewer.strip(),
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
        }
        self.store.update_dispute_case(updated)
        return updated

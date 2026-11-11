"""Append-only conflict declarations and reviewer recusal checks for research agents."""
from __future__ import annotations

from datetime import datetime, timezone

MAX_EVENTS = 10000
CONFLICT_CATEGORIES = {
    "none_declared", "financial", "employment", "collaboration",
    "personal_relationship", "institutional", "data_access", "other",
}


def _clean(value, field, maximum=240):
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > maximum:
        raise ValueError(f"{field} must contain 1 to {maximum} characters")
    return value.strip()


def _refs(values, field):
    if not isinstance(values, list) or len(values) > 500:
        raise ValueError(f"{field} must be a list of at most 500 values")
    result = sorted(set(_clean(item, field) for item in values))
    if len(result) != len(values):
        raise ValueError(f"{field} must not contain duplicates")
    return result


class AgentConflictRegister:
    """Record disclosures and later independent reviews without overwriting history."""
    def __init__(self, events: list[dict] | None = None):
        self._events = []
        for event in events or []:
            if not isinstance(event, dict):
                raise ValueError("existing events must be dictionaries")
            self._events.append(dict(event))
        if len(self._events) > MAX_EVENTS:
            raise ValueError(f"register is limited to {MAX_EVENTS} events")

    def declare(self, *, declaration_id: str, agent_id: str, category: str,
                description: str, campaign_ids: list[str] | None = None,
                source_ids: list[str] | None = None, global_scope: bool = False,
                recorded_at: str | None = None) -> dict:
        declaration_id = _clean(declaration_id, "declaration_id")
        agent_id = _clean(agent_id, "agent_id")
        description = _clean(description, "description", 4000)
        if category not in CONFLICT_CATEGORIES:
            raise ValueError("unsupported conflict category")
        if not isinstance(global_scope, bool):
            raise ValueError("global_scope must be boolean")
        campaigns = _refs(campaign_ids or [], "campaign_ids")
        sources = _refs(source_ids or [], "source_ids")
        if not global_scope and not campaigns and not sources:
            raise ValueError("a conflict must have a campaign, source or explicit global scope")
        if any(event["declaration_id"] == declaration_id for event in self._events):
            raise ValueError("declaration_id already exists")
        timestamp = _clean(recorded_at, "recorded_at") if recorded_at else datetime.now(timezone.utc).isoformat()
        event = {
            "event_id": declaration_id, "declaration_id": declaration_id,
            "supersedes_event_id": None, "agent_id": agent_id,
            "category": category, "description": description,
            "campaign_ids": campaigns, "source_ids": sources,
            "global_scope": global_scope,
            "status": "none_declared" if category == "none_declared" else "declared",
            "reviewer_id": None, "review_note": "", "evidence_refs": [],
            "recorded_at": timestamp,
        }
        self._append(event)
        return dict(event)

    def review(self, declaration_id: str, *, reviewer_id: str, decision: str,
               note: str, evidence_refs: list[str], recorded_at: str | None = None) -> dict:
        declaration_id = _clean(declaration_id, "declaration_id")
        reviewer = _clean(reviewer_id, "reviewer_id")
        note = _clean(note, "note", 4000)
        refs = _refs(evidence_refs, "evidence_refs")
        if decision not in {"recused", "cleared_after_review"}:
            raise ValueError("decision must be recused or cleared_after_review")
        history = [item for item in self._events if item["declaration_id"] == declaration_id]
        if not history:
            raise ValueError("declaration does not exist")
        previous = history[-1]
        if reviewer == previous["agent_id"]:
            raise ValueError("an agent cannot review its own conflict declaration")
        if previous["status"] in {"none_declared", "cleared_after_review", "recused"}:
            raise ValueError("the declaration is already resolved or has no conflict")
        if not refs:
            raise ValueError("an independent review requires evidence references")
        event_id = f"{declaration_id}:review:{len(history)}"
        event = {
            **previous, "event_id": event_id, "supersedes_event_id": previous["event_id"],
            "status": decision, "reviewer_id": reviewer, "review_note": note,
            "evidence_refs": refs,
            "recorded_at": _clean(recorded_at, "recorded_at") if recorded_at else datetime.now(timezone.utc).isoformat(),
        }
        self._append(event)
        return dict(event)

    def _append(self, event):
        if len(self._events) >= MAX_EVENTS:
            raise ValueError(f"register is limited to {MAX_EVENTS} events")
        self._events.append(dict(event))

    def history(self, declaration_id: str | None = None) -> list[dict]:
        if declaration_id is not None:
            key = _clean(declaration_id, "declaration_id")
            selected = [item for item in self._events if item["declaration_id"] == key]
        else:
            selected = list(self._events)
        return [dict(item) for item in selected]

    def eligibility(self, agent_id: str, *, campaign_id: str = "",
                    source_ids: list[str] | None = None) -> dict:
        agent = _clean(agent_id, "agent_id")
        campaign = campaign_id.strip() if campaign_id else ""
        sources = set(_refs(source_ids or [], "source_ids"))
        latest = {}
        for event in self._events:
            if event["agent_id"] == agent:
                latest[event["declaration_id"]] = event
        applicable = []
        for event in latest.values():
            scope_match = (
                event["global_scope"]
                or (campaign and campaign in event["campaign_ids"])
                or bool(sources & set(event["source_ids"]))
            )
            if scope_match:
                applicable.append(event)
        blockers = [
            {"declaration_id": item["declaration_id"], "status": item["status"],
             "category": item["category"], "reviewer_id": item["reviewer_id"]}
            for item in applicable if item["status"] in {"declared", "recused"}
        ]
        declaration_present = bool(applicable)
        cleared = all(item["status"] in {"none_declared", "cleared_after_review"} for item in applicable)
        return {
            "agent_id": agent, "applicable_declaration_count": len(applicable),
            "declarations": sorted(blockers, key=lambda item: item["declaration_id"]),
            "status": "blocked_by_declared_conflict" if blockers else "eligible_with_disclosure" if declaration_present and cleared else "no_applicable_declaration",
            "eligible_for_assignment": bool(declaration_present and cleared and not blockers),
            "independence_certified": False,
            "absence_of_declaration_is_not_evidence_of_independence": True,
        }

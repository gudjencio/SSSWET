"""Bounded research campaign records and explicit milestone transitions.

Campaigns coordinate bookkeeping across studies; they do not launch physical
experiments or silently execute proposed work.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


CAMPAIGN_STATES = {"draft", "active", "paused", "completed", "blocked"}
MILESTONE_STATES = {"pending", "in_progress", "completed", "blocked"}


@dataclass(frozen=True)
class CampaignMilestone:
    milestone_id: str
    title: str
    objective: str
    state: str = "pending"
    linked_study_ids: tuple[str, ...] = ()
    notes: str = ""


@dataclass(frozen=True)
class ResearchCampaign:
    campaign_id: str
    title: str
    objective: str
    domain: str
    state: str
    milestones: tuple[CampaignMilestone, ...]
    hypothesis: str = ""
    success_criteria: tuple[str, ...] = ()
    failure_criteria: tuple[str, ...] = ()
    agent_roles: tuple[str, ...] = ()
    resource_requirements: tuple[str, ...] = ()
    source_refs: tuple[str, ...] = ()
    safety_gates: tuple[str, ...] = ()
    warnings: tuple[str, ...] = (
        "Campaign status tracks workflow progress, not scientific validity.",
        "Simulation results, real observations and verified findings remain distinct.",
        "High-risk research requires qualified human, safety, ethics and regulatory review.",
    )


def create_campaign(
    campaign_id: str,
    title: str,
    objective: str,
    domain: str,
    milestones: list[CampaignMilestone],
    *,
    hypothesis: str = "",
    success_criteria: tuple[str, ...] = (),
    failure_criteria: tuple[str, ...] = (),
    agent_roles: tuple[str, ...] = (),
    resource_requirements: tuple[str, ...] = (),
    source_refs: tuple[str, ...] = (),
    safety_gates: tuple[str, ...] = (),
) -> ResearchCampaign:
    values = (campaign_id, title, objective, domain)
    if any(not isinstance(value, str) or not value.strip() for value in values):
        raise ValueError("Campaign ID, title, objective and domain are required")
    if len(milestones) > 100:
        raise ValueError("A campaign is limited to 100 milestones")
    ids = [item.milestone_id for item in milestones]
    if any(not item.strip() for item in ids) or len(set(ids)) != len(ids):
        raise ValueError("Milestone IDs must be non-empty and unique")
    for item in milestones:
        if item.state not in MILESTONE_STATES:
            raise ValueError(f"Unsupported milestone state: {item.state}")
        if not item.title.strip() or not item.objective.strip():
            raise ValueError("Every milestone needs a title and objective")
    if hypothesis and (not isinstance(hypothesis, str) or len(hypothesis) > 4000):
        raise ValueError("Hypothesis must be text of at most 4000 characters")
    collections = {
        "success_criteria": success_criteria, "failure_criteria": failure_criteria,
        "agent_roles": agent_roles, "resource_requirements": resource_requirements,
        "source_refs": source_refs, "safety_gates": safety_gates,
    }
    normalized = {}
    for key, values in collections.items():
        if not isinstance(values, (tuple, list)) or any(
            not isinstance(value, str) or not value.strip() or len(value) > 1000
            for value in values
        ):
            raise ValueError(f"{key} must contain non-empty text entries")
        normalized[key] = tuple(value.strip() for value in values)
    return ResearchCampaign(
        campaign_id.strip(), title.strip(), objective.strip(), domain.strip(),
        "draft", tuple(milestones), hypothesis.strip(), **normalized,
    )


def set_campaign_state(campaign: ResearchCampaign, state: str) -> ResearchCampaign:
    allowed = {
        "draft": {"active", "blocked"},
        "active": {"paused", "completed", "blocked"},
        "paused": {"active", "blocked"},
        "blocked": {"active", "paused"},
        "completed": set(),
    }
    if state not in CAMPAIGN_STATES:
        raise ValueError(f"Unsupported campaign state: {state}")
    if state != campaign.state and state not in allowed[campaign.state]:
        raise ValueError(f"Invalid campaign transition: {campaign.state} -> {state}")
    if state == "completed" and any(m.state != "completed" for m in campaign.milestones):
        raise ValueError("All milestones must be completed before campaign completion")
    return ResearchCampaign(
        campaign.campaign_id, campaign.title, campaign.objective, campaign.domain,
        state, campaign.milestones, campaign.hypothesis,
        campaign.success_criteria, campaign.failure_criteria, campaign.agent_roles,
        campaign.resource_requirements, campaign.source_refs, campaign.safety_gates,
        campaign.warnings,
    )


def update_milestone(
    campaign: ResearchCampaign, milestone_id: str, state: str,
    linked_study_ids: tuple[str, ...] | None = None, notes: str | None = None,
) -> ResearchCampaign:
    if state not in MILESTONE_STATES:
        raise ValueError(f"Unsupported milestone state: {state}")
    found = False
    updated = []
    for item in campaign.milestones:
        if item.milestone_id == milestone_id:
            found = True
            updated.append(CampaignMilestone(
                item.milestone_id, item.title, item.objective, state,
                item.linked_study_ids if linked_study_ids is None else linked_study_ids,
                item.notes if notes is None else notes,
            ))
        else:
            updated.append(item)
    if not found:
        raise ValueError(f"Unknown milestone: {milestone_id}")
    return ResearchCampaign(
        campaign.campaign_id, campaign.title, campaign.objective, campaign.domain,
        campaign.state, tuple(updated), campaign.hypothesis,
        campaign.success_criteria, campaign.failure_criteria, campaign.agent_roles,
        campaign.resource_requirements, campaign.source_refs, campaign.safety_gates,
        campaign.warnings,
    )


def campaign_to_dict(campaign: ResearchCampaign) -> dict[str, Any]:
    return asdict(campaign)

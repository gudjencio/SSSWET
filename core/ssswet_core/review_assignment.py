"""Deterministic safeguards for proposing independent scientific reviewers.

This module prepares an auditable assignment proposal. It does not contact
reviewers, verify identities, or establish scientific independence.
"""
from __future__ import annotations

from dataclasses import dataclass


PRIORITY_ROLES = (
    "independent_verifier", "data_analyst", "domain_specialist",
    "materials_scientist", "systems_engineer", "medical_researcher",
    "ethics_reviewer", "general_researcher", "futures_analyst",
)


@dataclass(frozen=True)
class ReviewerCandidate:
    agent_id: str
    role: str
    campaign_id: str = ""
    conflict_status: str = "none_declared"
    source_refs: tuple[str, ...] = ()


class IndependentReviewerSelector:
    """Build reviewer proposals while exposing exclusions and evidence overlap."""

    def propose(
        self, candidates: list[ReviewerCandidate], *,
        excluded_reviewer_ids: set[str] | None = None,
        excluded_campaign_ids: set[str] | None = None,
        lead_researcher_id: str = "",
        prior_source_refs: set[str] | None = None,
        required_count: int = 2,
    ) -> dict:
        if not isinstance(candidates, list):
            raise ValueError("candidates must be a list")
        if not isinstance(required_count, int) or isinstance(required_count, bool) or not 1 <= required_count <= 8:
            raise ValueError("required_count must be between 1 and 8")
        excluded_reviewer_ids = set(excluded_reviewer_ids or ())
        excluded_campaign_ids = set(excluded_campaign_ids or ())
        prior_source_refs = {str(value).strip() for value in (prior_source_refs or ()) if str(value).strip()}
        seen_ids = set()
        eligible = []
        exclusions = []
        for candidate in candidates:
            if not isinstance(candidate, ReviewerCandidate):
                raise ValueError("every candidate must be a ReviewerCandidate")
            agent_id = candidate.agent_id.strip()
            role = candidate.role.strip().lower()
            campaign_id = candidate.campaign_id.strip()
            if not agent_id or not role:
                exclusions.append({"agent_id": agent_id, "reason": "missing_identity_or_role"})
                continue
            if agent_id in seen_ids:
                exclusions.append({"agent_id": agent_id, "reason": "duplicate_candidate"})
                continue
            seen_ids.add(agent_id)
            if agent_id == lead_researcher_id or agent_id in excluded_reviewer_ids:
                exclusions.append({"agent_id": agent_id, "reason": "prior_reviewer_or_lead_researcher"})
                continue
            if campaign_id and campaign_id in excluded_campaign_ids:
                exclusions.append({"agent_id": agent_id, "reason": "prior_reviewer_campaign"})
                continue
            if candidate.conflict_status != "none_declared":
                exclusions.append({"agent_id": agent_id, "reason": "conflict_not_cleared", "conflict_status": candidate.conflict_status})
                continue
            overlap = sorted(set(candidate.source_refs) & prior_source_refs)
            eligible.append({
                "agent_id": agent_id, "role": role, "campaign_id": campaign_id,
                "shared_source_refs_to_disclose": overlap,
                "source_overlap_requires_disclosure": bool(overlap),
            })
        role_order = {role: index for index, role in enumerate(PRIORITY_ROLES)}
        eligible.sort(key=lambda item: (role_order.get(item["role"], len(role_order)), item["role"], item["agent_id"]))
        selected = []
        used_campaigns = set()
        for item in eligible:
            if item["campaign_id"] and item["campaign_id"] in used_campaigns:
                exclusions.append({"agent_id": item["agent_id"], "reason": "campaign_already_represented"})
                continue
            selected.append(item)
            if item["campaign_id"]:
                used_campaigns.add(item["campaign_id"])
            if len(selected) == required_count:
                break
        ready = len(selected) == required_count
        return {
            "status": "proposed" if ready else "insufficient_independent_candidates",
            "selected_reviewers": selected,
            "excluded_candidates": exclusions,
            "required_count": required_count,
            "selected_count": len(selected),
            "distinct_roles": len({item["role"] for item in selected}),
            "distinct_campaigns": len({item["campaign_id"] for item in selected if item["campaign_id"]}),
            "shared_sources_must_be_disclosed": any(item["source_overlap_requires_disclosure"] for item in selected),
            "reviewer_assignment_executed": False,
            "independence_certified": False,
            "scientific_validity_established": False,
        }

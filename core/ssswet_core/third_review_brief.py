"""Prepare an auditable brief for an independent third scientific review.

The brief organizes existing dossier and review records. It does not invoke an
agent, rank reviewers, resolve disagreements, or establish scientific validity.
"""
from __future__ import annotations

from collections import Counter
from typing import Any

from .evidence_dossiers import EvidenceDossierService
from .scientific_review_board import ScientificReviewBoard


class ThirdReviewBriefService:
    def __init__(self, store: Any):
        self.store = store

    def build(self, dossier_id: str) -> dict:
        if not isinstance(dossier_id, str) or not dossier_id.strip():
            raise ValueError("dossier_id is required")
        dossier = EvidenceDossierService(self.store).get(dossier_id.strip())
        report = ScientificReviewBoard(self.store).report(
            dossier_id=dossier_id.strip(), limit=2000
        )
        reviews = report["reviews"]
        verdicts = Counter(item["verdict"] for item in reviews)
        evidence_usage = Counter(
            ref for review in reviews for ref in review.get("evidence_refs", [])
        )
        repeated_evidence = sorted(
            ref for ref, count in evidence_usage.items() if count > 1
        )
        reviewer_ids = sorted({item["reviewer_id"] for item in reviews})
        campaign_ids = sorted({
            item["reviewer_campaign_id"]
            for item in reviews if item.get("reviewer_campaign_id")
        })
        disagreement = len(verdicts) > 1
        ready = len(reviews) >= 2

        reviewer_assessments = [
            {
                "review_id": item["review_id"],
                "reviewer_id": item["reviewer_id"],
                "reviewer_campaign_id": item["reviewer_campaign_id"],
                "verdict": item["verdict"],
                "rationale": item["rationale"],
                "methods_assessment": item["methods_assessment"],
                "limitations": item["limitations"],
                "evidence_refs": item["evidence_refs"],
                "conflict_of_interest_declaration": item["conflict_status"],
            }
            for item in reviews
        ]

        instructions = [
            "Act as an independent reviewer; do not assume any prior assessment is correct.",
            "Assess the dossier's claims against the cited evidence, not the confidence or seniority of prior reviewers.",
            "Separate direct observations, reported results, interpretations, assumptions, and hypotheses.",
            "Check source provenance, independence, publication status, dates, methods, units, sample sizes, controls, and reproducibility where applicable.",
            "Identify evidence that supports, challenges, or qualifies each material claim.",
            "Explain whether apparent disagreements could arise from different conditions, definitions, methods, or measurement uncertainty.",
            "State what evidence is missing and what safe, proportionate next checks could reduce uncertainty.",
            "Declare conflicts of interest and disclose any shared sources or provenance with prior reviewers.",
            "Do not use majority voting. Do not declare scientific validity solely from reviewer agreement.",
            "If evidence is inadequate, abstain and explain why."
        ]

        return {
            "dossier_id": dossier_id.strip(),
            "dossier_title": dossier["title"],
            "result_summary": dossier["result_summary"],
            "dossier_content_hash": dossier["content_hash"],
            "review_count": len(reviews),
            "third_review_status": (
                "recommended_due_to_disagreement" if ready and disagreement else
                "optional_independent_check" if ready else
                "not_ready_fewer_than_two_prior_reviews"
            ),
            "ready_for_third_review": ready,
            "prior_verdict_counts": dict(sorted(verdicts.items())),
            "prior_reviewers_to_exclude": reviewer_ids,
            "prior_reviewer_campaigns_to_exclude": campaign_ids,
            "shared_evidence_refs": repeated_evidence,
            "prior_assessments": reviewer_assessments,
            "dossier_source_refs": [
                {
                    "source_id": source.get("source_id", ""),
                    "title": source.get("title", ""),
                    "doi": source.get("doi", ""),
                    "url": source.get("url", ""),
                    "provenance_group": source.get("provenance_group", ""),
                }
                for source in dossier.get("sources", [])
            ],
            "third_reviewer_instructions": instructions,
            "requested_output_schema": {
                "verdict": ["supports", "challenges", "mixed", "abstains"],
                "conflict_of_interest": ["none_declared", "potential", "confirmed"],
                "rationale": "Evidence-linked assessment of the principal claims",
                "methods_assessment": "Assessment of methods, assumptions, units and reproducibility",
                "limitations": "Uncertainties, missing evidence and scope limits",
                "evidence_refs": "Identifiers of the sources actually examined",
                "shared_sources_and_provenance": "Any overlap with earlier reviews",
            },
            "automatic_reviewer_assignment": False,
            "automatic_adjudication": False,
            "majority_vote_used": False,
            "scientific_validity_established": False,
        }

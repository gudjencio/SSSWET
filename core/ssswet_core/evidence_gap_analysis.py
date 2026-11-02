"""Evidence-gap analysis for assembled dossiers and recorded review events.

The analyzer reports omissions in supplied records only. It does not infer that
missing records do not exist elsewhere or determine which scientific position
is correct.
"""
from __future__ import annotations

from typing import Any


class EvidenceGapAnalyzer:
    """Create deterministic, human-readable follow-up items from dossier records."""

    def analyze(self, dossier: dict[str, Any], reviews: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        if not isinstance(dossier, dict):
            raise ValueError("dossier must be a dictionary")
        if reviews is None:
            reviews = []
        if not isinstance(reviews, list):
            raise ValueError("reviews must be a list")

        gaps: list[dict[str, str]] = []

        def add(category: str, priority: str, title: str, reason: str, action: str) -> None:
            gaps.append({
                "category": category,
                "priority": priority,
                "title": title,
                "reason": reason,
                "suggested_action": action,
            })

        sources = dossier.get("sources", [])
        runs = dossier.get("runs", [])
        datasets = dossier.get("datasets", [])
        protocols = dossier.get("protocols", [])
        comparisons = dossier.get("comparisons", [])
        for name, value in (("sources", sources), ("runs", runs),
                            ("datasets", datasets), ("protocols", protocols),
                            ("comparisons", comparisons)):
            if not isinstance(value, list):
                raise ValueError(f"dossier {name} must be a list")

        if not sources:
            add("no_sources_in_dossier", "high", "No source records are attached",
                "The supplied dossier contains no linked source records. This describes the dossier only, not the wider literature.",
                "Locate relevant primary sources and attach their exact identifiers and bibliographic records.")
        if not runs:
            add("no_run_records", "medium", "No research run records are attached",
                "The supplied dossier contains no recorded research runs.",
                "Link the relevant run records, or explain why this dossier is a literature-only review.")
        if not datasets:
            add("no_dataset_records", "medium", "No dataset records are attached",
                "The supplied dossier contains no linked dataset records.",
                "Attach the datasets used, including versions and provenance, or document why no dataset applies.")
        if not protocols:
            add("no_protocol_records", "medium", "No protocol records are attached",
                "The supplied dossier contains no versioned protocol references.",
                "Attach applicable protocol versions and document deviations, or explain why no protocol applies.")
        if not comparisons:
            add("no_comparison_records", "medium", "No comparison records are attached",
                "The supplied dossier contains no recorded model or result comparisons.",
                "Record relevant comparisons with their inputs and limitations, or state why comparison is not applicable.")

        valid_reviews = [item for item in reviews if isinstance(item, dict)]
        verdicts = {item.get("verdict") for item in valid_reviews
                    if item.get("verdict") in {"supports", "challenges", "mixed", "abstains"}}
        if not valid_reviews:
            add("no_review_records", "medium", "No review assessments are attached",
                "No structured review events were supplied to the analyzer.",
                "Request independent assessments with methods, limitations, conflict declarations and traceable evidence references.")
        if len(verdicts) > 1:
            add("competing_review_positions", "high", "Reviewers recorded competing positions",
                "More than one review verdict is present. The analyzer does not decide which position is better supported.",
                "Compare each rationale, methods assessment, limitations and cited evidence; identify the specific observation or source inspection that could distinguish the interpretations.")

        known_source_ids = {
            item.get("source_id") for item in sources
            if isinstance(item, dict) and isinstance(item.get("source_id"), str)
        }
        known_record_ids = known_source_ids | {
            item.get("run_id") for item in runs if isinstance(item, dict) and isinstance(item.get("run_id"), str)
        } | {
            item.get("dataset_id") for item in datasets if isinstance(item, dict) and isinstance(item.get("dataset_id"), str)
        } | {
            item.get("comparison_id") for item in comparisons if isinstance(item, dict) and isinstance(item.get("comparison_id"), str)
        }
        cited = {
            ref for review in valid_reviews
            for ref in (review.get("evidence_refs", []) if isinstance(review.get("evidence_refs", []), list) else [])
            if isinstance(ref, str) and ref.strip()
        }
        unresolved = sorted(cited - known_record_ids)
        if unresolved:
            add("unmatched_review_references", "high", "Some review references are not in the dossier",
                "One or more review evidence identifiers do not match source, run, dataset or comparison identifiers in the supplied dossier. They may exist outside this dossier.",
                "Resolve each identifier against the originating record system and attach the corresponding versioned record where appropriate.")

        priority_order = {"high": 0, "medium": 1, "low": 2}
        gaps.sort(key=lambda item: (priority_order[item["priority"]], item["category"]))
        counts = {level: sum(item["priority"] == level for item in gaps)
                  for level in ("high", "medium", "low")}
        return {
            "dossier_id": dossier.get("dossier_id"),
            "gaps": gaps,
            "total": len(gaps),
            "priority_counts": counts,
            "unmatched_review_reference_ids": unresolved,
            "scientific_validity_established": False,
            "automatic_adjudication": False,
            "notice": (
                "Findings describe omissions and inconsistencies in the records supplied to this analysis. "
                "They do not prove that evidence is absent elsewhere, establish scientific validity, "
                "or authorize experiments or implementation."
            ),
        }

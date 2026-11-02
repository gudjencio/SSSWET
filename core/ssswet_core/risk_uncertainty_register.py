"""Structured, non-scoring review of explicitly supplied research risks and uncertainties."""
from __future__ import annotations

from collections import Counter
from typing import Any, Iterable


class ResearchRiskUncertaintyRegister:
    """Summarize declared risk records without inventing assessments.

    This component is a transparent organizer, not a risk-prediction engine.
    Missing likelihood, impact, ownership, dates or mitigations remain unknown.
    It deliberately does not calculate a composite risk score or authorize work.
    """

    CATEGORIES = {
        "scientific", "technical", "measurement", "ethical",
        "environmental", "regulatory", "safety", "operational", "other",
    }
    STATUSES = {
        "open", "monitoring", "mitigation_in_progress",
        "accepted", "closed", "unknown",
    }
    ASSESSMENT_LEVELS = {"low", "medium", "high", "unknown"}

    REQUIRED_FIELDS = ("item_id", "title", "category")
    REVIEW_FIELDS = (
        "description", "status", "likelihood", "impact", "owner",
        "review_due", "evidence_refs", "assumptions",
        "invalidation_conditions", "mitigation_actions", "provenance",
    )

    @staticmethod
    def _strings(value: Any, field: str, item_id: str) -> list[str]:
        if value is None:
            return []
        if not isinstance(value, (list, tuple)):
            raise ValueError(f"{field} for {item_id} must be a list")
        if any(not isinstance(entry, str) or not entry.strip() for entry in value):
            raise ValueError(f"{field} for {item_id} must contain non-empty strings")
        return list(dict.fromkeys(entry.strip() for entry in value))

    def analyze(self, records: Iterable[dict[str, Any]]) -> dict[str, Any]:
        if isinstance(records, (str, bytes, dict)) or records is None:
            raise ValueError("records must be an iterable of risk record objects")

        normalized: list[dict[str, Any]] = []
        seen: set[str] = set()
        for record in records:
            if not isinstance(record, dict):
                raise ValueError("each risk record must be an object")
            missing_required = [
                field for field in self.REQUIRED_FIELDS
                if not isinstance(record.get(field), str) or not record[field].strip()
            ]
            if missing_required:
                raise ValueError("risk record is missing required fields: " + ", ".join(missing_required))

            item_id = record["item_id"].strip()
            if item_id in seen:
                raise ValueError(f"duplicate item_id: {item_id}")
            seen.add(item_id)

            category = record["category"].strip().lower()
            if category not in self.CATEGORIES:
                raise ValueError(f"unsupported category for {item_id}: {category}")

            status = record.get("status")
            if status is not None:
                if not isinstance(status, str) or status.strip().lower() not in self.STATUSES:
                    raise ValueError(f"unsupported status for {item_id}")
                status = status.strip().lower()
            else:
                status = "unknown"

            likelihood = record.get("likelihood")
            impact = record.get("impact")
            for field, value in (("likelihood", likelihood), ("impact", impact)):
                if value is not None and (
                    not isinstance(value, str)
                    or value.strip().lower() not in self.ASSESSMENT_LEVELS
                ):
                    raise ValueError(f"{field} for {item_id} must be low, medium, high or unknown")
            likelihood = likelihood.strip().lower() if isinstance(likelihood, str) else None
            impact = impact.strip().lower() if isinstance(impact, str) else None

            item = {
                "item_id": item_id,
                "title": record["title"].strip(),
                "category": category,
                "description": str(record.get("description") or ""),
                "status": status,
                "likelihood": likelihood,
                "impact": impact,
                "owner": record.get("owner"),
                "review_due": record.get("review_due"),
                "evidence_refs": self._strings(record.get("evidence_refs"), "evidence_refs", item_id),
                "assumptions": self._strings(record.get("assumptions"), "assumptions", item_id),
                "invalidation_conditions": self._strings(
                    record.get("invalidation_conditions"), "invalidation_conditions", item_id
                ),
                "mitigation_actions": self._strings(
                    record.get("mitigation_actions"), "mitigation_actions", item_id
                ),
                "provenance": record.get("provenance"),
            }
            missing_review = [
                field for field in self.REVIEW_FIELDS
                if record.get(field) in (None, "", [], ())
            ]
            item["missing_fields"] = missing_review
            item["assessment_complete"] = not missing_review
            normalized.append(item)

        return {
            "record_count": len(normalized),
            "category_counts": dict(sorted(Counter(x["category"] for x in normalized).items())),
            "status_counts": dict(sorted(Counter(x["status"] for x in normalized).items())),
            "unassessed_count": sum(
                1 for x in normalized if x["likelihood"] is None or x["impact"] is None
            ),
            "records": normalized,
            "composite_risk_score": None,
            "risk_ranking_generated": False,
            "scientific_validity_established": False,
            "work_authorized": False,
            "interpretation": (
                "This register organizes declared information only. Missing assessments remain unknown; "
                "no likelihood, impact, priority, scientific validity or authorization is inferred."
            ),
        }

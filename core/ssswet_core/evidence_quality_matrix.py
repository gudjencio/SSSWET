"""Transparent evidence-quality matrix for existing evidence dossiers."""
from __future__ import annotations

from typing import Any

from .sources import SourceRecord, SourceQualityAssessor, analyze_source_independence


class EvidenceQualityMatrix:
    """Summarize recorded source metadata and review coverage without truth scoring."""

    @staticmethod
    def _source_record(item: dict[str, Any]) -> SourceRecord:
        metadata = item.get("metadata") or {}
        return SourceRecord(
            source_id=str(item.get("source_id", "")),
            title=str(item.get("title", "")),
            url=str(item.get("url", "")),
            source_type=str(item.get("source_type", "unknown")),
            peer_reviewed=bool(metadata.get("peer_reviewed", False)),
            primary_source=bool(metadata.get("primary_source", False)),
            methods_available=bool(metadata.get("methods_available", False)),
            publication_date_known=bool(metadata.get("publication_date_known", False)),
            limitations=tuple(metadata.get("limitations", [])),
            doi=str(item.get("doi", "")),
            authors=tuple(item.get("authors", [])),
            institutions=tuple(item.get("institutions", [])),
            dataset_ids=tuple(item.get("dataset_ids", [])),
            related_source_ids=tuple(item.get("related_source_ids", [])),
            provenance_group=str(item.get("provenance_group", "")),
        )

    def analyze(self, dossier: dict[str, Any], reviews: list[dict[str, Any]]) -> dict[str, Any]:
        if not isinstance(dossier, dict):
            raise ValueError("dossier must be a dictionary")
        if not isinstance(reviews, list) or any(not isinstance(item, dict) for item in reviews):
            raise ValueError("reviews must be a list of dictionaries")
        raw_sources = dossier.get("sources", [])
        if not isinstance(raw_sources, list) or any(not isinstance(item, dict) for item in raw_sources):
            raise ValueError("dossier sources must be a list of dictionaries")

        assessor = SourceQualityAssessor()
        source_assessments = []
        for item in raw_sources:
            try:
                source = self._source_record(item)
                assessment = assessor.assess(source)
            except (TypeError, ValueError, AttributeError):
                source_assessments.append({
                    "source_id": item.get("source_id"),
                    "assessment": "incomplete_source_metadata",
                    "score": None,
                    "tier": "not_assessed",
                    "factors": [],
                })
                continue
            source_assessments.append({
                "source_id": assessment.source_id,
                "assessment": "rubric_metadata_assessment",
                "score": assessment.score,
                "tier": assessment.tier,
                "factors": list(assessment.factors),
                "warning": assessment.warning,
            })

        independence = analyze_source_independence(raw_sources)
        verdicts = sorted({str(item.get("verdict", "unknown")) for item in reviews})
        review_coverage = {
            "review_count": len(reviews),
            "reviewer_count": len({item.get("reviewer_id") for item in reviews if item.get("reviewer_id")}),
            "verdicts_recorded": verdicts,
            "conflict_declarations_complete": all(
                item.get("conflict_status") in {"none_declared", "potential", "confirmed"}
                for item in reviews
            ),
            "multiple_positions_recorded": len(verdicts) > 1,
            "independent_review_established": False,
        }
        categories = {
            "sources": len(raw_sources),
            "protocols": len(dossier.get("protocols", [])),
            "runs": len(dossier.get("runs", [])),
            "datasets": len(dossier.get("datasets", [])),
            "comparisons": len(dossier.get("comparisons", [])),
            "peer_review_records_in_dossier": len(dossier.get("peer_reviews", [])),
            "scientific_board_reviews": len(reviews),
        }
        return {
            "dossier_id": dossier.get("dossier_id"),
            "record_counts": categories,
            "source_assessments": source_assessments,
            "source_independence": independence,
            "review_coverage": review_coverage,
            "limitations_recorded": sum(
                1 for item in raw_sources
                if (item.get("metadata") or {}).get("limitations")
            ),
            "missing_areas": [
                key for key in ("sources", "protocols", "runs", "datasets", "comparisons")
                if categories[key] == 0
            ],
            "scientific_validity_established": False,
            "evidence_quality_score": None,
            "notice": (
                "Source rubric scores describe declared metadata only; they are not probabilities "
                "of truth or scores for the dossier as a whole. Missing records may exist outside "
                "this dossier. Recorded reviewer count does not prove reviewer independence."
            ),
        }

    def build(self, store: Any, dossier_id: str | None = None, limit: int = 100) -> dict[str, Any]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 200:
            raise ValueError("limit must be an integer between 1 and 200")
        from .evidence_dossiers import EvidenceDossierService
        from .scientific_review_board import ScientificReviewBoard

        dossiers = EvidenceDossierService(store)
        selected = [dossiers.get(dossier_id)] if dossier_id else dossiers.overview(limit=limit)["dossiers"]
        board = ScientificReviewBoard(store)
        reports = []
        for item in selected:
            full = dossiers.get(item["dossier_id"])
            reviews = board.report(dossier_id=item["dossier_id"], limit=500).get("reviews", [])
            reports.append(self.analyze(full, reviews))
        return {
            "dossiers": reports,
            "count": len(reports),
            "read_only": True,
            "scientific_validity_established": False,
            "automatic_adjudication": False,
        }

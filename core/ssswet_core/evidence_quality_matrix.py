"""Transparent evidence-quality matrix for existing evidence dossiers."""
from __future__ import annotations
from typing import Any
from .sources import SourceRecord, SourceQualityAssessor, analyze_source_independence

MAX_DOSSIER_RECORDS = 2000
MAX_REVIEW_RECORDS = 1000


class EvidenceQualityMatrix:
    """Summarize recorded source metadata and review coverage without truth scoring."""

    @staticmethod
    def _source_record(item: dict[str, Any]) -> SourceRecord:
        metadata = item.get("metadata") or {}
        return SourceRecord(
            source_id=str(item.get("source_id", "")), title=str(item.get("title", "")),
            url=str(item.get("url", "")), source_type=str(item.get("source_type", "unknown")),
            peer_reviewed=bool(metadata.get("peer_reviewed", False)),
            primary_source=bool(metadata.get("primary_source", False)),
            methods_available=bool(metadata.get("methods_available", False)),
            publication_date_known=bool(metadata.get("publication_date_known", False)),
            limitations=tuple(metadata.get("limitations", [])), doi=str(item.get("doi", "")),
            authors=tuple(item.get("authors", [])), institutions=tuple(item.get("institutions", [])),
            dataset_ids=tuple(item.get("dataset_ids", [])),
            related_source_ids=tuple(item.get("related_source_ids", [])),
            provenance_group=str(item.get("provenance_group", "")),
        )

    @staticmethod
    def _provenance_audit(dossier: dict[str, Any]) -> dict[str, Any]:
        collections = {
            "sources": (dossier.get("sources", []), "source_id"),
            "protocols": (dossier.get("protocols", []), "protocol_id"),
            "runs": (dossier.get("runs", []), "run_id"),
            "datasets": (dossier.get("datasets", []), "dataset_id"),
            "comparisons": (dossier.get("comparisons", []), "comparison_id"),
        }
        known, duplicates = {}, []
        for name, (records, id_field) in collections.items():
            if not isinstance(records, list) or len(records) > MAX_DOSSIER_RECORDS:
                raise ValueError(f"dossier {name} must be a list of at most {MAX_DOSSIER_RECORDS} records")
            identifiers = [str(item.get(id_field, "")).strip() for item in records if isinstance(item, dict)]
            counts = {}
            for identifier in identifiers:
                if identifier:
                    counts[identifier] = counts.get(identifier, 0) + 1
            duplicates.extend(
                {"collection": name, "identifier": identifier, "count": count}
                for identifier, count in sorted(counts.items()) if count > 1
            )
            known[name] = set(counts)
        unresolved, declared, resolved = [], 0, 0

        def check(owner: str, field: str, target: str, value: Any):
            nonlocal declared, resolved
            values = list(value) if isinstance(value, (list, tuple, set)) else [value]
            for raw in values:
                if raw is None or raw == "":
                    continue
                declared += 1
                reference = str(raw)
                if reference in known.get(target, set()):
                    resolved += 1
                else:
                    unresolved.append({"owner": owner, "field": field, "target_collection": target, "reference": reference})

        for item in collections["sources"][0]:
            if isinstance(item, dict):
                check(str(item.get("source_id", "")), "related_source_ids", "sources", item.get("related_source_ids", []))
        for item in collections["protocols"][0]:
            if isinstance(item, dict):
                check(str(item.get("protocol_id", "")), "source_ids", "sources", item.get("source_ids", []))
        for item in collections["runs"][0]:
            if isinstance(item, dict):
                check(str(item.get("run_id", "")), "protocol_id", "protocols", item.get("protocol_id"))
                check(str(item.get("run_id", "")), "source_ids", "sources", item.get("source_ids", []))
                check(str(item.get("run_id", "")), "dataset_ids", "datasets", item.get("dataset_ids", []))
        for item in collections["datasets"][0]:
            if isinstance(item, dict):
                check(str(item.get("dataset_id", "")), "source_ids", "sources", item.get("source_ids", []))
        for item in collections["comparisons"][0]:
            if isinstance(item, dict):
                check(str(item.get("comparison_id", "")), "left_run_id", "runs", item.get("left_run_id"))
                check(str(item.get("comparison_id", "")), "right_run_id", "runs", item.get("right_run_id"))
        return {
            "declared_reference_count": declared, "resolved_reference_count": resolved,
            "unresolved_reference_count": len(unresolved), "unresolved_references": unresolved,
            "duplicate_identifiers": duplicates,
            "provenance_completeness": resolved / declared if declared else None,
            "all_declared_references_resolve": not unresolved,
            "identifier_uniqueness": not duplicates, "automatic_repair": False,
        }

    def analyze(self, dossier: dict[str, Any], reviews: list[dict[str, Any]]) -> dict[str, Any]:
        if not isinstance(dossier, dict):
            raise ValueError("dossier must be a dictionary")
        if not isinstance(reviews, list) or len(reviews) > MAX_REVIEW_RECORDS or any(not isinstance(item, dict) for item in reviews):
            raise ValueError(f"reviews must be a list of at most {MAX_REVIEW_RECORDS} dictionaries")
        raw_sources = dossier.get("sources", [])
        if not isinstance(raw_sources, list) or len(raw_sources) > MAX_DOSSIER_RECORDS or any(not isinstance(item, dict) for item in raw_sources):
            raise ValueError(f"dossier sources must be a list of at most {MAX_DOSSIER_RECORDS} dictionaries")
        assessor, source_assessments = SourceQualityAssessor(), []
        for item in raw_sources:
            try:
                assessment = assessor.assess(self._source_record(item))
            except (TypeError, ValueError, AttributeError):
                source_assessments.append({"source_id": item.get("source_id"), "assessment": "incomplete_source_metadata", "score": None, "tier": "not_assessed", "factors": []})
                continue
            source_assessments.append({
                "source_id": assessment.source_id, "assessment": "rubric_metadata_assessment",
                "score": assessment.score, "tier": assessment.tier,
                "factors": list(assessment.factors), "warning": assessment.warning,
            })
        independence = analyze_source_independence(raw_sources)
        verdicts = sorted({str(item.get("verdict", "unknown")) for item in reviews})
        reviewer_ids = [str(item.get("reviewer_id", "")).strip() for item in reviews]
        nonempty_reviewers = [item for item in reviewer_ids if item]
        review_coverage = {
            "review_count": len(reviews), "reviewer_count": len(set(nonempty_reviewers)),
            "verdicts_recorded": verdicts,
            "conflict_declarations_complete": all(item.get("conflict_status") in {"none_declared", "potential", "confirmed"} for item in reviews),
            "missing_reviewer_id_count": sum(not item for item in reviewer_ids),
            "repeated_reviewer_id_count": len(nonempty_reviewers) - len(set(nonempty_reviewers)),
            "multiple_positions_recorded": len(verdicts) > 1,
            "independent_review_established": False,
        }
        categories = {
            "sources": len(raw_sources), "protocols": len(dossier.get("protocols", [])),
            "runs": len(dossier.get("runs", [])), "datasets": len(dossier.get("datasets", [])),
            "comparisons": len(dossier.get("comparisons", [])),
            "peer_review_records_in_dossier": len(dossier.get("peer_reviews", [])),
            "scientific_board_reviews": len(reviews),
        }
        return {
            "dossier_id": dossier.get("dossier_id"), "record_counts": categories,
            "source_assessments": source_assessments, "source_independence": independence,
            "review_coverage": review_coverage, "provenance_integrity": self._provenance_audit(dossier),
            "limitations_recorded": sum(1 for item in raw_sources if (item.get("metadata") or {}).get("limitations")),
            "missing_areas": [key for key in ("sources", "protocols", "runs", "datasets", "comparisons") if categories[key] == 0],
            "scientific_validity_established": False, "evidence_quality_score": None,
            "notice": (
                "Source rubric scores describe declared metadata only; they are not probabilities of truth "
                "or scores for the dossier as a whole. Missing records may exist outside this dossier. "
                "Recorded reviewer count does not prove reviewer independence. Provenance diagnostics "
                "identify unresolved declared links; they do not repair them."
            ),
        }

    def build(self, store: Any, dossier_id: str | None = None, limit: int = 100) -> dict[str, Any]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 200:
            raise ValueError("limit must be an integer between 1 and 200")
        from .evidence_dossiers import EvidenceDossierService
        from .scientific_review_board import ScientificReviewBoard
        dossiers = EvidenceDossierService(store)
        selected = [dossiers.get(dossier_id)] if dossier_id else dossiers.overview(limit=limit)["dossiers"]
        board, reports = ScientificReviewBoard(store), []
        for item in selected:
            full = dossiers.get(item["dossier_id"])
            reviews = board.report(dossier_id=item["dossier_id"], limit=500).get("reviews", [])
            reports.append(self.analyze(full, reviews))
        return {
            "dossiers": reports, "count": len(reports), "read_only": True,
            "scientific_validity_established": False, "automatic_adjudication": False,
        }

"""Consolidated, read-only overview of recorded SSSWET research activity."""
from __future__ import annotations

from collections import Counter
from typing import Any


class ResearchKnowledgeObservatory:
    """Aggregate existing research registries without scoring scientific truth."""

    @staticmethod
    def summarize(knowledge_graph: dict[str, Any], technology_report: dict[str, Any],
                  lab_report: dict[str, Any], dossier_report: dict[str, Any]) -> dict[str, Any]:
        nodes = knowledge_graph.get("nodes", [])
        edges = knowledge_graph.get("edges", [])
        technologies = technology_report.get("technologies", [])
        maturity = Counter(item.get("recorded_maturity", "unknown") for item in technologies)
        dossiers = dossier_report.get("dossiers", [])
        return {
            "overview": {
                "technology_programmes": technology_report.get("count", len(technologies)),
                "knowledge_nodes": len(nodes),
                "recorded_knowledge_relationships": len(edges),
                "protocol_versions": lab_report.get("protocol_count", 0),
                "research_runs": lab_report.get("run_count", 0),
                "recorded_comparisons": lab_report.get("comparison_count", 0),
                "evidence_dossiers": dossier_report.get("count", len(dossiers)),
            },
            "technology_record_maturity": dict(sorted(maturity.items())),
            "technologies_without_project_records": sorted(
                item.get("technology") for item in technologies
                if item.get("recorded_maturity") == "no_project_records"
            ),
            "laboratory_record_integrity": lab_report.get("integrity", {}),
            "evidence_dossiers": [
                {key: item.get(key) for key in (
                    "dossier_id", "title", "status", "verification_state",
                    "source_count", "run_count", "comparison_count", "event_count"
                )}
                for item in dossiers
            ],
            "provenance": {
                "knowledge_graph_is_explicit": True,
                "technology_maturity_is_recorded_metadata": True,
                "laboratory_integrity_is_record_integrity_only": True,
                "dossier_review_is_distinct_from_verification": True,
            },
            "scientific_validity_established": False,
            "technical_feasibility_established": False,
            "automatic_adjudication": False,
            "automatic_experiment_execution": False,
            "notice": (
                "This observatory aggregates records already stored by SSSWET. Counts describe "
                "the retrieved records, not the completeness of external research. Recorded "
                "maturity, integrity checks and review states do not establish scientific truth, "
                "technical feasibility, safety or product readiness."
            ),
        }

    def build(self, store: Any, limit: int = 200) -> dict[str, Any]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 500:
            raise ValueError("limit must be an integer between 1 and 500")
        from .digital_lab import DigitalLabService
        from .evidence_dossiers import EvidenceDossierService
        from .technology_feasibility import TechnologyFeasibilityObservatory
        return self.summarize(
            store.knowledge_graph(limit=500),
            TechnologyFeasibilityObservatory(store).build(),
            DigitalLabService(store).overview(limit=limit),
            EvidenceDossierService(store).overview(limit=limit),
        )

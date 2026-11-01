"""Unified, explainable synthesis of cross-campaign research opportunities.

This service combines recorded graph gaps and possible interdisciplinary links.
It proposes review leads only: it never changes the graph, creates tasks, or
establishes scientific validity.
"""
from __future__ import annotations

import hashlib
import json

from .research_gaps import ResearchGapAnalyzer
from .research_relations import ResearchRelationDiscovery


_PRIORITY = {"high": 0, "medium": 1, "low": 2}


class ResearchOpportunitySynthesizer:
    """Combine existing discovery signals into traceable review opportunities."""

    def __init__(self, store):
        self.store = store

    @staticmethod
    def _identifier(kind: str, references: list[str]) -> str:
        payload = json.dumps(
            [kind, sorted(set(references))], ensure_ascii=False, separators=(",", ":")
        )
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]
        return f"opportunity:{kind}:{digest}"

    def build(self, limit: int = 100) -> dict:
        bounded_limit = max(1, min(int(limit), 500))
        graph = self.store.knowledge_graph(limit=2000)
        nodes = {item["node_id"]: item for item in graph.get("nodes", [])}
        gaps = ResearchGapAnalyzer().report(graph).get("gaps", [])
        relations = ResearchRelationDiscovery(self.store).discover(
            limit=500, minimum_shared_terms=2
        ).get("suggestions", [])

        opportunities = []
        for gap in gaps:
            node_ids = sorted(set(gap.get("node_ids", [])))
            campaigns = sorted({
                str((nodes.get(node_id, {}).get("metadata") or {}).get("campaign_id")
                    or nodes.get(node_id, {}).get("campaign_id") or "")
                for node_id in node_ids
                if ((nodes.get(node_id, {}).get("metadata") or {}).get("campaign_id")
                    or nodes.get(node_id, {}).get("campaign_id"))
            })
            opportunities.append({
                "opportunity_id": self._identifier("research_gap", node_ids + [gap["gap_id"]]),
                "kind": "research_gap",
                "priority": gap["priority"],
                "priority_rank": _PRIORITY[gap["priority"]],
                "title": gap["title"],
                "summary": gap["reason"],
                "suggested_action": gap["suggested_action"],
                "graph_node_ids": node_ids,
                "campaign_ids": campaigns,
                "related_opportunity_ids": [],
                "evidence_references": [gap["gap_id"]],
                "discovery_method": "knowledge_graph_gap_analysis",
                "score": {"priority_order": _PRIORITY[gap["priority"]]},
            })

        relation_opportunities = []
        for relation in relations:
            node_ids = sorted({
                relation["source_node_id"], relation["target_node_id"]
            })
            opportunity = {
                "opportunity_id": self._identifier("interdisciplinary_link", node_ids),
                "kind": "interdisciplinary_link",
                "priority": "medium",
                "priority_rank": 1,
                "title": f"Possible link: {relation['source_label']} ↔ {relation['target_label']}",
                "summary": relation["rationale"],
                "suggested_action": (
                    "Compare the original sources, definitions, assumptions, methods "
                    "and boundary conditions before deciding whether the link is meaningful."
                ),
                "graph_node_ids": node_ids,
                "campaign_ids": sorted({
                    relation["source_campaign_id"], relation["target_campaign_id"]
                }),
                "related_opportunity_ids": [],
                "evidence_references": [relation["suggestion_id"]],
                "shared_terms": relation["shared_terms"],
                "overlap_score": relation["overlap_score"],
                "discovery_method": relation["method"],
                "score": {"lexical_overlap": relation["overlap_score"]},
            }
            relation_opportunities.append(opportunity)
            opportunities.append(opportunity)

        # Link gap reviews to any interdisciplinary lead involving the same node.
        for gap_opportunity in opportunities:
            if gap_opportunity["kind"] != "research_gap":
                continue
            gap_nodes = set(gap_opportunity["graph_node_ids"])
            gap_opportunity["related_opportunity_ids"] = sorted(
                item["opportunity_id"] for item in relation_opportunities
                if gap_nodes.intersection(item["graph_node_ids"])
            )

        opportunities.sort(key=lambda item: (
            item["priority_rank"],
            -item.get("overlap_score", 0.0),
            item["opportunity_id"],
        ))
        selected = opportunities[:bounded_limit]
        return {
            "opportunities": selected,
            "total": len(opportunities),
            "returned": len(selected),
            "signal_counts": {
                "research_gaps": len(gaps),
                "interdisciplinary_links": len(relation_opportunities),
            },
            "synthesis_method": "deterministic combination of graph-gap analysis and normalized lexical overlap",
            "requires_human_review": True,
            "automatic_task_creation": False,
            "graph_mutated": False,
            "scientific_validity_established": False,
            "limitations": [
                "A missing graph relationship is not proof that evidence does not exist.",
                "Lexical overlap may be coincidental and may miss synonyms or conceptual links.",
                "Priority and overlap scores rank review leads; they are not probabilities, confidence values or measures of scientific truth.",
                "Researchers must inspect primary sources, methods, provenance, uncertainty and safety before acting.",
            ],
        }

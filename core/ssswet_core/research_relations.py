"""Explainable, review-only discovery of possible interdisciplinary links."""
from __future__ import annotations

import re
from itertools import combinations


_STOP = {
    "about", "after", "also", "among", "and", "are", "because", "been",
    "between", "could", "data", "does", "from", "have", "into", "more",
    "other", "over", "same", "should", "some", "such", "than", "that",
    "their", "them", "there", "these", "they", "this", "those", "through",
    "under", "using", "very", "were", "what", "when", "where", "which",
    "while", "with", "within", "would", "your",
}


def _terms(value: str) -> set[str]:
    return {
        token for token in re.findall(r"[a-z0-9]{3,}", value.lower())
        if token not in _STOP
    }


class ResearchRelationDiscovery:
    """Find lexical overlaps between distinct research campaigns.

    Suggestions are explainable leads for human review, never graph edges or
    evidence of scientific connection.
    """

    def __init__(self, store):
        self.store = store

    def discover(self, limit: int = 100, minimum_shared_terms: int = 2) -> dict:
        bounded_limit = max(1, min(int(limit), 500))
        minimum = max(2, min(int(minimum_shared_terms), 10))
        graph = self.store.knowledge_graph(limit=2000)
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        existing = {
            frozenset((edge["source_id"], edge["target_id"]))
            for edge in edges
            if edge.get("relation") in {"related_to", "supports", "contradicts", "derived_from"}
        }
        indexed = []
        for node in nodes:
            metadata = node.get("metadata") or {}
            campaign = metadata.get("campaign_id") or node.get("campaign_id") or ""
            domain = metadata.get("domain") or metadata.get("research_domain") or ""
            text = " ".join((node.get("label", ""), node.get("description", "")))
            terms = _terms(text)
            if terms and campaign:
                indexed.append((node, campaign, str(domain), terms))

        suggestions = []
        for left, right in combinations(indexed, 2):
            a, campaign_a, domain_a, terms_a = left
            b, campaign_b, domain_b, terms_b = right
            if campaign_a == campaign_b or a["node_id"] == b["node_id"]:
                continue
            if frozenset((a["node_id"], b["node_id"])) in existing:
                continue
            shared = sorted(terms_a & terms_b)
            if len(shared) < minimum:
                continue
            union = terms_a | terms_b
            score = round(len(shared) / len(union), 4) if union else 0.0
            suggestions.append({
                "suggestion_id": "::".join(sorted((a["node_id"], b["node_id"]))),
                "source_node_id": a["node_id"],
                "target_node_id": b["node_id"],
                "source_label": a["label"],
                "target_label": b["label"],
                "source_campaign_id": campaign_a,
                "target_campaign_id": campaign_b,
                "source_domain": domain_a,
                "target_domain": domain_b,
                "shared_terms": shared,
                "overlap_score": score,
                "method": "normalized lexical Jaccard overlap",
                "rationale": "Both records contain the listed terms; inspect their context and methods before deciding whether a meaningful connection exists.",
                "requires_human_review": True,
                "graph_edge_created": False,
                "scientific_validity_established": False,
            })
        suggestions.sort(key=lambda item: (
            -item["overlap_score"], item["source_node_id"], item["target_node_id"]
        ))
        return {
            "suggestions": suggestions[:bounded_limit],
            "suggestion_count": min(len(suggestions), bounded_limit),
            "candidates_examined": len(indexed),
            "method": "normalized lexical Jaccard overlap",
            "automatic_graph_changes": False,
            "scientific_validity_established": False,
            "limitations": [
                "Lexical overlap can be coincidental or miss synonyms and conceptual links.",
                "Campaign metadata and descriptions are supplied by researchers.",
                "Every suggestion requires contextual, methodological and source review.",
            ],
        }

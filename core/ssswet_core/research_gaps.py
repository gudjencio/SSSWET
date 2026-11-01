"""Deterministic research-gap analysis over an explicit knowledge graph.

This module proposes review work; it never changes node verification states
or asserts that a missing edge proves the absence of real-world evidence.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class ResearchGap:
    gap_id: str
    category: str
    priority: str
    node_ids: tuple[str, ...]
    title: str
    reason: str
    suggested_action: str


class ResearchGapAnalyzer:
    """Identify graph-level omissions that deserve a human or agent review."""

    def analyze(self, graph: dict) -> list[ResearchGap]:
        nodes = {item["node_id"]: item for item in graph.get("nodes", [])}
        edges = [
            edge for edge in graph.get("edges", [])
            if edge.get("source_id") in nodes and edge.get("target_id") in nodes
        ]
        incoming: dict[str, list[dict]] = {key: [] for key in nodes}
        outgoing: dict[str, list[dict]] = {key: [] for key in nodes}
        for edge in edges:
            incoming[edge["target_id"]].append(edge)
            outgoing[edge["source_id"]].append(edge)

        gaps: list[ResearchGap] = []

        def add(category: str, priority: str, node_ids: tuple[str, ...],
                title: str, reason: str, action: str) -> None:
            stable_ids = tuple(sorted(set(node_ids)))
            identity = "|".join((category, *stable_ids))
            gaps.append(ResearchGap(
                gap_id=f"gap:{category}:{identity}",
                category=category,
                priority=priority,
                node_ids=stable_ids,
                title=title,
                reason=reason,
                suggested_action=action,
            ))

        for node_id, node in nodes.items():
            kind = node.get("node_type")
            label = node.get("label", node_id)
            ins, outs = incoming[node_id], outgoing[node_id]

            if kind == "hypothesis":
                support = [e for e in ins if e["relation"] == "supports"]
                refute = [e for e in ins if e["relation"] == "contradicts"]
                tests = [
                    e for e in ins + outs
                    if e["relation"] == "tests"
                ]
                if support and refute:
                    linked = [e["source_id"] for e in support + refute] + [node_id]
                    add("unresolved_contradiction", "high", tuple(linked),
                        f"Contradictory evidence around: {label}",
                        "The graph contains both supporting and contradicting relationships; their methods, provenance and scope have not been reconciled.",
                        "Assign an independent review to compare source provenance, methods, populations, assumptions and uncertainty.")
                if not support:
                    add("missing_support", "high", (node_id,),
                        f"No supporting source linked: {label}",
                        "No incoming 'supports' relationship is recorded in this graph. This does not prove that no supporting research exists.",
                        "Search primary literature and datasets, then register traceable sources and explicitly assessed relationships.")
                if not tests:
                    add("untested_hypothesis", "medium", (node_id,),
                        f"No experiment linked: {label}",
                        "No experiment is currently connected through a 'tests' relationship.",
                        "Define a falsifiable prediction, controls, measurable outcomes and a safe reproducible test plan.")
                state = str(node.get("verification_state", "unverified")).casefold()
                if state not in {"independently_verified", "reproduced", "rejected"}:
                    add("verification_pending", "medium", (node_id,),
                        f"Verification still pending: {label}",
                        f"The recorded state is '{state}', which is not an independently verified or reproduced result.",
                        "Obtain independent evidence with assessed provenance; require real-world expert validation where applicable.")

            elif kind == "question" and not any(e["relation"] == "answers" for e in ins + outs):
                add("unanswered_question", "medium", (node_id,),
                    f"Question without an answer link: {label}",
                    "No 'answers' relationship is recorded for this question.",
                    "Break the question into testable subquestions and link relevant findings or sources when assessed.")

            elif kind == "experiment" and not any(e["relation"] == "tests" for e in ins + outs):
                add("unlinked_experiment", "low", (node_id,),
                    f"Experiment not linked to a hypothesis: {label}",
                    "No 'tests' relationship connects this experiment to a graph node.",
                    "Document the hypothesis, protocol, controls and outcomes this experiment is intended to evaluate.")

            elif kind == "finding" and not any(
                e["relation"] in {"derived_from", "supports", "contradicts"}
                for e in ins + outs
            ):
                add("finding_without_provenance", "high", (node_id,),
                    f"Finding without a provenance link: {label}",
                    "No source or derivation relationship is recorded for this finding.",
                    "Attach the original source, dataset or derivation and preserve exact identifiers.")

        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(gaps, key=lambda gap: (
            priority_order[gap.priority], gap.category, gap.gap_id
        ))

    def report(self, graph: dict) -> dict:
        gaps = self.analyze(graph)
        counts = {level: sum(g.priority == level for g in gaps)
                  for level in ("high", "medium", "low")}
        return {
            "gaps": [gap.__dict__.copy() for gap in gaps],
            "total": len(gaps),
            "priority_counts": counts,
            "notice": (
                "Graph gaps indicate missing recorded relationships, not proof "
                "that evidence, experiments or answers do not exist outside this graph. "
                "No verification state is changed automatically."
            ),
        }

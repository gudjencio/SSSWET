"""Persistent, explicit knowledge graph for research claims and evidence.

Edges record declared relationships; they are not proof that a claim is true.
"""
from dataclasses import dataclass
from datetime import datetime, timezone


NODE_TYPES = {
    "hypothesis", "finding", "source", "dataset", "experiment",
    "question", "method", "concept",
}
RELATIONS = {
    "supports", "contradicts", "derived_from", "tests", "uses_dataset",
    "related_to", "answers", "requires_verification",
}


@dataclass(frozen=True)
class KnowledgeNode:
    node_id: str
    node_type: str
    label: str
    description: str = ""
    verification_state: str = "unverified"
    metadata: dict | None = None
    created_at: str = ""


@dataclass(frozen=True)
class KnowledgeEdge:
    source_id: str
    target_id: str
    relation: str
    note: str = ""
    confidence: float = 0.0
    created_at: str = ""


def validate_node(node: KnowledgeNode) -> None:
    if not node.node_id.strip() or not node.label.strip():
        raise ValueError("node_id and label must not be empty")
    if node.node_type not in NODE_TYPES:
        raise ValueError(f"Unsupported node_type: {node.node_type}")
    if not 0.0 <= float(node.metadata.get("confidence", 0.0) if node.metadata else 0.0) <= 1.0:
        raise ValueError("metadata confidence must be between 0 and 1")


def validate_edge(edge: KnowledgeEdge) -> None:
    if not edge.source_id.strip() or not edge.target_id.strip():
        raise ValueError("edge endpoints must not be empty")
    if edge.source_id == edge.target_id:
        raise ValueError("self-referencing edges are not allowed")
    if edge.relation not in RELATIONS:
        raise ValueError(f"Unsupported relation: {edge.relation}")
    if not 0.0 <= float(edge.confidence) <= 1.0:
        raise ValueError("edge confidence must be between 0 and 1")

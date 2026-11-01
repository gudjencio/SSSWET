"""Immutable, versioned research memory linked to explicit evidence records.

A workflow status is not a scientific verification status. Every revision is
stored as a new snapshot; prior versions are never edited or deleted.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Iterable


MEMORY_VERSION_STATES = {"candidate", "reviewed", "contested", "archived"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _tokens(value: str) -> set[str]:
    return {part.casefold() for part in re.findall(r"[\w']{2,}", value, flags=re.UNICODE)}


@dataclass(frozen=True)
class ScientificMemoryVersion:
    version_id: str
    memory_key: str
    topic: str
    statement: str
    campaign_id: str = ""
    graph_node_ids: tuple[str, ...] = ()
    experiment_ids: tuple[str, ...] = ()
    source_ids: tuple[str, ...] = ()
    provenance_group: str = ""
    status: str = "candidate"
    review_note: str = ""
    supersedes_version_id: str = ""
    created_at: str = ""

    def __post_init__(self) -> None:
        for field_name in ("version_id", "memory_key", "topic", "statement"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} is required")
        if self.status not in MEMORY_VERSION_STATES:
            raise ValueError("Unsupported scientific-memory state")
        for field_name in ("graph_node_ids", "experiment_ids", "source_ids"):
            values = getattr(self, field_name)
            if len(set(values)) != len(values) or any(not item.strip() for item in values):
                raise ValueError(f"{field_name} must contain unique, non-empty identifiers")
        if self.supersedes_version_id and not self.review_note.strip():
            raise ValueError("A review note is required when superseding a version")

    @classmethod
    def create(
        cls, version_id: str, memory_key: str, topic: str, statement: str, *,
        campaign_id: str = "", graph_node_ids: Iterable[str] = (),
        experiment_ids: Iterable[str] = (), source_ids: Iterable[str] = (),
        provenance_group: str = "", status: str = "candidate",
        review_note: str = "", supersedes_version_id: str = "",
    ) -> "ScientificMemoryVersion":
        return cls(
            version_id=version_id, memory_key=memory_key, topic=topic,
            statement=statement, campaign_id=campaign_id,
            graph_node_ids=tuple(graph_node_ids),
            experiment_ids=tuple(experiment_ids), source_ids=tuple(source_ids),
            provenance_group=provenance_group, status=status,
            review_note=review_note.strip(),
            supersedes_version_id=supersedes_version_id,
            created_at=_now(),
        )


def version_to_dict(version: ScientificMemoryVersion) -> dict:
    payload = asdict(version)
    for field in ("graph_node_ids", "experiment_ids", "source_ids"):
        payload[field] = list(payload[field])
    return payload


class ScientificMemoryService:
    def __init__(self, store) -> None:
        self.store = store

    def add_version(self, version: ScientificMemoryVersion) -> dict:
        return self.store.add_scientific_memory_version(version)

    def revise(
        self, previous_version_id: str, version_id: str, *,
        statement: str | None = None, topic: str | None = None,
        status: str = "candidate", review_note: str,
    ) -> dict:
        previous = self.store.get_scientific_memory_version(previous_version_id)
        if previous is None:
            raise ValueError("The version to revise does not exist")
        return self.add_version(ScientificMemoryVersion.create(
            version_id, previous["memory_key"], topic or previous["topic"],
            statement if statement is not None else previous["statement"],
            campaign_id=previous.get("campaign_id", ""),
            graph_node_ids=previous.get("graph_node_ids", ()),
            experiment_ids=previous.get("experiment_ids", ()),
            source_ids=previous.get("source_ids", ()),
            provenance_group=previous.get("provenance_group", ""),
            status=status, review_note=review_note,
            supersedes_version_id=previous_version_id,
        ))

    def overview(self, query: str = "", limit: int = 200) -> dict:
        versions = self.store.scientific_memory_history(limit=limit)
        graph = self.store.knowledge_graph(limit=2000)
        contradiction_nodes = set()
        for edge in graph["edges"]:
            if edge["relation"] == "contradicts":
                contradiction_nodes.update((edge["source_id"], edge["target_id"]))
        latest_by_key: dict[str, str] = {}
        for item in reversed(versions):
            latest_by_key.setdefault(item["memory_key"], item["version_id"])
        enriched = []
        for item in versions:
            linked = set(item.get("graph_node_ids", []))
            contested_links = sorted(linked & contradiction_nodes)
            item = {
                **item,
                "is_current": latest_by_key.get(item["memory_key"]) == item["version_id"],
                "contested_by_graph": bool(contested_links),
                "contested_graph_node_ids": contested_links,
                "potentially_outdated": latest_by_key.get(item["memory_key"]) != item["version_id"],
                "scientific_validity_established": False,
            }
            enriched.append(item)
        if query.strip():
            terms = _tokens(query)
            ranked = []
            for item in enriched:
                words = _tokens(" ".join((
                    item["topic"], item["statement"], item["campaign_id"],
                    " ".join(item["source_ids"]), " ".join(item["graph_node_ids"]),
                    " ".join(item["experiment_ids"]),
                )))
                overlap = terms & words
                if overlap:
                    ranked.append((len(overlap) / len(terms), item))
            ranked.sort(key=lambda pair: (pair[0], pair[1]["created_at"]), reverse=True)
            enriched = [
                {**item, "matched_terms": sorted(terms & _tokens(
                    item["topic"] + " " + item["statement"]
                )), "retrieval_method": "lexical_overlap"}
                for _, item in ranked
            ]
        return {
            "versions": enriched[:max(1, min(int(limit), 500))],
            "total_versions": len(enriched),
            "current_versions": sum(1 for item in enriched if item["is_current"]),
            "contested_versions": sum(1 for item in enriched if item["contested_by_graph"]),
            "retrieval_method": "lexical_overlap" if query.strip() else "chronological",
            "scientific_validity_established": False,
            "automatic_adjudication": False,
        }

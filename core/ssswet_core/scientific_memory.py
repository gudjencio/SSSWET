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

    def lineage(self, version_id: str) -> dict | None:
        """Explain the complete revision chain without judging scientific truth."""
        selected = self.store.get_scientific_memory_version(version_id)
        if selected is None:
            return None
        history = self.store.scientific_memory_history_for_key(selected["memory_key"])
        selected_index = next(
            (index for index, item in enumerate(history)
             if item["version_id"] == version_id),
            None,
        )
        if selected_index is None:
            return None
        current = history[-1]
        return {
            "memory_key": selected["memory_key"],
            "topic": selected["topic"],
            "selected_version_id": version_id,
            "selected_version_number": selected["version_number"],
            "is_current": version_id == current["version_id"],
            "predecessors": history[:selected_index],
            "selected_version": selected,
            "successors": history[selected_index + 1:],
            "current_version_id": current["version_id"],
            "version_count": len(history),
            "revision_chain_is_complete": True,
            "scientific_validity_established": False,
            "automatic_adjudication": False,
        }

    def lineage_page(
        self, version_id: str, *, limit: int = 50,
        before_version_number: int | None = None,
    ) -> dict | None:
        """Return one bounded page of a version's predecessor history."""
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
            raise ValueError("limit must be an integer between 1 and 100")
        selected = self.store.get_scientific_memory_version(version_id)
        if selected is None:
            return None
        cursor = before_version_number
        if cursor is None:
            cursor = int(selected["version_number"]) + 1
        elif cursor > int(selected["version_number"]) + 1:
            raise ValueError("before_version_number cannot be later than the selected version")
        page = self.store.scientific_memory_history_page_for_key(
            selected["memory_key"], before_version_number=cursor, limit=limit + 1
        )
        raw_items = page["items"]
        has_more = len(raw_items) > limit
        items = raw_items[:limit]
        next_cursor = items[-1]["version_number"] if has_more and items else None
        latest = self.store.scientific_memory_history_page_for_key(
            selected["memory_key"], before_version_number=None, limit=1
        )["items"]
        return {
            "memory_key": selected["memory_key"],
            "selected_version": selected,
            "items": items,
            "page_order": "newest_to_oldest",
            "page_count": len(items),
            "total_versions": page["total_count"],
            "current_version_id": latest[0]["version_id"] if latest else "",
            "has_more_predecessors": has_more,
            "next_before_version_number": next_cursor,
            "revision_chain_is_complete": not has_more,
            "retrieval_is_sql_bounded": True,
            "scientific_validity_established": False,
            "automatic_adjudication": False,
        }

    def evolution_alerts(self, limit: int = 500) -> dict:
        """Flag current memories challenged by later graph evidence for human review."""
        versions = self.store.scientific_memory_history(limit=limit)
        graph = self.store.knowledge_graph(limit=2000)
        nodes = {node["node_id"]: node for node in graph["nodes"]}
        latest_by_key: dict[str, str] = {}
        for version in reversed(versions):
            latest_by_key.setdefault(version["memory_key"], version["version_id"])

        alerts = []
        for version in versions:
            if latest_by_key.get(version["memory_key"]) != version["version_id"]:
                continue
            for edge in graph["edges"]:
                if edge["relation"] != "contradicts":
                    continue
                linked_id = None
                later_id = None
                if edge["source_id"] in version.get("graph_node_ids", []):
                    linked_id, later_id = edge["source_id"], edge["target_id"]
                elif edge["target_id"] in version.get("graph_node_ids", []):
                    linked_id, later_id = edge["target_id"], edge["source_id"]
                if not linked_id or later_id not in nodes:
                    continue
                later_node = nodes[later_id]
                linked_node = nodes.get(linked_id, {})
                memory_time = version.get("created_at", "")
                discovery_time = later_node.get("created_at", "")
                if not discovery_time or not memory_time or discovery_time <= memory_time:
                    continue
                alerts.append({
                    "version_id": version["version_id"],
                    "memory_key": version["memory_key"],
                    "topic": version["topic"],
                    "statement": version["statement"],
                    "linked_node_id": linked_id,
                    "linked_node_label": linked_node.get("label", ""),
                    "later_contradicting_node_id": later_id,
                    "later_contradicting_node_label": later_node.get("label", ""),
                    "discovery_recorded_at": discovery_time,
                    "edge_note": edge.get("note", ""),
                    "edge_confidence": edge.get("confidence", 0.0),
                    "suggestion": "Re-examine this hypothesis against the later contradictory record, including methods, provenance, and limitations.",
                    "automatic_status_change": False,
                    "scientific_validity_established": False,
                })
        alerts.sort(key=lambda item: (item["discovery_recorded_at"], item["version_id"]), reverse=True)
        return {
            "alerts": alerts,
            "alert_count": len(alerts),
            "review_required": bool(alerts),
            "automatic_revision": False,
            "scientific_validity_established": False,
        }

    def overview(self, query: str = "", limit: int = 200) -> dict:
        versions = self.store.scientific_memory_history(limit=limit)
        graph = self.store.knowledge_graph(limit=2000)
        graph_node_ids = {node["node_id"] for node in graph["nodes"]}
        source_ids = {source["source_id"] for source in self.store._all_source_records()}
        experiment_ids = {
            item["experiment_id"] for item in self.store.experiment_overview(limit=500)
        }
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
            missing_sources = sorted(set(item.get("source_ids", [])) - source_ids)
            missing_experiments = sorted(set(item.get("experiment_ids", [])) - experiment_ids)
            missing_graph_nodes = sorted(linked - graph_node_ids)
            missing_links = {
                "source_ids": missing_sources,
                "experiment_ids": missing_experiments,
                "graph_node_ids": missing_graph_nodes,
            }
            item = {
                **item,
                "is_current": latest_by_key.get(item["memory_key"]) == item["version_id"],
                "contested_by_graph": bool(contested_links),
                "contested_graph_node_ids": contested_links,
                "potentially_outdated": latest_by_key.get(item["memory_key"]) != item["version_id"],
                "missing_links": missing_links,
                "has_missing_links": any(missing_links.values()),
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
            "versions_with_missing_links": sum(1 for item in enriched if item["has_missing_links"]),
            "missing_link_counts": {
                "source_ids": sum(len(item["missing_links"]["source_ids"]) for item in enriched),
                "experiment_ids": sum(len(item["missing_links"]["experiment_ids"]) for item in enriched),
                "graph_node_ids": sum(len(item["missing_links"]["graph_node_ids"]) for item in enriched),
            },
            "retrieval_method": "lexical_overlap" if query.strip() else "chronological",
            "scientific_validity_established": False,
            "automatic_adjudication": False,
        }

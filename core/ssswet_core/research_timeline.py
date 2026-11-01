"""Derived, timestamp-aware chronology of recorded research changes.

Timeline entries are assembled from existing persisted records. Missing dates
are not invented; simulations and observations remain explicitly distinct.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any


def _valid_timestamp(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        return ""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return ""
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=None).isoformat()
    return parsed.isoformat()


class ResearchTimeline:
    def __init__(self, store: object):
        self.store = store

    def build(self, campaign_id: str = "", limit: int = 200) -> dict:
        bounded = max(1, min(int(limit), 1000))
        events: list[dict] = []

        def add(event_id: str, occurred_at: Any, kind: str, title: str,
                description: str, campaign: str = "", references: dict | None = None,
                validity: bool = False) -> None:
            timestamp = _valid_timestamp(occurred_at)
            if not timestamp or (campaign_id and campaign != campaign_id):
                return
            events.append({
                "event_id": event_id, "occurred_at": timestamp,
                "kind": kind, "title": title, "description": description,
                "campaign_id": campaign, "references": references or {},
                "scientific_validity_established": validity,
            })

        graph = self.store.knowledge_graph(limit=2000)
        for node in graph.get("nodes", []):
            metadata = node.get("metadata") or {}
            add(
                "graph-node:" + node["node_id"], node.get("created_at"),
                "knowledge_recorded", node.get("label", node["node_id"]),
                node.get("description", ""), metadata.get("campaign_id", ""),
                {"graph_node_ids": [node["node_id"]],
                 "verification_state": node.get("verification_state", "unverified")},
            )
        for index, edge in enumerate(graph.get("edges", [])):
            add(
                "graph-edge:" + edge["source_id"] + ":" + edge["target_id"] + ":" + edge["relation"],
                edge.get("created_at"), "relationship_recorded", edge["relation"],
                edge.get("note", ""),
                references={"graph_node_ids": [edge["source_id"], edge["target_id"]]},
            )

        for version in self.store.scientific_memory_history(limit=500):
            add(
                "scientific-memory:" + version["version_id"], version.get("created_at"),
                "memory_version", version.get("topic", "Scientific memory"),
                version.get("statement", ""), version.get("campaign_id", ""),
                {"memory_key": version.get("memory_key", ""),
                 "version_id": version["version_id"],
                 "source_ids": version.get("source_ids", []),
                 "experiment_ids": version.get("experiment_ids", []),
                 "graph_node_ids": version.get("graph_node_ids", [])},
            )

        for experiment in self.store.experiment_overview(limit=500):
            experiment_id = experiment.get("experiment_id", "")
            add(
                "experiment-plan:" + experiment_id,
                experiment.get("updated_at"), "experiment_plan_updated",
                experiment_id or "Experiment plan",
                experiment.get("objective", ""),
                references={"experiment_ids": [experiment_id]} if experiment_id else {},
            )
            for record in experiment.get("records", []):
                add(
                    "experiment-record:" + record.get("record_id", ""),
                    record.get("recorded_at"), "experiment_recorded",
                    record.get("record_id", "Experiment record"),
                    record.get("method", ""),
                    references={
                        "experiment_ids": [experiment_id] if experiment_id else [],
                        "source_ids": record.get("source_ids", []),
                        "execution_kind": record.get("kind", ""),
                    },
                )

        for case in self.store.dispute_history(limit=500):
            add(
                "dispute-opened:" + case["case_id"], case.get("created_at"),
                "contradiction_review_opened", "Contradiction review opened",
                case.get("left_label", "") + " ↔ " + case.get("right_label", ""),
                references={"dispute_case_id": case["case_id"],
                            "graph_node_ids": [case.get("left_node_id", ""), case.get("right_node_id", "")]},
            )
            add(
                "dispute-reviewed:" + case["case_id"], case.get("reviewed_at"),
                "contradiction_review_updated", "Contradiction review: " + case.get("state", ""),
                case.get("review_note", ""), references={"dispute_case_id": case["case_id"]},
            )

        for report in self.store.literature_watch_history(limit=500):
            add(
                "literature-watch:" + report["watch_id"], report.get("created_at"),
                "literature_watch", "Literature watch",
                report.get("query", ""),
                references={"watch_id": report["watch_id"],
                            "candidate_count": len(report.get("candidates", []))},
            )

        for campaign in self.store.campaign_history(limit=500):
            add(
                "campaign-update:" + campaign["campaign_id"], campaign.get("updated_at"),
                "campaign_updated", campaign.get("title") or campaign["campaign_id"],
                campaign.get("objective", ""), campaign["campaign_id"],
                {"campaign_id": campaign["campaign_id"], "state": campaign.get("state", "")},
            )

        events.sort(key=lambda event: (event["occurred_at"], event["event_id"]), reverse=True)
        selected = events[:bounded]
        return {
            "events": selected,
            "total_events": len(events),
            "campaign_filter": campaign_id or None,
            "event_kinds": sorted({event["kind"] for event in events}),
            "chronology_is_not_validation": True,
            "undated_records_omitted": True,
        }

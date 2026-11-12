"""Deterministic human-review queue assembled from existing research records."""
from __future__ import annotations

from typing import Any

from .dataset_registry import DatasetRegistry
from .scientific_memory import ScientificMemoryService

MAX_QUEUE_ITEMS = 500
PRIORITY_ORDER = {"critical": 0, "high": 1, "normal": 2}


def build_review_queue(store: Any, *, limit: int = 100) -> dict[str, Any]:
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= MAX_QUEUE_ITEMS:
        raise ValueError(f"limit must be an integer between 1 and {MAX_QUEUE_ITEMS}")

    items: dict[tuple[str, str], dict[str, Any]] = {}

    def add(entity_type: str, entity_id: str, reason: str, priority: str, created_at: str = "", detail: str = ""):
        key = (entity_type, entity_id)
        if key not in items:
            items[key] = {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "priority": priority,
                "reason_codes": [],
                "created_at": created_at,
                "details": [],
                "requires_human_review": True,
            }
        current = items[key]
        if PRIORITY_ORDER[priority] < PRIORITY_ORDER[current["priority"]]:
            current["priority"] = priority
        if reason not in current["reason_codes"]:
            current["reason_codes"].append(reason)
        if detail and detail not in current["details"] and len(current["details"]) < 8:
            current["details"].append(detail)
        if created_at and created_at > current["created_at"]:
            current["created_at"] = created_at

    memory_service = ScientificMemoryService(store)
    overview = memory_service.overview(limit=500)
    for memory in overview.get("versions", []):
        version_id = str(memory.get("version_id", ""))
        if not version_id:
            continue
        if memory.get("contested_by_graph"):
            add("scientific_memory_version", version_id, "linked_graph_contradiction", "critical",
                memory.get("created_at", ""), "A linked graph node participates in a recorded contradiction.")
        missing = memory.get("missing_links", {})
        missing_count = sum(len(missing.get(key, [])) for key in ("source_ids", "experiment_ids", "graph_node_ids"))
        if missing_count:
            add("scientific_memory_version", version_id, "missing_evidence_links", "high",
                memory.get("created_at", ""), f"{missing_count} declared evidence link(s) do not resolve.")
        if memory.get("is_current") and memory.get("status") == "candidate":
            add("scientific_memory_version", version_id, "candidate_waiting_for_review", "normal",
                memory.get("created_at", ""), "Candidate workflow state; not a scientific validity verdict.")

    for alert in memory_service.evolution_alerts(limit=500).get("alerts", []):
        version_id = str(alert.get("version_id", ""))
        if version_id:
            add("scientific_memory_version", version_id, "later_contradiction_recorded", "critical",
                alert.get("discovery_recorded_at", ""), "A later graph record is linked by a contradicts edge.")

    for report in store.literature_watch_history(limit=100):
        for candidate in report.get("candidates", [])[:50]:
            candidate_id = str(candidate.get("candidate_id", ""))
            if not candidate_id:
                continue
            classification = candidate.get("classification")
            if candidate.get("metadata_conflicts"):
                add("literature_candidate", candidate_id, "cross_provider_metadata_conflict", "high",
                    report.get("created_at", ""), "Provider metadata differs for: " + ", ".join(candidate.get("metadata_conflicts", [])))
            if classification == "possible_duplicate":
                add("literature_candidate", candidate_id, "possible_exact_source_duplicate", "high",
                    report.get("created_at", ""), "Compare strong identifiers before registering a new source.")
            elif classification == "possible_title_match":
                add("literature_candidate", candidate_id, "possible_title_similarity", "normal",
                    report.get("created_at", ""), "Title similarity is a review cue, not proof of duplication.")
            elif classification == "candidate_for_review":
                add("literature_candidate", candidate_id, "new_metadata_candidate", "normal",
                    report.get("created_at", ""), "Bibliographic metadata requires source and methods review.")

    dataset_report = DatasetRegistry(store).overview(limit=500)
    for record in dataset_report.get("governance", {}).get("versions", []):
        issues = record.get("issues", [])
        if not issues:
            continue
        dataset_id = str(record.get("dataset_id", ""))
        version = record.get("version")
        if not dataset_id or version is None:
            continue
        entity_id = f"{dataset_id}@{version}"
        priority = "critical" if "consent_withdrawn" in issues else (
            "high" if any(code in issues for code in (
                "consent_review_pending", "consent_or_other_lawful_basis_review_required",
                "public_access_for_personal_data",
            )) else "normal"
        )
        add("dataset_version", entity_id, "dataset_governance_review", priority,
            "", "; ".join(issues))

    ordered = sorted(
        items.values(),
        key=lambda item: (
            -PRIORITY_ORDER[item["priority"]],
            str(item.get("created_at", "")),
            item["entity_type"],
            item["entity_id"],
        ),
        reverse=True,
    )
    for item in ordered:
        item["reason_codes"].sort()
        item["details"].sort()
    selected = ordered[:limit]
    return {
        "items": selected,
        "item_count": len(selected),
        "total_matching_items": len(ordered),
        "omitted_item_count": max(0, len(ordered) - len(selected)),
        "priority_counts": {
            priority: sum(1 for item in ordered if item["priority"] == priority)
            for priority in ("critical", "high", "normal")
        },
        "automatic_task_creation": False,
        "automatic_status_change": False,
        "scientific_validity_established": False,
        "notice": "Priority is a workflow triage cue based on recorded flags; it is not a ranking of scientific truth or legal compliance.",
    }

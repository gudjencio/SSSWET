"""Version-aware change detection for deciding when a review needs refreshing."""
from __future__ import annotations


MAP_FIELDS = (
    "source_digests", "dataset_digests", "method_versions",
    "safety_review_versions", "memory_version_ids",
)
MAX_DEPENDENCIES = 5000


def _mapping(value, field):
    if not isinstance(value, dict) or len(value) > MAX_DEPENDENCIES:
        raise ValueError(f"{field} must be a mapping of at most {MAX_DEPENDENCIES} entries")
    cleaned = {}
    for key, item in value.items():
        if (not isinstance(key, str) or not key.strip() or len(key) > 200
                or not isinstance(item, str) or not item.strip() or len(item) > 300):
            raise ValueError(f"{field} keys and values must be non-empty bounded strings")
        cleaned[key.strip()] = item.strip()
    return cleaned


def compare_review_dependencies(previous: dict, current: dict) -> dict:
    if not isinstance(previous, dict) or not isinstance(current, dict):
        raise ValueError("previous and current dependency snapshots must be dictionaries")
    changes = {}
    for field in MAP_FIELDS:
        before = _mapping(previous.get(field, {}), field)
        after = _mapping(current.get(field, {}), field)
        added = sorted(set(after) - set(before))
        missing = sorted(set(before) - set(after))
        changed = sorted(
            key for key in set(before) & set(after) if before[key] != after[key]
        )
        if added or missing or changed:
            changes[field] = {"added": added, "missing_from_current": missing, "changed": changed}
    trigger_reasons = []
    for field, result in changes.items():
        if result["added"]:
            trigger_reasons.append({"field": field, "reason": "new_dependency"})
        if result["changed"]:
            trigger_reasons.append({"field": field, "reason": "dependency_version_changed"})
        if result["missing_from_current"]:
            trigger_reasons.append({"field": field, "reason": "dependency_missing_needs_review"})
    return {
        "reassessment_recommended": bool(trigger_reasons),
        "changes": changes, "trigger_reasons": trigger_reasons,
        "missing_means_deleted": False,
        "automatic_review_started": False,
        "automatic_claim_status_change": False,
    }

"""Compare recorded Virtual Time Mapping snapshots without inventing observations."""
from __future__ import annotations


def diff_snapshots(previous: list[dict], current: list[dict]) -> dict:
    def key(item: dict) -> tuple[str, str]:
        return str(item.get("source_id", "")), str(item.get("timestamp", ""))
    old = {key(item): item for item in previous}
    new = {key(item): item for item in current}
    added = [new[k] for k in sorted(set(new) - set(old))]
    removed = [old[k] for k in sorted(set(old) - set(new))]
    changed = [{"before": old[k], "after": new[k]} for k in sorted(set(old) & set(new)) if old[k] != new[k]]
    return {"added": added, "removed": removed, "changed": changed, "observation_count_delta": len(new) - len(old), "unrecorded_history_recovered": False}

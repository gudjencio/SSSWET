"""Append-only, hash-linked research checkpoints with explicit diffs."""
from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

def _digest(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

@dataclass(frozen=True)
class ResearchCheckpoint:
    task_id: str
    version: int
    state: str
    source_refs: tuple[str, ...]
    unresolved_questions: tuple[str, ...]
    created_at: str
    previous_digest: str = ""
    digest: str = ""

class CheckpointLedger:
    def __init__(self) -> None:
        self._items: dict[str, list[ResearchCheckpoint]] = {}

    @staticmethod
    def _clean_refs(values, field: str) -> tuple[str, ...]:
        if isinstance(values, (str, bytes)):
            raise TypeError(f"{field} must be a sequence of strings")
        cleaned = []
        for value in values:
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field} must contain non-empty strings")
            if value.strip() not in cleaned:
                cleaned.append(value.strip())
        return tuple(cleaned)

    @staticmethod
    def _payload(checkpoint: ResearchCheckpoint) -> dict:
        return {
            "task_id": checkpoint.task_id, "version": checkpoint.version, "state": checkpoint.state,
            "source_refs": list(checkpoint.source_refs), "unresolved_questions": list(checkpoint.unresolved_questions),
            "created_at": checkpoint.created_at, "previous_digest": checkpoint.previous_digest,
        }

    def save(self, task_id: str, state: str, *, source_refs=(), unresolved_questions=()) -> ResearchCheckpoint:
        if not isinstance(task_id, str) or not task_id.strip():
            raise ValueError("task_id is required")
        if not isinstance(state, str) or not state.strip():
            raise ValueError("state is required")
        history = self._items.setdefault(task_id, [])
        previous = history[-1].digest if history else ""
        checkpoint = ResearchCheckpoint(
            task_id=task_id.strip(), version=len(history) + 1, state=state.strip(),
            source_refs=self._clean_refs(source_refs, "source_refs"),
            unresolved_questions=self._clean_refs(unresolved_questions, "unresolved_questions"),
            created_at=datetime.now(timezone.utc).isoformat(), previous_digest=previous, digest="",
        )
        checkpoint = ResearchCheckpoint(**{**asdict(checkpoint), "digest": _digest(self._payload(checkpoint))})
        history.append(checkpoint)
        return checkpoint

    def latest(self, task_id: str) -> ResearchCheckpoint | None:
        history = self._items.get(task_id, [])
        return history[-1] if history else None

    def history(self, task_id: str) -> list[dict]:
        return [asdict(item) for item in self._items.get(task_id, [])]

    def verify(self, task_id: str) -> dict:
        history = self._items.get(task_id, [])
        issues = []
        previous = ""
        for index, checkpoint in enumerate(history):
            if checkpoint.version != index + 1:
                issues.append({"version": checkpoint.version, "code": "non_monotonic_version"})
            if checkpoint.previous_digest != previous:
                issues.append({"version": checkpoint.version, "code": "previous_digest_mismatch"})
            if checkpoint.digest != _digest(self._payload(checkpoint)):
                issues.append({"version": checkpoint.version, "code": "content_digest_mismatch"})
            previous = checkpoint.digest
        return {"valid": not issues, "task_id": task_id, "checkpoint_count": len(history),
                "issues": issues, "append_only_history_preserved": True}

    def diff(self, task_id: str, from_version: int, to_version: int) -> dict:
        history = self._items.get(task_id, [])
        by_version = {item.version: item for item in history}
        if from_version not in by_version or to_version not in by_version:
            raise ValueError("both checkpoint versions must exist")
        left, right = by_version[from_version], by_version[to_version]
        left_sources, right_sources = set(left.source_refs), set(right.source_refs)
        left_questions, right_questions = set(left.unresolved_questions), set(right.unresolved_questions)
        return {
            "task_id": task_id, "from_version": from_version, "to_version": to_version,
            "state_changed": left.state != right.state, "state": {"from": left.state, "to": right.state},
            "source_refs_added": sorted(right_sources - left_sources),
            "source_refs_removed": sorted(left_sources - right_sources),
            "questions_opened": sorted(right_questions - left_questions),
            "questions_resolved_or_removed": sorted(left_questions - right_questions),
            "scientific_progress_established": False,
        }

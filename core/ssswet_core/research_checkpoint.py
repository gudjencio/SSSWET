from dataclasses import dataclass, asdict
from datetime import datetime, timezone


@dataclass(frozen=True)
class ResearchCheckpoint:
    task_id: str
    version: int
    state: str
    source_refs: tuple[str, ...]
    unresolved_questions: tuple[str, ...]
    created_at: str


class CheckpointLedger:
    def __init__(self) -> None:
        self._items: dict[str, list[ResearchCheckpoint]] = {}

    def save(self, task_id: str, state: str, *, source_refs=(), unresolved_questions=()) -> ResearchCheckpoint:
        history = self._items.setdefault(task_id, [])
        checkpoint = ResearchCheckpoint(task_id, len(history) + 1, state, tuple(source_refs), tuple(unresolved_questions), datetime.now(timezone.utc).isoformat())
        history.append(checkpoint)
        return checkpoint

    def latest(self, task_id: str) -> ResearchCheckpoint | None:
        history = self._items.get(task_id, [])
        return history[-1] if history else None

    def history(self, task_id: str) -> list[dict]:
        return [asdict(item) for item in self._items.get(task_id, [])]

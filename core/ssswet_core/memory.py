from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class MemoryItem:
    key: str
    statement: str
    source: str
    validated: bool = False
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class KnowledgeMemory:
    """Small validated-knowledge store.

    Unvalidated findings can be retained for traceability, but callers must
    explicitly request validated items when building a new research context.
    """

    def __init__(self) -> None:
        self._items: dict[str, MemoryItem] = {}

    def remember(self, item: MemoryItem) -> None:
        self._items[item.key] = item

    def validated(self) -> list[MemoryItem]:
        return [item for item in self._items.values() if item.validated]

    def search(self, text: str, validated_only: bool = False) -> list[MemoryItem]:
        needle = text.casefold()
        return [
            item for item in self._items.values()
            if (not validated_only or item.validated)
            and (needle in item.statement.casefold() or needle in item.key.casefold())
        ]

    def export(self) -> list[dict[str, object]]:
        return [item.__dict__.copy() for item in self._items.values()]

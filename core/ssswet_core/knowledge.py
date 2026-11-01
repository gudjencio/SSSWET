from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable


@dataclass(frozen=True)
class KnowledgeItem:
    key: str
    statement: str
    evidence: tuple[str, ...]
    confidence: float
    verified: bool
    created_at: str


class KnowledgeExchange:
    """Shared memory that keeps evidence attached to conclusions."""

    def __init__(self) -> None:
        self._items: dict[str, KnowledgeItem] = {}

    def remember(
        self,
        key: str,
        statement: str,
        evidence: Iterable[str] = (),
        confidence: float = 0.0,
        verified: bool = False,
    ) -> KnowledgeItem:
        item = KnowledgeItem(
            key=key,
            statement=statement,
            evidence=tuple(evidence),
            confidence=max(0.0, min(1.0, confidence)),
            verified=verified,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._items[key] = item
        return item

    def get(self, key: str) -> KnowledgeItem | None:
        return self._items.get(key)

    def verified_items(self) -> list[KnowledgeItem]:
        return [item for item in self._items.values() if item.verified]

    def search(self, phrase: str) -> list[KnowledgeItem]:
        query = phrase.lower().strip()
        if not query:
            return []
        return [
            item for item in self._items.values()
            if query in item.statement.lower() or query in item.key.lower()
        ]

    def export(self) -> list[dict]:
        return [item.__dict__.copy() for item in self._items.values()]

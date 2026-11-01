"""SQLite persistence for SSSWET research runs.

The store uses only the Python standard library. It records task metadata,
structured events and provider outputs without upgrading their verification
status. It is intended for a single local installation.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable

from .models import ResearchEvent, Task


class SQLiteResearchStore:
    def __init__(self, database: str | Path = ".ssswet/ssswet.sqlite3") -> None:
        self.path = Path(database).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 10000")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    objective TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    attempts INTEGER NOT NULL,
                    strategy_history TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kind TEXT NOT NULL,
                    message TEXT NOT NULL,
                    task_id TEXT,
                    agent_id TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS research_steps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    evidence TEXT NOT NULL,
                    source_ids TEXT NOT NULL,
                    uncertainty REAL NOT NULL,
                    classification TEXT NOT NULL DEFAULT 'unverified',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS sources (
                    source_id TEXT PRIMARY KEY,
                    doi TEXT NOT NULL DEFAULT '',
                    title TEXT NOT NULL,
                    url TEXT NOT NULL DEFAULT '',
                    source_type TEXT NOT NULL,
                    authors TEXT NOT NULL,
                    institutions TEXT NOT NULL,
                    dataset_ids TEXT NOT NULL,
                    related_source_ids TEXT NOT NULL,
                    provenance_group TEXT NOT NULL DEFAULT '',
                    metadata TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_sources_doi ON sources(doi);
                CREATE INDEX IF NOT EXISTS idx_sources_provenance ON sources(provenance_group);
                CREATE TABLE IF NOT EXISTS knowledge (
                    item_key TEXT PRIMARY KEY,
                    statement TEXT NOT NULL,
                    source TEXT NOT NULL,
                    validated INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_events_created ON events(id DESC);
                CREATE INDEX IF NOT EXISTS idx_steps_task ON research_steps(task_id);
                """
            )

    def save_run(
        self,
        task: Task,
        events: Iterable[ResearchEvent],
        steps: Iterable[object] = (),
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO tasks(task_id, objective, domain, priority, status, attempts, strategy_history, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(task_id) DO UPDATE SET
                    objective=excluded.objective,
                    domain=excluded.domain,
                    priority=excluded.priority,
                    status=excluded.status,
                    attempts=excluded.attempts,
                    strategy_history=excluded.strategy_history,
                    updated_at=CURRENT_TIMESTAMP
                """,
                (
                    task.id, task.objective, task.domain, task.priority,
                    task.status.value, task.attempts,
                    json.dumps(task.strategy_history, ensure_ascii=False),
                ),
            )
            for event in events:
                connection.execute(
                    "INSERT INTO events(kind, message, task_id, agent_id) VALUES (?, ?, ?, ?)",
                    (event.kind, event.message, event.task_id, event.agent_id),
                )
            for step in steps:
                connection.execute(
                    """
                    INSERT INTO research_steps(
                        task_id, role, agent_id, provider, summary, evidence,
                        source_ids, uncertainty, classification
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'unverified')
                    """,
                    (
                        task.id,
                        step.subtask.role,
                        step.agent_id,
                        step.provider,
                        step.result.summary,
                        json.dumps(list(step.result.evidence), ensure_ascii=False),
                        json.dumps(list(step.result.source_ids), ensure_ascii=False),
                        float(step.result.uncertainty),
                    ),
                )

    def recent_tasks(self, limit: int = 20) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM tasks ORDER BY updated_at DESC LIMIT ?",
                (max(1, min(int(limit), 100)),),
            ).fetchall()
        results = []
        for row in rows:
            item = dict(row)
            item["strategy_history"] = json.loads(item["strategy_history"])
            results.append(item)
        return results

    def recent_events(self, limit: int = 50) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM events ORDER BY id DESC LIMIT ?",
                (max(1, min(int(limit), 200)),),
            ).fetchall()
        return [dict(row) for row in rows]

    def recent_steps(self, limit: int = 50) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM research_steps ORDER BY id DESC LIMIT ?",
                (max(1, min(int(limit), 200)),),
            ).fetchall()
        results = []
        for row in rows:
            item = dict(row)
            item["evidence"] = json.loads(item["evidence"])
            item["source_ids"] = json.loads(item["source_ids"])
            results.append(item)
        return results


    def save_knowledge(self, item: object) -> None:
        """Persist a MemoryItem without changing its validation flag."""
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO knowledge(item_key, statement, source, validated, created_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(item_key) DO UPDATE SET
                    statement=excluded.statement,
                    source=excluded.source,
                    validated=excluded.validated,
                    created_at=excluded.created_at
                """,
                (
                    item.key,
                    item.statement,
                    item.source,
                    1 if item.validated else 0,
                    item.created_at,
                ),
            )

    def knowledge_items(self, validated_only: bool = False) -> list[dict]:
        query = "SELECT item_key, statement, source, validated, created_at FROM knowledge"
        if validated_only:
            query += " WHERE validated = 1"
        query += " ORDER BY created_at"
        with self._connect() as connection:
            rows = connection.execute(query).fetchall()
        return [
            {
                "key": row["item_key"],
                "statement": row["statement"],
                "source": row["source"],
                "validated": bool(row["validated"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]


    def register_source(self, source: object) -> None:
        """Insert or update a source's traceable bibliographic provenance."""
        metadata = {
            "peer_reviewed": bool(source.peer_reviewed),
            "primary_source": bool(source.primary_source),
            "methods_available": bool(source.methods_available),
            "publication_date_known": bool(source.publication_date_known),
            "limitations": list(source.limitations),
            "retrieved_at": source.retrieved_at,
        }
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO sources(
                    source_id, doi, title, url, source_type, authors, institutions,
                    dataset_ids, related_source_ids, provenance_group, metadata, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(source_id) DO UPDATE SET
                    doi=excluded.doi, title=excluded.title, url=excluded.url,
                    source_type=excluded.source_type, authors=excluded.authors,
                    institutions=excluded.institutions, dataset_ids=excluded.dataset_ids,
                    related_source_ids=excluded.related_source_ids,
                    provenance_group=excluded.provenance_group,
                    metadata=excluded.metadata, updated_at=CURRENT_TIMESTAMP
                """,
                (
                    source.source_id.strip(), source.doi.strip(), source.title.strip(),
                    source.url, source.source_type,
                    json.dumps(list(source.authors), ensure_ascii=False),
                    json.dumps(list(source.institutions), ensure_ascii=False),
                    json.dumps(list(source.dataset_ids), ensure_ascii=False),
                    json.dumps(list(source.related_source_ids), ensure_ascii=False),
                    source.provenance_group.strip(),
                    json.dumps(metadata, ensure_ascii=False),
                ),
            )

    def get_source(self, source_id: str) -> dict | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM sources WHERE source_id = ?", (source_id,)
            ).fetchone()
        if row is None:
            return None
        item = dict(row)
        for field in ("authors", "institutions", "dataset_ids", "related_source_ids", "metadata"):
            item[field] = json.loads(item[field])
        return item

    def find_sources_by_doi(self, doi: str) -> list[dict]:
        normalized = doi.strip().lower().removeprefix("https://doi.org/").removeprefix("http://doi.org/")
        if not normalized:
            return []
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT source_id FROM sources WHERE lower(doi) = ? ORDER BY source_id",
                (normalized,),
            ).fetchall()
        return [item for row in rows if (item := self.get_source(row["source_id"])) is not None]

    def sources_sharing_provenance(self, provenance_group: str) -> list[dict]:
        group = provenance_group.strip()
        if not group:
            return []
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT source_id FROM sources WHERE provenance_group = ? ORDER BY source_id",
                (group,),
            ).fetchall()
        return [item for row in rows if (item := self.get_source(row["source_id"])) is not None]

    def source_dependency_report(self, source_id: str) -> dict:
        """Return explicit DOI, dataset and declared related-source overlaps."""
        source = self.get_source(source_id)
        if source is None:
            return {"source_id": source_id, "found": False, "dependencies": []}
        dependencies: dict[str, set[str]] = {}
        for other in self._all_source_records():
            if other["source_id"] == source_id:
                continue
            reasons = set()
            if source["doi"] and source["doi"].casefold() == other["doi"].casefold():
                reasons.add("same_doi")
            shared_datasets = set(source["dataset_ids"]) & set(other["dataset_ids"])
            if shared_datasets:
                reasons.add("shared_dataset:" + ",".join(sorted(shared_datasets)))
            if other["source_id"] in source["related_source_ids"] or source_id in other["related_source_ids"]:
                reasons.add("declared_related_source")
            if source["provenance_group"] and source["provenance_group"] == other["provenance_group"]:
                reasons.add("same_provenance_group")
            if reasons:
                dependencies[other["source_id"]] = reasons
        return {
            "source_id": source_id,
            "found": True,
            "dependencies": [
                {"source_id": key, "reasons": sorted(value)}
                for key, value in sorted(dependencies.items())
            ],
            "warning": "Declared overlaps are review signals, not proof of dependence or independence.",
        }

    def _all_source_records(self) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute("SELECT source_id FROM sources ORDER BY source_id").fetchall()
        return [item for row in rows if (item := self.get_source(row["source_id"])) is not None]

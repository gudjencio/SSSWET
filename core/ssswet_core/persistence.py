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
                CREATE TABLE IF NOT EXISTS knowledge_nodes (
                    node_id TEXT PRIMARY KEY,
                    node_type TEXT NOT NULL,
                    label TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    verification_state TEXT NOT NULL DEFAULT 'unverified',
                    metadata TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS knowledge_edges (
                    source_id TEXT NOT NULL REFERENCES knowledge_nodes(node_id) ON DELETE CASCADE,
                    target_id TEXT NOT NULL REFERENCES knowledge_nodes(node_id) ON DELETE CASCADE,
                    relation TEXT NOT NULL,
                    note TEXT NOT NULL DEFAULT '',
                    confidence REAL NOT NULL DEFAULT 0.0,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY(source_id, target_id, relation)
                );
                CREATE INDEX IF NOT EXISTS idx_graph_edges_target ON knowledge_edges(target_id);
                CREATE INDEX IF NOT EXISTS idx_graph_edges_relation ON knowledge_edges(relation);
                CREATE TABLE IF NOT EXISTS experiment_plans (
                    experiment_id TEXT PRIMARY KEY,
                    hypothesis_id TEXT NOT NULL,
                    plan_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS experiment_records (
                    record_id TEXT PRIMARY KEY,
                    experiment_id TEXT NOT NULL REFERENCES experiment_plans(experiment_id) ON DELETE CASCADE,
                    kind TEXT NOT NULL,
                    record_json TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_experiment_records_plan ON experiment_records(experiment_id);
                CREATE TABLE IF NOT EXISTS adaptive_cycles (
                    cycle_id TEXT PRIMARY KEY,
                    study_id TEXT NOT NULL,
                    cycle_json TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_adaptive_cycles_study ON adaptive_cycles(study_id);
                CREATE TABLE IF NOT EXISTS research_campaigns (
                    campaign_id TEXT PRIMARY KEY,
                    campaign_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_campaigns_updated ON research_campaigns(updated_at DESC);
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


    def add_knowledge_node(self, node: object) -> None:
        from .knowledge_graph import validate_node
        from datetime import datetime, timezone

        validate_node(node)
        created_at = node.created_at or datetime.now(timezone.utc).isoformat()
        metadata = node.metadata or {}
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO knowledge_nodes(
                    node_id, node_type, label, description, verification_state, metadata, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(node_id) DO UPDATE SET
                    node_type=excluded.node_type, label=excluded.label,
                    description=excluded.description,
                    verification_state=excluded.verification_state,
                    metadata=excluded.metadata
                """,
                (
                    node.node_id.strip(), node.node_type, node.label.strip(),
                    node.description, node.verification_state,
                    json.dumps(metadata, ensure_ascii=False), created_at,
                ),
            )

    def add_knowledge_edge(self, edge: object) -> None:
        from .knowledge_graph import validate_edge
        from datetime import datetime, timezone

        validate_edge(edge)
        created_at = edge.created_at or datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            endpoints = connection.execute(
                "SELECT node_id FROM knowledge_nodes WHERE node_id IN (?, ?)",
                (edge.source_id, edge.target_id),
            ).fetchall()
            if len(endpoints) != 2:
                raise ValueError("Both edge endpoints must exist in the knowledge graph")
            connection.execute(
                """
                INSERT INTO knowledge_edges(
                    source_id, target_id, relation, note, confidence, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_id, target_id, relation) DO UPDATE SET
                    note=excluded.note, confidence=excluded.confidence
                """,
                (
                    edge.source_id, edge.target_id, edge.relation,
                    edge.note, float(edge.confidence), created_at,
                ),
            )

    def knowledge_graph(
        self, node_type: str | None = None, limit: int = 500
    ) -> dict:
        bounded_limit = max(1, min(int(limit), 2000))
        with self._connect() as connection:
            if node_type:
                rows = connection.execute(
                    "SELECT * FROM knowledge_nodes WHERE node_type = ? ORDER BY created_at LIMIT ?",
                    (node_type, bounded_limit),
                ).fetchall()
                ids = [row["node_id"] for row in rows]
                if ids:
                    placeholders = ",".join("?" for _ in ids)
                    edges = connection.execute(
                        f"SELECT * FROM knowledge_edges WHERE source_id IN ({placeholders}) OR target_id IN ({placeholders}) ORDER BY created_at",
                        (*ids, *ids),
                    ).fetchall()
                else:
                    edges = []
            else:
                rows = connection.execute(
                    "SELECT * FROM knowledge_nodes ORDER BY created_at LIMIT ?",
                    (bounded_limit,),
                ).fetchall()
                edges = connection.execute(
                    "SELECT * FROM knowledge_edges ORDER BY created_at LIMIT ?",
                    (bounded_limit * 4,),
                ).fetchall()
        nodes = []
        for row in rows:
            item = dict(row)
            item["metadata"] = json.loads(item["metadata"])
            nodes.append(item)
        return {"nodes": nodes, "edges": [dict(edge) for edge in edges]}

    def knowledge_neighbors(
        self, node_id: str, relation: str | None = None
    ) -> dict:
        with self._connect() as connection:
            params: list = [node_id, node_id]
            sql = "SELECT * FROM knowledge_edges WHERE (source_id = ? OR target_id = ?)"
            if relation:
                sql += " AND relation = ?"
                params.append(relation)
            sql += " ORDER BY created_at"
            rows = connection.execute(sql, params).fetchall()
        incoming = [dict(row) for row in rows if row["target_id"] == node_id]
        outgoing = [dict(row) for row in rows if row["source_id"] == node_id]
        return {"node_id": node_id, "incoming": incoming, "outgoing": outgoing}


    def save_experiment_plan(self, plan: object) -> None:
        from .experimentation import plan_to_dict, validate_experiment_plan
        missing = validate_experiment_plan(plan)
        payload = plan_to_dict(plan)
        payload["missing_information"] = missing
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO experiment_plans(experiment_id, hypothesis_id, plan_json, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(experiment_id) DO UPDATE SET
                    hypothesis_id=excluded.hypothesis_id,
                    plan_json=excluded.plan_json,
                    updated_at=CURRENT_TIMESTAMP
                """,
                (plan.experiment_id, plan.hypothesis_id,
                 json.dumps(payload, ensure_ascii=False)),
            )

    def get_experiment_plan(self, experiment_id: str) -> dict | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT plan_json FROM experiment_plans WHERE experiment_id = ?",
                (experiment_id,),
            ).fetchone()
        return json.loads(row["plan_json"]) if row else None

    def save_experiment_record(self, record: object) -> None:
        from .experimentation import record_to_dict, EXECUTION_KINDS
        if record.kind not in EXECUTION_KINDS:
            raise ValueError(f"Unsupported execution kind: {record.kind}")
        payload = record_to_dict(record)
        with self._connect() as connection:
            exists = connection.execute(
                "SELECT 1 FROM experiment_plans WHERE experiment_id = ?",
                (record.experiment_id,),
            ).fetchone()
            if not exists:
                raise ValueError("Experiment plan must be saved before its records")
            connection.execute(
                """
                INSERT INTO experiment_records(record_id, experiment_id, kind, record_json)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(record_id) DO UPDATE SET
                    experiment_id=excluded.experiment_id,
                    kind=excluded.kind,
                    record_json=excluded.record_json
                """,
                (record.record_id, record.experiment_id, record.kind,
                 json.dumps(payload, ensure_ascii=False)),
            )

    def experiment_records(self, experiment_id: str) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT record_json FROM experiment_records WHERE experiment_id = ? ORDER BY created_at, record_id",
                (experiment_id,),
            ).fetchall()
        return [json.loads(row["record_json"]) for row in rows]


    def experiment_overview(self, limit: int = 100) -> list[dict]:
        bounded_limit = max(1, min(int(limit), 500))
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT experiment_id, plan_json FROM experiment_plans ORDER BY updated_at DESC LIMIT ?",
                (bounded_limit,),
            ).fetchall()
        overview = []
        for row in rows:
            plan = json.loads(row["plan_json"])
            plan["records"] = self.experiment_records(row["experiment_id"])
            overview.append(plan)
        return overview


    def experiment_overview(self, limit: int = 100) -> list[dict]:
        bounded_limit = max(1, min(int(limit), 500))
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT experiment_id, plan_json FROM experiment_plans ORDER BY updated_at DESC LIMIT ?",
                (bounded_limit,),
            ).fetchall()
        overview = []
        for row in rows:
            plan = json.loads(row["plan_json"])
            plan["records"] = self.experiment_records(row["experiment_id"])
            overview.append(plan)
        return overview


    def save_adaptive_cycle(self, cycle_id: str, cycle: object) -> None:
        from .adaptive_cycle import adaptive_cycle_to_dict
        if not isinstance(cycle_id, str) or not cycle_id.strip():
            raise ValueError("cycle_id is required")
        payload = adaptive_cycle_to_dict(cycle)
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO adaptive_cycles(cycle_id, study_id, cycle_json)
                VALUES (?, ?, ?)
                ON CONFLICT(cycle_id) DO UPDATE SET
                    study_id=excluded.study_id,
                    cycle_json=excluded.cycle_json
                """,
                (cycle_id, cycle.study_id, json.dumps(payload, ensure_ascii=False, sort_keys=True)),
            )

    def get_adaptive_cycle(self, cycle_id: str) -> dict | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT cycle_json FROM adaptive_cycles WHERE cycle_id = ?",
                (cycle_id,),
            ).fetchone()
        return json.loads(row["cycle_json"]) if row else None

    def adaptive_cycle_history(self, study_id: str | None = None, limit: int = 100) -> list[dict]:
        bounded_limit = max(1, min(int(limit), 500))
        with self._connect() as connection:
            if study_id is None:
                rows = connection.execute(
                    "SELECT cycle_id, cycle_json, created_at FROM adaptive_cycles ORDER BY created_at DESC, cycle_id LIMIT ?",
                    (bounded_limit,),
                ).fetchall()
            else:
                rows = connection.execute(
                    "SELECT cycle_id, cycle_json, created_at FROM adaptive_cycles WHERE study_id = ? ORDER BY created_at DESC, cycle_id LIMIT ?",
                    (study_id, bounded_limit),
                ).fetchall()
        return [
            {"cycle_id": row["cycle_id"], "created_at": row["created_at"], **json.loads(row["cycle_json"])}
            for row in rows
        ]


    def save_campaign(self, campaign: object) -> None:
        from .campaigns import campaign_to_dict
        payload = campaign_to_dict(campaign)
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO research_campaigns(campaign_id, campaign_json)
                VALUES (?, ?)
                ON CONFLICT(campaign_id) DO UPDATE SET
                    campaign_json=excluded.campaign_json,
                    updated_at=CURRENT_TIMESTAMP
                """,
                (campaign.campaign_id, json.dumps(payload, ensure_ascii=False, sort_keys=True)),
            )

    def get_campaign(self, campaign_id: str) -> dict | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT campaign_json FROM research_campaigns WHERE campaign_id = ?",
                (campaign_id,),
            ).fetchone()
        return json.loads(row["campaign_json"]) if row else None

    def campaign_history(self, limit: int = 100) -> list[dict]:
        bounded_limit = max(1, min(int(limit), 500))
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT campaign_json, updated_at FROM research_campaigns ORDER BY updated_at DESC, campaign_id LIMIT ?",
                (bounded_limit,),
            ).fetchall()
        return [
            {**json.loads(row["campaign_json"]), "updated_at": row["updated_at"]}
            for row in rows
        ]

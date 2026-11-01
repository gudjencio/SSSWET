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
                CREATE TABLE IF NOT EXISTS lab_protocols (
                    protocol_id TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    protocol_json TEXT NOT NULL,
                    state TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY(protocol_id, version)
                );
                CREATE INDEX IF NOT EXISTS idx_lab_protocols_state
                    ON lab_protocols(state, created_at DESC);
                CREATE TABLE IF NOT EXISTS lab_protocol_proposals (
                    proposal_id TEXT PRIMARY KEY,
                    protocol_id TEXT NOT NULL,
                    base_version INTEGER NOT NULL,
                    proposer_campaign_id TEXT NOT NULL,
                    proposal_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_lab_protocol_proposals_status
                    ON lab_protocol_proposals(created_at DESC);
                CREATE TABLE IF NOT EXISTS lab_protocol_proposal_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    proposal_id TEXT NOT NULL REFERENCES lab_protocol_proposals(proposal_id),
                    event_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TRIGGER IF NOT EXISTS lab_protocol_proposal_events_no_update
                    BEFORE UPDATE ON lab_protocol_proposal_events
                    BEGIN SELECT RAISE(ABORT, 'protocol proposal events are immutable'); END;
                CREATE TRIGGER IF NOT EXISTS lab_protocol_proposal_events_no_delete
                    BEFORE DELETE ON lab_protocol_proposal_events
                    BEGIN SELECT RAISE(ABORT, 'protocol proposal events are immutable'); END;
                CREATE TABLE IF NOT EXISTS lab_runs (
                    run_id TEXT PRIMARY KEY,
                    protocol_id TEXT NOT NULL,
                    protocol_version INTEGER NOT NULL,
                    campaign_id TEXT NOT NULL,
                    run_json TEXT NOT NULL,
                    recorded_at TEXT NOT NULL,
                    FOREIGN KEY(protocol_id, protocol_version)
                        REFERENCES lab_protocols(protocol_id, version)
                );
                CREATE INDEX IF NOT EXISTS idx_lab_runs_protocol
                    ON lab_runs(protocol_id, protocol_version, recorded_at DESC);
                CREATE INDEX IF NOT EXISTS idx_lab_runs_campaign
                    ON lab_runs(campaign_id, recorded_at DESC);
                CREATE TRIGGER IF NOT EXISTS lab_protocols_no_update
                    BEFORE UPDATE ON lab_protocols
                    BEGIN SELECT RAISE(ABORT, 'lab protocol versions are immutable'); END;
                CREATE TRIGGER IF NOT EXISTS lab_protocols_no_delete
                    BEFORE DELETE ON lab_protocols
                    BEGIN SELECT RAISE(ABORT, 'lab protocol versions are immutable'); END;
                CREATE TRIGGER IF NOT EXISTS lab_runs_no_update
                    BEFORE UPDATE ON lab_runs
                    BEGIN SELECT RAISE(ABORT, 'lab run records are immutable'); END;
                CREATE TRIGGER IF NOT EXISTS lab_runs_no_delete
                    BEFORE DELETE ON lab_runs
                    BEGIN SELECT RAISE(ABORT, 'lab run records are immutable'); END;
                CREATE TABLE IF NOT EXISTS lab_comparisons (
                    comparison_id TEXT PRIMARY KEY,
                    left_run_id TEXT NOT NULL REFERENCES lab_runs(run_id),
                    right_run_id TEXT NOT NULL REFERENCES lab_runs(run_id),
                    comparison_json TEXT NOT NULL,
                    compared_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_lab_comparisons_time
                    ON lab_comparisons(compared_at DESC);
                CREATE TRIGGER IF NOT EXISTS lab_comparisons_no_update
                    BEFORE UPDATE ON lab_comparisons
                    BEGIN SELECT RAISE(ABORT, 'lab comparisons are immutable'); END;
                CREATE TRIGGER IF NOT EXISTS lab_comparisons_no_delete
                    BEFORE DELETE ON lab_comparisons
                    BEGIN SELECT RAISE(ABORT, 'lab comparisons are immutable'); END;
                CREATE TABLE IF NOT EXISTS lab_datasets (
                    dataset_id TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    record_json TEXT NOT NULL,
                    content_fingerprint TEXT NOT NULL DEFAULT '',
                    registered_at TEXT NOT NULL,
                    PRIMARY KEY(dataset_id, version)
                );
                CREATE INDEX IF NOT EXISTS idx_lab_datasets_fingerprint
                    ON lab_datasets(content_fingerprint);
                CREATE INDEX IF NOT EXISTS idx_lab_datasets_time
                    ON lab_datasets(registered_at DESC);
                CREATE TRIGGER IF NOT EXISTS lab_datasets_no_update
                    BEFORE UPDATE ON lab_datasets
                    BEGIN SELECT RAISE(ABORT, 'dataset versions are immutable'); END;
                CREATE TRIGGER IF NOT EXISTS lab_datasets_no_delete
                    BEFORE DELETE ON lab_datasets
                    BEGIN SELECT RAISE(ABORT, 'dataset versions are immutable'); END;
                CREATE TABLE IF NOT EXISTS lab_dataset_transformations (
                    transformation_id TEXT PRIMARY KEY,
                    dataset_id TEXT NOT NULL,
                    input_version INTEGER NOT NULL,
                    output_version INTEGER NOT NULL,
                    record_json TEXT NOT NULL,
                    recorded_at TEXT NOT NULL,
                    FOREIGN KEY(dataset_id, input_version)
                        REFERENCES lab_datasets(dataset_id, version),
                    FOREIGN KEY(dataset_id, output_version)
                        REFERENCES lab_datasets(dataset_id, version)
                );
                CREATE INDEX IF NOT EXISTS idx_lab_dataset_transformations_dataset
                    ON lab_dataset_transformations(dataset_id, recorded_at DESC);
                CREATE TRIGGER IF NOT EXISTS lab_dataset_transformations_no_update
                    BEFORE UPDATE ON lab_dataset_transformations
                    BEGIN SELECT RAISE(ABORT, 'dataset transformations are immutable'); END;
                CREATE TRIGGER IF NOT EXISTS lab_dataset_transformations_no_delete
                    BEFORE DELETE ON lab_dataset_transformations
                    BEGIN SELECT RAISE(ABORT, 'dataset transformations are immutable'); END;
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
                CREATE TABLE IF NOT EXISTS resource_snapshots (
                    snapshot_id TEXT PRIMARY KEY,
                    snapshot_json TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_resource_snapshots_created ON resource_snapshots(created_at DESC);
                CREATE TABLE IF NOT EXISTS peer_review_requests (
                    review_id TEXT PRIMARY KEY,
                    source_campaign_id TEXT NOT NULL,
                    node_id TEXT NOT NULL,
                    request_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    closed_at TEXT NOT NULL DEFAULT ''
                );
                CREATE INDEX IF NOT EXISTS idx_peer_review_status
                    ON peer_review_requests(status, created_at DESC);
                CREATE TABLE IF NOT EXISTS peer_review_submissions (
                    submission_id TEXT PRIMARY KEY,
                    review_id TEXT NOT NULL REFERENCES peer_review_requests(review_id),
                    reviewer_campaign_id TEXT NOT NULL,
                    submission_json TEXT NOT NULL,
                    submitted_at TEXT NOT NULL,
                    UNIQUE(review_id, reviewer_campaign_id)
                );
                CREATE INDEX IF NOT EXISTS idx_peer_review_submissions_case
                    ON peer_review_submissions(review_id, submitted_at);
                CREATE TRIGGER IF NOT EXISTS peer_review_submission_no_update
                    BEFORE UPDATE ON peer_review_submissions
                    BEGIN SELECT RAISE(ABORT, 'peer review submissions are immutable'); END;
                CREATE TRIGGER IF NOT EXISTS peer_review_submission_no_delete
                    BEFORE DELETE ON peer_review_submissions
                    BEGIN SELECT RAISE(ABORT, 'peer review submissions are immutable'); END;
                CREATE TABLE IF NOT EXISTS knowledge_transfers (
                    transfer_id TEXT PRIMARY KEY,
                    source_campaign_id TEXT NOT NULL,
                    target_campaign_id TEXT NOT NULL,
                    node_id TEXT NOT NULL,
                    transfer_json TEXT NOT NULL,
                    state TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    decided_at TEXT NOT NULL DEFAULT ''
                );
                CREATE INDEX IF NOT EXISTS idx_transfers_target ON knowledge_transfers(target_campaign_id, state);
                CREATE INDEX IF NOT EXISTS idx_transfers_source ON knowledge_transfers(source_campaign_id, state);
                CREATE TABLE IF NOT EXISTS dispute_cases (\n                    case_id TEXT PRIMARY KEY,\n                    case_json TEXT NOT NULL,\n                    state TEXT NOT NULL,\n                    created_at TEXT NOT NULL,\n                    reviewed_at TEXT NOT NULL DEFAULT ''\n                );\n                CREATE INDEX IF NOT EXISTS idx_dispute_cases_state ON dispute_cases(state, created_at DESC);\n                CREATE TABLE IF NOT EXISTS knowledge (
                    item_key TEXT PRIMARY KEY,
                    statement TEXT NOT NULL,
                    source TEXT NOT NULL,
                    validated INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS collective_memory (
                    memory_id TEXT PRIMARY KEY,
                    campaign_id TEXT NOT NULL DEFAULT '',
                    topic TEXT NOT NULL,
                    statement TEXT NOT NULL,
                    status TEXT NOT NULL,
                    source_ids TEXT NOT NULL,
                    provenance_group TEXT NOT NULL DEFAULT '',
                    confidence REAL NOT NULL DEFAULT 0.0,
                    review_note TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_collective_memory_topic ON collective_memory(topic);
                CREATE INDEX IF NOT EXISTS idx_collective_memory_status ON collective_memory(status);
                CREATE INDEX IF NOT EXISTS idx_collective_memory_campaign ON collective_memory(campaign_id);
                CREATE TABLE IF NOT EXISTS scientific_memory_versions (
                    version_id TEXT PRIMARY KEY,
                    memory_key TEXT NOT NULL,
                    version_number INTEGER NOT NULL,
                    supersedes_version_id TEXT NOT NULL DEFAULT '',
                    record_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE(memory_key, version_number)
                );
                CREATE INDEX IF NOT EXISTS idx_scientific_memory_key
                    ON scientific_memory_versions(memory_key, version_number DESC);
                CREATE TRIGGER IF NOT EXISTS scientific_memory_no_update
                    BEFORE UPDATE ON scientific_memory_versions
                    BEGIN SELECT RAISE(ABORT, 'scientific memory versions are immutable'); END;
                CREATE TRIGGER IF NOT EXISTS scientific_memory_no_delete
                    BEFORE DELETE ON scientific_memory_versions
                    BEGIN SELECT RAISE(ABORT, 'scientific memory versions are immutable'); END;
                CREATE TABLE IF NOT EXISTS literature_watch_reports (
                    watch_id TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    report_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS campaign_watch_subscriptions (
                    subscription_id TEXT PRIMARY KEY,
                    campaign_id TEXT NOT NULL,
                    subscription_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_campaign_watch_due
                    ON campaign_watch_subscriptions(campaign_id, updated_at);
                CREATE TABLE IF NOT EXISTS campaign_watch_runs (
                    run_id TEXT PRIMARY KEY,
                    subscription_id TEXT NOT NULL,
                    campaign_id TEXT NOT NULL,
                    run_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_campaign_watch_runs
                    ON campaign_watch_runs(campaign_id, subscription_id, created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_literature_watch_created
                    ON literature_watch_reports(created_at DESC);
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



    def save_collective_memory(self, record: object) -> None:
        """Persist a traceable memory record without changing its review state."""
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO collective_memory(
                    memory_id, campaign_id, topic, statement, status, source_ids,
                    provenance_group, confidence, review_note, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(memory_id) DO UPDATE SET
                    campaign_id=excluded.campaign_id, topic=excluded.topic,
                    statement=excluded.statement, status=excluded.status,
                    source_ids=excluded.source_ids,
                    provenance_group=excluded.provenance_group,
                    confidence=excluded.confidence, review_note=excluded.review_note,
                    updated_at=excluded.updated_at
                """,
                (
                    record.memory_id, record.campaign_id, record.topic,
                    record.statement, record.status,
                    json.dumps(list(record.source_ids), ensure_ascii=False),
                    record.provenance_group, float(record.confidence),
                    record.review_note, record.created_at, record.updated_at,
                ),
            )

    def collective_memory_items(
        self, *, status: str | None = None, campaign_id: str | None = None,
        limit: int = 200,
    ) -> list[dict]:
        clauses = []
        values: list[object] = []
        if status:
            clauses.append("status = ?")
            values.append(status)
        if campaign_id:
            clauses.append("campaign_id = ?")
            values.append(campaign_id)
        query = "SELECT * FROM collective_memory"
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY updated_at DESC LIMIT ?"
        values.append(max(1, min(int(limit), 500)))
        with self._connect() as connection:
            rows = connection.execute(query, values).fetchall()
        return [
            {**dict(row), "source_ids": json.loads(row["source_ids"])}
            for row in rows
        ]


    def add_scientific_memory_version(self, version: object) -> dict:
        """Append an immutable version; revisions must explicitly supersede the current one."""
        from .scientific_memory import version_to_dict
        payload = version_to_dict(version)
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, allow_nan=False)
        with self._connect() as connection:
            current = connection.execute(
                """SELECT version_id, version_number FROM scientific_memory_versions
                   WHERE memory_key = ? ORDER BY version_number DESC LIMIT 1""",
                (version.memory_key,),
            ).fetchone()
            if current is None:
                if version.supersedes_version_id:
                    raise ValueError("The superseded version does not exist")
                number = 1
            else:
                if version.supersedes_version_id != current["version_id"]:
                    raise ValueError("A revision must supersede the current version")
                number = int(current["version_number"]) + 1
            connection.execute(
                """INSERT INTO scientific_memory_versions(
                       version_id, memory_key, version_number,
                       supersedes_version_id, record_json, created_at
                   ) VALUES (?, ?, ?, ?, ?, ?)""",
                (version.version_id, version.memory_key, number,
                 version.supersedes_version_id, encoded, version.created_at),
            )
        return {"version_id": version.version_id, "memory_key": version.memory_key,
                "version_number": number, **payload}

    def get_scientific_memory_version(self, version_id: str) -> dict | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT version_number, record_json FROM scientific_memory_versions WHERE version_id = ?",
                (version_id,),
            ).fetchone()
        if row is None:
            return None
        return {"version_number": row["version_number"], **json.loads(row["record_json"])}

    def scientific_memory_history(self, limit: int = 200) -> list[dict]:
        bounded = max(1, min(int(limit), 500))
        with self._connect() as connection:
            rows = connection.execute(
                """SELECT version_number, record_json FROM scientific_memory_versions
                   ORDER BY created_at DESC, memory_key DESC, version_number DESC LIMIT ?""",
                (bounded,),
            ).fetchall()
        return [
            {"version_number": row["version_number"], **json.loads(row["record_json"])}
            for row in reversed(rows)
        ]


    def save_literature_watch(self, report: object) -> None:
        """Persist a metadata-watch report without changing research memory."""
        from .literature_watch import report_to_dict
        payload = report_to_dict(report)
        with self._connect() as connection:
            connection.execute(
                """INSERT INTO literature_watch_reports(watch_id, query, report_json, created_at)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(watch_id) DO UPDATE SET
                     query=excluded.query, report_json=excluded.report_json,
                     created_at=excluded.created_at""",
                (report.watch_id, report.query,
                 json.dumps(payload, ensure_ascii=False), report.created_at),
            )

    def literature_watch_history(self, limit: int = 50) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT report_json FROM literature_watch_reports ORDER BY created_at DESC LIMIT ?",
                (max(1, min(int(limit), 200)),),
            ).fetchall()
        return [json.loads(row["report_json"]) for row in rows]


    def save_campaign_watch_subscription(self, subscription: object) -> None:
        from .campaign_literature_watch import subscription_to_dict
        payload = subscription_to_dict(subscription)
        with self._connect() as connection:
            connection.execute(
                """INSERT INTO campaign_watch_subscriptions(
                    subscription_id, campaign_id, subscription_json, updated_at
                ) VALUES (?, ?, ?, ?)
                ON CONFLICT(subscription_id) DO UPDATE SET
                    campaign_id=excluded.campaign_id,
                    subscription_json=excluded.subscription_json,
                    updated_at=excluded.updated_at""",
                (subscription.subscription_id, subscription.campaign_id,
                 json.dumps(payload, ensure_ascii=False, sort_keys=True),
                 subscription.created_at),
            )

    def get_campaign_watch_subscription(self, subscription_id: str) -> dict | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT subscription_json FROM campaign_watch_subscriptions WHERE subscription_id=?",
                (subscription_id,),
            ).fetchone()
        return json.loads(row["subscription_json"]) if row else None

    def campaign_watch_subscriptions(self, campaign_id: str | None = None) -> list[dict]:
        with self._connect() as connection:
            if campaign_id:
                rows = connection.execute(
                    "SELECT subscription_json FROM campaign_watch_subscriptions WHERE campaign_id=? ORDER BY updated_at DESC",
                    (campaign_id,),
                ).fetchall()
            else:
                rows = connection.execute(
                    "SELECT subscription_json FROM campaign_watch_subscriptions ORDER BY updated_at DESC"
                ).fetchall()
        return [json.loads(row["subscription_json"]) for row in rows]

    def due_campaign_watch_subscriptions(self, now_iso: str, limit: int = 20) -> list[dict]:
        rows = self.campaign_watch_subscriptions()
        due = [
            item for item in rows
            if item.get("enabled") and item.get("next_run_at")
            and item["next_run_at"] <= now_iso
        ]
        return sorted(due, key=lambda item: (item["next_run_at"], item["subscription_id"]))[
            :max(1, min(int(limit), 100))
        ]

    def mark_campaign_watch_run(
        self, subscription_id: str, last_run_at: str, next_run_at: str
    ) -> None:
        current = self.get_campaign_watch_subscription(subscription_id)
        if current is None:
            raise ValueError("Unknown campaign watch subscription")
        current["last_run_at"] = last_run_at
        current["next_run_at"] = next_run_at
        with self._connect() as connection:
            connection.execute(
                "UPDATE campaign_watch_subscriptions SET subscription_json=?, updated_at=? WHERE subscription_id=?",
                (json.dumps(current, ensure_ascii=False, sort_keys=True),
                 last_run_at, subscription_id),
            )

    def save_campaign_watch_run(self, run: object) -> None:
        from .campaign_literature_watch import run_to_dict
        payload = run_to_dict(run)
        with self._connect() as connection:
            connection.execute(
                """INSERT INTO campaign_watch_runs(
                    run_id, subscription_id, campaign_id, run_json, created_at
                ) VALUES (?, ?, ?, ?, ?)""",
                (run.run_id, run.subscription_id, run.campaign_id,
                 json.dumps(payload, ensure_ascii=False, sort_keys=True), run.created_at),
            )

    def campaign_watch_run_history(
        self, campaign_id: str | None = None, limit: int = 100
    ) -> list[dict]:
        bounded = max(1, min(int(limit), 500))
        with self._connect() as connection:
            if campaign_id:
                rows = connection.execute(
                    "SELECT run_json FROM campaign_watch_runs WHERE campaign_id=? ORDER BY created_at DESC, run_id LIMIT ?",
                    (campaign_id, bounded),
                ).fetchall()
            else:
                rows = connection.execute(
                    "SELECT run_json FROM campaign_watch_runs ORDER BY created_at DESC, run_id LIMIT ?",
                    (bounded,),
                ).fetchall()
        return [json.loads(row["run_json"]) for row in rows]

    def campaign_watch_seen_ids(self, campaign_id: str, subscription_id: str) -> set[str]:
        seen: set[str] = set()
        for run in self.campaign_watch_run_history(campaign_id, limit=500):
            if run.get("subscription_id") != subscription_id or run.get("error"):
                continue
            seen.update(run.get("new_candidate_ids", []))
            seen.update(run.get("previously_seen_ids", []))
        return seen

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
                "SELECT record_json, created_at FROM experiment_records WHERE experiment_id = ? ORDER BY created_at, record_id",
                (experiment_id,),
            ).fetchall()
        return [
            {**json.loads(row["record_json"]), "recorded_at": row["created_at"]}
            for row in rows
        ]


    def experiment_overview(self, limit: int = 100) -> list[dict]:
        bounded_limit = max(1, min(int(limit), 500))
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT experiment_id, plan_json, updated_at FROM experiment_plans ORDER BY updated_at DESC LIMIT ?",
                (bounded_limit,),
            ).fetchall()
        overview = []
        for row in rows:
            plan = json.loads(row["plan_json"])
            plan["updated_at"] = row["updated_at"]
            plan["records"] = self.experiment_records(row["experiment_id"])
            overview.append(plan)
        return overview


    def experiment_overview(self, limit: int = 100) -> list[dict]:
        bounded_limit = max(1, min(int(limit), 500))
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT experiment_id, plan_json, updated_at FROM experiment_plans ORDER BY updated_at DESC LIMIT ?",
                (bounded_limit,),
            ).fetchall()
        overview = []
        for row in rows:
            plan = json.loads(row["plan_json"])
            plan["updated_at"] = row["updated_at"]
            plan["records"] = self.experiment_records(row["experiment_id"])
            overview.append(plan)
        return overview


    def save_lab_protocol(self, protocol: object) -> dict:
        from dataclasses import asdict
        payload = asdict(protocol)
        if protocol.state != "published":
            raise ValueError("Only published protocol versions can be shared")
        with self._connect() as connection:
            owner = connection.execute(
                "SELECT campaign_json FROM research_campaigns WHERE campaign_id = ?",
                (protocol.owner_campaign_id,),
            ).fetchone()
            if owner is None:
                raise ValueError("Protocol owner campaign must exist")
            if json.loads(owner["campaign_json"]).get("state") != "active":
                raise ValueError("Protocol owner campaign must be active")
            connection.execute(
                """INSERT INTO lab_protocols(
                    protocol_id, version, protocol_json, state, created_at
                ) VALUES (?, ?, ?, ?, ?)""",
                (protocol.protocol_id, protocol.version,
                 json.dumps(payload, ensure_ascii=False, sort_keys=True),
                 protocol.state, protocol.created_at),
            )
        return payload

    def get_lab_protocol(self, protocol_id: str, version: int) -> dict | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT protocol_json FROM lab_protocols WHERE protocol_id = ? AND version = ?",
                (protocol_id, version),
            ).fetchone()
        return json.loads(row["protocol_json"]) if row else None

    def lab_protocol_history(self, limit: int = 200) -> list[dict]:
        bounded = max(1, min(int(limit), 500))
        with self._connect() as connection:
            rows = connection.execute(
                """SELECT protocol_json FROM lab_protocols
                   ORDER BY created_at DESC, protocol_id, version DESC LIMIT ?""",
                (bounded,),
            ).fetchall()
        return [json.loads(row["protocol_json"]) for row in rows]

    def save_lab_protocol_proposal(self, proposal: dict) -> dict:
        required = ("proposal_id", "protocol_id", "proposer_campaign_id", "created_at")
        if any(not isinstance(proposal.get(key), str) or not proposal[key].strip() for key in required):
            raise ValueError("Proposal identifiers and timestamp are required")
        payload = json.dumps(proposal, ensure_ascii=False, sort_keys=True)
        with self._connect() as connection:
            campaign = connection.execute(
                "SELECT campaign_json FROM research_campaigns WHERE campaign_id=?",
                (proposal["proposer_campaign_id"],),
            ).fetchone()
            if campaign is None or json.loads(campaign["campaign_json"]).get("state") != "active":
                raise ValueError("Proposing campaign must exist and be active")
            if connection.execute(
                "SELECT 1 FROM lab_protocol_proposals WHERE proposal_id=?",
                (proposal["proposal_id"],),
            ).fetchone():
                raise ValueError("Protocol proposal ID already exists")
            connection.execute(
                "INSERT INTO lab_protocol_proposals VALUES (?, ?, ?, ?, ?, ?)",
                (proposal["proposal_id"], proposal["protocol_id"], proposal["base_version"],
                 proposal["proposer_campaign_id"], payload, proposal["created_at"]),
            )
            connection.execute(
                "INSERT INTO lab_protocol_proposal_events(proposal_id,event_json,created_at) VALUES(?,?,?)",
                (proposal["proposal_id"], json.dumps({
                    "event": "submitted", "actor_campaign_id": proposal["proposer_campaign_id"],
                    "note": proposal["rationale"],
                }, ensure_ascii=False, sort_keys=True), proposal["created_at"]),
            )
        return proposal

    def get_lab_protocol_proposal(self, proposal_id: str) -> dict | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT proposal_json FROM lab_protocol_proposals WHERE proposal_id=?",
                (proposal_id,),
            ).fetchone()
            events = connection.execute(
                "SELECT event_json FROM lab_protocol_proposal_events WHERE proposal_id=? ORDER BY event_id",
                (proposal_id,),
            ).fetchall()
        if row is None:
            return None
        result = json.loads(row["proposal_json"])
        result["events"] = [json.loads(item["event_json"]) for item in events]
        return result

    def lab_protocol_proposal_history(self, limit: int = 200) -> list[dict]:
        bounded = max(1, min(int(limit), 500))
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT proposal_id FROM lab_protocol_proposals ORDER BY created_at DESC, proposal_id LIMIT ?",
                (bounded,),
            ).fetchall()
        return [self.get_lab_protocol_proposal(row["proposal_id"]) for row in rows]

    def decide_lab_protocol_proposal(self, proposal_id: str, decision: str,
                                     reviewer_campaign_id: str, note: str,
                                     decided_at: str, resulting_version: int = 0) -> dict:
        if decision not in {"accepted", "rejected"} or not note.strip():
            raise ValueError("A supported decision and review note are required")
        with self._connect() as connection:
            row = connection.execute(
                "SELECT proposal_json FROM lab_protocol_proposals WHERE proposal_id=?",
                (proposal_id,),
            ).fetchone()
            if row is None:
                raise ValueError("Protocol proposal does not exist")
            proposal = json.loads(row["proposal_json"])
            if proposal["status"] != "pending":
                raise ValueError("Only pending proposals can be reviewed")
            protocol = connection.execute(
                "SELECT protocol_json FROM lab_protocols WHERE protocol_id=? AND version=?",
                (proposal["protocol_id"], proposal["base_version"]),
            ).fetchone()
            if protocol is None:
                raise ValueError("Base protocol version no longer exists")
            owner_campaign_id = json.loads(protocol["protocol_json"])["owner_campaign_id"]
            if reviewer_campaign_id != owner_campaign_id:
                raise ValueError("Only the protocol owner campaign can decide this proposal")
            campaign = connection.execute(
                "SELECT campaign_json FROM research_campaigns WHERE campaign_id=?",
                (reviewer_campaign_id,),
            ).fetchone()
            if campaign is None or json.loads(campaign["campaign_json"]).get("state") != "active":
                raise ValueError("Reviewing campaign must be active")
            proposal.update({
                "status": decision, "reviewer_campaign_id": reviewer_campaign_id,
                "review_note": note, "decided_at": decided_at,
                "resulting_version": resulting_version,
            })
            connection.execute(
                "UPDATE lab_protocol_proposals SET proposal_json=? WHERE proposal_id=?",
                (json.dumps(proposal, ensure_ascii=False, sort_keys=True), proposal_id),
            )
            connection.execute(
                "INSERT INTO lab_protocol_proposal_events(proposal_id,event_json,created_at) VALUES(?,?,?)",
                (proposal_id, json.dumps({
                    "event": decision, "actor_campaign_id": reviewer_campaign_id,
                    "note": note, "resulting_version": resulting_version,
                }, ensure_ascii=False, sort_keys=True), decided_at),
            )
        return self.get_lab_protocol_proposal(proposal_id)

    def save_lab_run(self, run: object) -> dict:
        from dataclasses import asdict
        payload = asdict(run)
        with self._connect() as connection:
            protocol = connection.execute(
                "SELECT state FROM lab_protocols WHERE protocol_id = ? AND version = ?",
                (run.protocol_id, run.protocol_version),
            ).fetchone()
            if protocol is None or protocol["state"] != "published":
                raise ValueError("Lab run requires a published protocol version")
            campaign = connection.execute(
                "SELECT campaign_json FROM research_campaigns WHERE campaign_id = ?",
                (run.campaign_id,),
            ).fetchone()
            if campaign is None:
                raise ValueError("Reproducing campaign must exist")
            if json.loads(campaign["campaign_json"]).get("state") != "active":
                raise ValueError("Reproducing campaign must be active")
            if connection.execute(
                "SELECT 1 FROM lab_runs WHERE run_id = ?", (run.run_id,)
            ).fetchone():
                raise ValueError("Lab run ID already exists; records are immutable")
            connection.execute(
                """INSERT INTO lab_runs(
                    run_id, protocol_id, protocol_version, campaign_id,
                    run_json, recorded_at
                ) VALUES (?, ?, ?, ?, ?, ?)""",
                (run.run_id, run.protocol_id, run.protocol_version, run.campaign_id,
                 json.dumps(payload, ensure_ascii=False, sort_keys=True),
                 run.recorded_at),
            )
        return payload

    def get_lab_run(self, run_id: str) -> dict | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT run_json FROM lab_runs WHERE run_id = ?", (run_id,)
            ).fetchone()
        return json.loads(row["run_json"]) if row else None

    def lab_run_history(self, limit: int = 200) -> list[dict]:
        bounded = max(1, min(int(limit), 500))
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT run_json FROM lab_runs ORDER BY recorded_at DESC, run_id LIMIT ?",
                (bounded,),
            ).fetchall()
        return [json.loads(row["run_json"]) for row in rows]


    def save_lab_comparison(self, comparison: dict) -> dict:
        required = ("comparison_id", "left_run_id", "right_run_id", "compared_at")
        if any(not isinstance(comparison.get(key), str) or not comparison[key].strip() for key in required):
            raise ValueError("Comparison identifiers and timestamp are required")
        if comparison["left_run_id"] == comparison["right_run_id"]:
            raise ValueError("A comparison requires two distinct runs")
        with self._connect() as connection:
            existing = connection.execute(
                "SELECT comparison_json FROM lab_comparisons WHERE comparison_id = ?",
                (comparison["comparison_id"],),
            ).fetchone()
            if existing:
                return json.loads(existing["comparison_json"])
            connection.execute(
                """INSERT INTO lab_comparisons(
                    comparison_id, left_run_id, right_run_id,
                    comparison_json, compared_at
                ) VALUES (?, ?, ?, ?, ?)""",
                (comparison["comparison_id"], comparison["left_run_id"],
                 comparison["right_run_id"],
                 json.dumps(comparison, ensure_ascii=False, sort_keys=True),
                 comparison["compared_at"]),
            )
        return comparison

    def lab_comparison_history(self, limit: int = 200) -> list[dict]:
        bounded = max(1, min(int(limit), 500))
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT comparison_json FROM lab_comparisons ORDER BY compared_at DESC, comparison_id LIMIT ?",
                (bounded,),
            ).fetchall()
        return [json.loads(row["comparison_json"]) for row in rows]



    def save_lab_dataset(self, record: dict) -> dict:
        required = ("dataset_id", "version", "registered_at", "record_fingerprint")
        if any(key not in record for key in required):
            raise ValueError("Dataset version record is incomplete")
        with self._connect() as connection:
            campaign = connection.execute(
                "SELECT campaign_json FROM research_campaigns WHERE campaign_id=?",
                (record.get("campaign_id", ""),),
            ).fetchone()
            if campaign is None or json.loads(campaign["campaign_json"]).get("state") != "active":
                raise ValueError("Dataset registration campaign must exist and be active")
            if connection.execute(
                "SELECT 1 FROM lab_datasets WHERE dataset_id=? AND version=?",
                (record["dataset_id"], record["version"]),
            ).fetchone():
                raise ValueError("Dataset version already exists; versions are immutable")
            previous = connection.execute(
                "SELECT MAX(version) AS version FROM lab_datasets WHERE dataset_id=?",
                (record["dataset_id"],),
            ).fetchone()["version"]
            expected = 1 if previous is None else previous + 1
            if record["version"] != expected:
                raise ValueError("Dataset versions must be registered sequentially")
            connection.execute(
                """INSERT INTO lab_datasets(dataset_id, version, record_json,
                   content_fingerprint, registered_at) VALUES (?, ?, ?, ?, ?)""",
                (record["dataset_id"], record["version"],
                 json.dumps(record, ensure_ascii=False, sort_keys=True),
                 record.get("content_sha256", ""), record["registered_at"]),
            )
        return record

    def get_lab_dataset(self, dataset_id: str, version: int) -> dict | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT record_json FROM lab_datasets WHERE dataset_id=? AND version=?",
                (dataset_id, version),
            ).fetchone()
        return json.loads(row["record_json"]) if row else None

    def lab_dataset_history(self, limit: int = 200) -> list[dict]:
        bounded = max(1, min(int(limit), 500))
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT record_json FROM lab_datasets ORDER BY registered_at DESC, dataset_id, version DESC LIMIT ?",
                (bounded,),
            ).fetchall()
        return [json.loads(row["record_json"]) for row in rows]

    def save_lab_dataset_transformation(self, record: dict) -> dict:
        with self._connect() as connection:
            for field in ("input_version", "output_version"):
                exists = connection.execute(
                    "SELECT 1 FROM lab_datasets WHERE dataset_id=? AND version=?",
                    (record["dataset_id"], record[field]),
                ).fetchone()
                if not exists:
                    raise ValueError("Transformation references an unknown dataset version")
            connection.execute(
                """INSERT INTO lab_dataset_transformations(
                    transformation_id, dataset_id, input_version, output_version,
                    record_json, recorded_at) VALUES (?, ?, ?, ?, ?, ?)""",
                (record["transformation_id"], record["dataset_id"],
                 record["input_version"], record["output_version"],
                 json.dumps(record, ensure_ascii=False, sort_keys=True),
                 record["recorded_at"]),
            )
        return record

    def lab_dataset_transformation_history(self, limit: int = 200) -> list[dict]:
        bounded = max(1, min(int(limit), 500))
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT record_json FROM lab_dataset_transformations ORDER BY recorded_at DESC, transformation_id LIMIT ?",
                (bounded,),
            ).fetchall()
        return [json.loads(row["record_json"]) for row in rows]


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


    def save_resource_snapshot(self, snapshot_id: str, snapshot: dict) -> None:
        if not isinstance(snapshot_id, str) or not snapshot_id.strip():
            raise ValueError("snapshot_id is required")
        if not isinstance(snapshot, dict):
            raise TypeError("snapshot must be a dictionary")
        encoded = json.dumps(snapshot, ensure_ascii=False, sort_keys=True, allow_nan=False)
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO resource_snapshots(snapshot_id, snapshot_json) VALUES (?, ?)",
                (snapshot_id, encoded),
            )

    def resource_snapshot_history(self, limit: int = 50) -> list[dict]:
        bounded_limit = max(1, min(int(limit), 200))
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT snapshot_id, snapshot_json, created_at FROM resource_snapshots ORDER BY created_at DESC, snapshot_id LIMIT ?",
                (bounded_limit,),
            ).fetchall()
        return [
            {"snapshot_id": row["snapshot_id"], "created_at": row["created_at"],
             "snapshot": json.loads(row["snapshot_json"])}
            for row in rows
        ]


    def create_peer_review_request(self, request: object) -> dict:
        from dataclasses import asdict
        payload = asdict(request)
        with self._connect() as connection:
            source = connection.execute(
                "SELECT campaign_json FROM research_campaigns WHERE campaign_id = ?",
                (request.source_campaign_id,),
            ).fetchone()
            if source is None:
                raise ValueError("Unknown source campaign")
            if json.loads(source["campaign_json"]).get("state") != "active":
                raise ValueError("Source campaign must be active")
            node_row = connection.execute(
                "SELECT metadata FROM knowledge_nodes WHERE node_id = ?",
                (request.node_id,),
            ).fetchone()
            if node_row is None:
                raise ValueError("Unknown knowledge node")
            node_metadata = json.loads(node_row["metadata"] or "{}")
            node_campaign = node_metadata.get("campaign_id")
            if node_campaign != request.source_campaign_id:
                raise ValueError("Knowledge node is not assigned to the source campaign")
            for reviewer_id in request.reviewer_campaign_ids:
                reviewer = connection.execute(
                    "SELECT campaign_json FROM research_campaigns WHERE campaign_id = ?",
                    (reviewer_id,),
                ).fetchone()
                if reviewer is None:
                    raise ValueError(f"Unknown reviewer campaign: {reviewer_id}")
                if json.loads(reviewer["campaign_json"]).get("state") != "active":
                    raise ValueError("Every reviewer campaign must be active")
            connection.execute(
                """INSERT INTO peer_review_requests(
                    review_id, source_campaign_id, node_id, request_json,
                    status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)""",
                (request.review_id, request.source_campaign_id, request.node_id,
                 json.dumps(payload, ensure_ascii=False, sort_keys=True),
                 request.status, request.created_at),
            )
        return payload

    def add_peer_review_submission(self, submission: object) -> dict:
        from dataclasses import asdict
        payload = asdict(submission)
        with self._connect() as connection:
            row = connection.execute(
                "SELECT request_json, status FROM peer_review_requests WHERE review_id = ?",
                (submission.review_id,),
            ).fetchone()
            if row is None:
                raise ValueError("Unknown peer-review request")
            request = json.loads(row["request_json"])
            if submission.reviewer_campaign_id not in request["reviewer_campaign_ids"]:
                raise ValueError("Reviewer campaign is not assigned to this request")
            prior_submission = connection.execute(
                "SELECT 1 FROM peer_review_submissions WHERE review_id = ? AND reviewer_campaign_id = ?",
                (submission.review_id, submission.reviewer_campaign_id),
            ).fetchone()
            if prior_submission:
                raise ValueError("This reviewer campaign has already submitted")
            if row["status"] != "open":
                raise ValueError("Peer-review request is not open")
            campaign = connection.execute(
                "SELECT campaign_json FROM research_campaigns WHERE campaign_id = ?",
                (submission.reviewer_campaign_id,),
            ).fetchone()
            if campaign is None or json.loads(campaign["campaign_json"]).get("state") != "active":
                raise ValueError("Reviewer campaign must still be active")
            if not connection.execute(
                "SELECT 1 FROM knowledge_nodes WHERE node_id = ?",
                (request["node_id"],),
            ).fetchone():
                raise ValueError("The reviewed knowledge node no longer exists")
            connection.execute(
                """INSERT INTO peer_review_submissions(
                    submission_id, review_id, reviewer_campaign_id,
                    submission_json, submitted_at
                ) VALUES (?, ?, ?, ?, ?)""",
                (submission.submission_id, submission.review_id,
                 submission.reviewer_campaign_id,
                 json.dumps(payload, ensure_ascii=False, sort_keys=True),
                 submission.submitted_at),
            )
            submitted = connection.execute(
                "SELECT COUNT(*) AS n FROM peer_review_submissions WHERE review_id = ?",
                (submission.review_id,),
            ).fetchone()["n"]
            if submitted >= len(request["reviewer_campaign_ids"]):
                request["status"] = "completed"
                request["closed_at"] = submission.submitted_at
                connection.execute(
                    "UPDATE peer_review_requests SET request_json = ?, status = ?, closed_at = ? WHERE review_id = ?",
                    (json.dumps(request, ensure_ascii=False, sort_keys=True),
                     "completed", submission.submitted_at, submission.review_id),
                )
        return payload

    def peer_review_history(self, limit: int = 200) -> list[dict]:
        bounded = max(1, min(int(limit), 500))
        with self._connect() as connection:
            requests = connection.execute(
                """SELECT request_json FROM peer_review_requests
                   ORDER BY created_at DESC, review_id LIMIT ?""",
                (bounded,),
            ).fetchall()
            results = []
            for row in requests:
                request = json.loads(row["request_json"])
                submissions = connection.execute(
                    """SELECT submission_json FROM peer_review_submissions
                       WHERE review_id = ? ORDER BY submitted_at, submission_id""",
                    (request["review_id"],),
                ).fetchall()
                request["submissions"] = [
                    json.loads(item["submission_json"]) for item in submissions
                ]
                results.append(request)
        return results


    def create_knowledge_transfer(self, transfer: object) -> None:
        from .collaboration import transfer_to_dict
        payload = transfer_to_dict(transfer)
        if transfer.state != "pending":
            raise ValueError("New knowledge transfers must begin pending")
        with self._connect() as connection:
            for campaign_id in (transfer.source_campaign_id, transfer.target_campaign_id):
                if not connection.execute(
                    "SELECT 1 FROM research_campaigns WHERE campaign_id = ?",
                    (campaign_id,),
                ).fetchone():
                    raise ValueError(f"Unknown campaign: {campaign_id}")
            if not connection.execute(
                "SELECT 1 FROM knowledge_nodes WHERE node_id = ?",
                (transfer.node_id,),
            ).fetchone():
                raise ValueError(f"Unknown knowledge node: {transfer.node_id}")
            connection.execute(
                """INSERT INTO knowledge_transfers(
                    transfer_id, source_campaign_id, target_campaign_id,
                    node_id, transfer_json, state, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (transfer.transfer_id, transfer.source_campaign_id,
                 transfer.target_campaign_id, transfer.node_id,
                 json.dumps(payload, ensure_ascii=False, sort_keys=True),
                 transfer.state, transfer.created_at),
            )

    def decide_knowledge_transfer(self, transfer: object) -> None:
        from .collaboration import transfer_to_dict
        if transfer.state not in {"accepted", "rejected"} or not transfer.decided_at:
            raise ValueError("A transfer decision must be accepted or rejected and timestamped")
        payload = transfer_to_dict(transfer)
        with self._connect() as connection:
            row = connection.execute(
                "SELECT state FROM knowledge_transfers WHERE transfer_id = ?",
                (transfer.transfer_id,),
            ).fetchone()
            if row is None:
                raise ValueError("Unknown knowledge transfer")
            if row["state"] != "pending":
                raise ValueError("Only pending transfers can be decided")
            connection.execute(
                """UPDATE knowledge_transfers
                   SET transfer_json = ?, state = ?, decided_at = ?
                   WHERE transfer_id = ? AND state = 'pending'""",
                (json.dumps(payload, ensure_ascii=False, sort_keys=True),
                 transfer.state, transfer.decided_at, transfer.transfer_id),
            )

    def knowledge_transfer_history(
        self, campaign_id: str | None = None, limit: int = 100
    ) -> list[dict]:
        bounded_limit = max(1, min(int(limit), 500))
        with self._connect() as connection:
            if campaign_id:
                rows = connection.execute(
                    """SELECT transfer_json FROM knowledge_transfers
                       WHERE source_campaign_id = ? OR target_campaign_id = ?
                       ORDER BY created_at DESC, transfer_id LIMIT ?""",
                    (campaign_id, campaign_id, bounded_limit),
                ).fetchall()
            else:
                rows = connection.execute(
                    """SELECT transfer_json FROM knowledge_transfers
                       ORDER BY created_at DESC, transfer_id LIMIT ?""",
                    (bounded_limit,),
                ).fetchall()
        return [json.loads(row["transfer_json"]) for row in rows]

    def campaign_conflict_report(self, campaign_id: str) -> dict:
        if not isinstance(campaign_id, str) or not campaign_id.strip():
            raise ValueError("campaign_id is required")
        graph = self.knowledge_graph(limit=2000)
        nodes = {node["node_id"]: node for node in graph["nodes"]}
        conflicts = []
        for edge in graph["edges"]:
            if edge["relation"] != "contradicts":
                continue
            left = nodes.get(edge["source_id"])
            right = nodes.get(edge["target_id"])
            if left is None or right is None:
                continue
            left_campaign = (left.get("metadata") or {}).get("campaign_id")
            right_campaign = (right.get("metadata") or {}).get("campaign_id")
            if campaign_id in {left_campaign, right_campaign}:
                conflicts.append({
                    "source_id": edge["source_id"], "target_id": edge["target_id"],
                    "source_label": left["label"], "target_label": right["label"],
                    "note": edge["note"], "confidence": edge["confidence"],
                    "source_campaign_id": left_campaign,
                    "target_campaign_id": right_campaign,
                    "requires_human_review": True,
                })
        return {
            "campaign_id": campaign_id,
            "contradictions": conflicts,
            "count": len(conflicts),
            "warning": "Graph contradictions are recorded claims, not adjudicated scientific disputes.",
        }


    def save_dispute_case(self, case: dict) -> None:
        if not isinstance(case, dict) or not case.get("case_id"):
            raise ValueError("A dispute case with an ID is required")
        encoded = json.dumps(case, ensure_ascii=False, sort_keys=True, allow_nan=False)
        with self._connect() as connection:
            connection.execute(
                """INSERT INTO dispute_cases(case_id, case_json, state, created_at)
                   VALUES (?, ?, ?, ?)""",
                (case["case_id"], encoded, case.get("state", "open"),
                 case.get("created_at", "")),
            )

    def update_dispute_case(self, case: dict) -> None:
        if not isinstance(case, dict) or not case.get("case_id"):
            raise ValueError("A dispute case with an ID is required")
        encoded = json.dumps(case, ensure_ascii=False, sort_keys=True, allow_nan=False)
        with self._connect() as connection:
            cursor = connection.execute(
                """UPDATE dispute_cases SET case_json = ?, state = ?, reviewed_at = ?
                   WHERE case_id = ?""",
                (encoded, case["state"], case.get("reviewed_at", ""), case["case_id"]),
            )
            if cursor.rowcount != 1:
                raise ValueError("Unknown dispute case")

    def dispute_history(self, state: str | None = None, limit: int = 200) -> list[dict]:
        bounded_limit = max(1, min(int(limit), 1000))
        with self._connect() as connection:
            if state:
                rows = connection.execute(
                    """SELECT case_json FROM dispute_cases WHERE state = ?
                       ORDER BY created_at DESC, case_id LIMIT ?""",
                    (state, bounded_limit),
                ).fetchall()
            else:
                rows = connection.execute(
                    """SELECT case_json FROM dispute_cases
                       ORDER BY created_at DESC, case_id LIMIT ?""",
                    (bounded_limit,),
                ).fetchall()
        return [json.loads(row["case_json"]) for row in rows]

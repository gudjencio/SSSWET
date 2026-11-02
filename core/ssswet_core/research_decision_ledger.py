"""Append-only, provenance-linked research decision history.

The ledger records review states and their rationale; it does not determine
scientific truth or certify the correctness of a decision.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from uuid import uuid4


DECISION_STATES = {
    "proposed", "supported", "challenged", "superseded",
    "withdrawn", "rejected", "unresolved",
}
_ALLOWED_TRANSITIONS = {
    "proposed": {"supported", "challenged", "withdrawn", "rejected", "unresolved"},
    "supported": {"challenged", "superseded", "withdrawn", "unresolved"},
    "challenged": {"supported", "superseded", "withdrawn", "rejected", "unresolved"},
    "unresolved": {"supported", "challenged", "superseded", "withdrawn", "rejected"},
    "superseded": set(), "withdrawn": set(), "rejected": set(),
}


class ResearchDecisionLedger:
    """Persist decision lineage as immutable, source-linked events."""

    def __init__(self, store):
        self.store = store
        with store._connect() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS research_decision_events (
                    event_id TEXT PRIMARY KEY,
                    decision_id TEXT NOT NULL,
                    subject_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    rationale TEXT NOT NULL,
                    supersedes_decision_id TEXT,
                    evidence_refs_json TEXT NOT NULL,
                    reviewer_ids_json TEXT NOT NULL,
                    actor_id TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_research_decisions_subject
                    ON research_decision_events(subject_id, created_at, event_id);
                CREATE INDEX IF NOT EXISTS idx_research_decisions_lineage
                    ON research_decision_events(decision_id, created_at, event_id);
                CREATE TRIGGER IF NOT EXISTS research_decision_events_no_update
                    BEFORE UPDATE ON research_decision_events
                    BEGIN SELECT RAISE(ABORT, 'research decision events are append-only'); END;
                CREATE TRIGGER IF NOT EXISTS research_decision_events_no_delete
                    BEFORE DELETE ON research_decision_events
                    BEGIN SELECT RAISE(ABORT, 'research decision events are append-only'); END;
            """)

    @staticmethod
    def _identifier(value, field):
        if not isinstance(value, str):
            raise ValueError(f"{field} must be a string")
        value = value.strip()
        if not value or len(value) > 120 or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]*", value):
            raise ValueError(f"{field} must be a valid identifier")
        return value

    @staticmethod
    def _text(value, field, maximum):
        if not isinstance(value, str) or not value.strip() or len(value.strip()) > maximum:
            raise ValueError(f"{field} must contain 1 to {maximum} characters")
        return value.strip()

    @classmethod
    def _refs(cls, values, field):
        if not isinstance(values, (list, tuple)):
            raise ValueError(f"{field} must be a list")
        result = []
        for value in values:
            result.append(cls._text(value, field, 500))
        return list(dict.fromkeys(result))

    def record(self, *, subject_id, rationale, actor_id, evidence_refs=(),
               reviewer_ids=(), status="proposed", supersedes_decision_id=None):
        subject_id = self._identifier(subject_id, "subject_id")
        actor_id = self._identifier(actor_id, "actor_id")
        rationale = self._text(rationale, "rationale", 4000)
        if status not in DECISION_STATES:
            raise ValueError("unsupported decision status")
        refs = self._refs(evidence_refs, "evidence reference")
        reviewers = self._refs(reviewer_ids, "reviewer ID")
        supersedes = None
        with self.store._connect() as connection:
            if supersedes_decision_id is not None:
                supersedes = self._identifier(supersedes_decision_id, "supersedes_decision_id")
                if not refs:
                    raise ValueError("a correction or replacement requires evidence references")
                prior = connection.execute(
                    "SELECT subject_id FROM research_decision_events WHERE decision_id=? "
                    "ORDER BY rowid DESC LIMIT 1", (supersedes,)
                ).fetchone()
                if prior is None:
                    raise ValueError("superseded decision does not exist")
                if prior["subject_id"] != subject_id:
                    raise ValueError("a decision can only supersede a decision on the same subject")
                latest = connection.execute(
                    "SELECT status FROM research_decision_events WHERE decision_id=? "
                    "ORDER BY rowid DESC LIMIT 1", (supersedes,)
                ).fetchone()
                if latest["status"] in {"superseded", "withdrawn", "rejected"}:
                    raise ValueError("terminal decisions cannot be superseded again")
            decision_id = str(uuid4())
            now = datetime.now(timezone.utc).isoformat()
            event_id = str(uuid4())
            connection.execute(
                "INSERT INTO research_decision_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (event_id, decision_id, subject_id, "recorded", status, rationale, supersedes,
                 json.dumps(refs, ensure_ascii=False), json.dumps(reviewers, ensure_ascii=False),
                 actor_id, now),
            )
            if supersedes:
                connection.execute(
                    "INSERT INTO research_decision_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (str(uuid4()), supersedes, subject_id, "status_changed", "superseded",
                     f"Superseded by decision {decision_id}", None, "[]", "[]", actor_id, now),
                )
        return {"event_id": event_id, "decision_id": decision_id, "subject_id": subject_id,
                "status": status, "supersedes_decision_id": supersedes, "created_at": now}

    def transition(self, decision_id, *, status, rationale, actor_id,
                   evidence_refs=(), reviewer_ids=()):
        decision_id = self._identifier(decision_id, "decision_id")
        actor_id = self._identifier(actor_id, "actor_id")
        rationale = self._text(rationale, "rationale", 4000)
        if status not in DECISION_STATES:
            raise ValueError("unsupported decision status")
        refs = self._refs(evidence_refs, "evidence reference")
        reviewers = self._refs(reviewer_ids, "reviewer ID")
        with self.store._connect() as connection:
            prior = connection.execute(
                "SELECT * FROM research_decision_events WHERE decision_id=? "
                "ORDER BY rowid DESC LIMIT 1", (decision_id,)
            ).fetchone()
            if prior is None:
                raise ValueError("decision does not exist")
            if status not in _ALLOWED_TRANSITIONS[prior["status"]]:
                raise ValueError("invalid decision status transition")
            now = datetime.now(timezone.utc).isoformat()
            event_id = str(uuid4())
            connection.execute(
                "INSERT INTO research_decision_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (event_id, decision_id, prior["subject_id"], "status_changed", status,
                 rationale, None, json.dumps(refs, ensure_ascii=False),
                 json.dumps(reviewers, ensure_ascii=False), actor_id, now),
            )
        return {"event_id": event_id, "decision_id": decision_id,
                "subject_id": prior["subject_id"], "status": status, "created_at": now}

    def history(self, subject_id, *, limit=100):
        subject_id = self._identifier(subject_id, "subject_id")
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 500:
            raise ValueError("limit must be between 1 and 500")
        with self.store._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM research_decision_events WHERE subject_id=? "
                "ORDER BY rowid LIMIT ?", (subject_id, limit)
            ).fetchall()
        return [{
            "event_id": row["event_id"], "decision_id": row["decision_id"],
            "subject_id": row["subject_id"], "event_type": row["event_type"],
            "status": row["status"], "rationale": row["rationale"],
            "supersedes_decision_id": row["supersedes_decision_id"],
            "evidence_refs": json.loads(row["evidence_refs_json"]),
            "reviewer_ids": json.loads(row["reviewer_ids_json"]),
            "actor_id": row["actor_id"], "created_at": row["created_at"],
        } for row in rows]

    def get(self, decision_id):
        decision_id = self._identifier(decision_id, "decision_id")
        with self.store._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM research_decision_events WHERE decision_id=? "
                "ORDER BY rowid", (decision_id,)
            ).fetchall()
        if not rows:
            raise ValueError("decision does not exist")
        events = [{
            "event_id": row["event_id"], "event_type": row["event_type"],
            "status": row["status"], "rationale": row["rationale"],
            "evidence_refs": json.loads(row["evidence_refs_json"]),
            "reviewer_ids": json.loads(row["reviewer_ids_json"]),
            "actor_id": row["actor_id"], "created_at": row["created_at"],
        } for row in rows]
        first = rows[0]
        return {
            "decision_id": decision_id, "subject_id": first["subject_id"],
            "supersedes_decision_id": first["supersedes_decision_id"],
            "current_recorded_status": rows[-1]["status"], "events": events,
            "scientific_truth_established": False,
            "interpretation": "Recorded review status is not a determination of scientific truth.",
        }

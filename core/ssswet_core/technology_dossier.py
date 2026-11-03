"""Append-only technology dossier and evidence timeline.

The register stores supplied records; it does not decide scientific truth,
technical feasibility, safety, or commercial readiness.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


TECHNOLOGY_STATES = {
    "concept", "hypothesis", "research", "simulation",
    "candidate", "independently_verified", "reproduced",
    "real_world_validation", "validated", "paused", "rejected",
}
EVENT_TYPES = {
    "research_note", "evidence_added", "experiment_recorded",
    "simulation_recorded", "peer_review", "risk_updated",
    "cost_estimate", "milestone", "correction", "negative_result",
    "status_changed", "decision_recorded",
}


class TechnologyDossierRegistry:
    """Persist versioned technology dossiers as immutable event streams."""

    def __init__(self, store):
        self.store = store
        with store._connect() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS technology_dossiers (
                    technology_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS technology_dossier_events (
                    event_id TEXT PRIMARY KEY,
                    technology_id TEXT NOT NULL REFERENCES technology_dossiers(technology_id),
                    event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    source_refs_json TEXT NOT NULL,
                    actor_id TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_technology_dossier_events
                    ON technology_dossier_events(technology_id, created_at, event_id);
                CREATE TRIGGER IF NOT EXISTS technology_dossier_events_no_update
                    BEFORE UPDATE ON technology_dossier_events
                    BEGIN SELECT RAISE(ABORT, 'technology dossier events are append-only'); END;
                CREATE TRIGGER IF NOT EXISTS technology_dossier_events_no_delete
                    BEFORE DELETE ON technology_dossier_events
                    BEGIN SELECT RAISE(ABORT, 'technology dossier events are append-only'); END;
            """)

    @staticmethod
    def _identifier(value: Any, field: str) -> str:
        if not isinstance(value, str):
            raise ValueError(f"{field} must be a string")
        value = value.strip()
        if not value or len(value) > 120 or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]*", value):
            raise ValueError(f"{field} must be a valid identifier of at most 120 characters")
        return value

    @staticmethod
    def _source_refs(value: Any) -> list[str]:
        if not isinstance(value, (list, tuple)):
            raise ValueError("source_refs must be a list")
        refs = []
        for item in value:
            if not isinstance(item, str) or not item.strip() or len(item.strip()) > 500:
                raise ValueError("source_refs must contain non-empty references up to 500 characters")
            refs.append(item.strip())
        return list(dict.fromkeys(refs))

    def create(self, *, technology_id: str, title: str, domain: str, actor_id: str) -> dict:
        technology_id = self._identifier(technology_id, "technology_id")
        actor_id = self._identifier(actor_id, "actor_id")
        if not isinstance(title, str) or not title.strip() or len(title.strip()) > 240:
            raise ValueError("title must contain 1 to 240 characters")
        if not isinstance(domain, str) or not domain.strip() or len(domain.strip()) > 120:
            raise ValueError("domain must contain 1 to 120 characters")
        now = datetime.now(timezone.utc).isoformat()
        with self.store._connect() as connection:
            connection.execute(
                "INSERT INTO technology_dossiers VALUES (?, ?, ?, ?)",
                (technology_id, title.strip(), domain.strip(), now),
            )
            self._append(connection, technology_id, "status_changed",
                         {"state": "concept", "reason": "initial dossier registration"},
                         [], actor_id, now)
        return self.get(technology_id)

    @staticmethod
    def _append(connection, technology_id, event_type, payload, source_refs, actor_id, now):
        event_id = str(uuid4())
        connection.execute(
            "INSERT INTO technology_dossier_events VALUES (?, ?, ?, ?, ?, ?, ?)",
            (event_id, technology_id, event_type,
             json.dumps(payload, ensure_ascii=False, sort_keys=True),
             json.dumps(source_refs, ensure_ascii=False), actor_id, now),
        )
        return event_id

    def append_event(
        self, *, technology_id: str, event_type: str, payload: dict[str, Any],
        actor_id: str, source_refs: list[str] | tuple[str, ...] = (),
    ) -> dict:
        technology_id = self._identifier(technology_id, "technology_id")
        actor_id = self._identifier(actor_id, "actor_id")
        if event_type not in EVENT_TYPES:
            raise ValueError("unsupported dossier event type")
        if not isinstance(payload, dict) or not payload:
            raise ValueError("payload must be a non-empty object")
        try:
            encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise ValueError("payload must contain JSON-compatible finite values") from exc
        if len(encoded) > 20000:
            raise ValueError("event payload must not exceed 20000 characters")
        refs = self._source_refs(source_refs)
        if event_type in {"evidence_added", "experiment_recorded", "simulation_recorded",
                          "peer_review", "cost_estimate", "negative_result"} and not refs:
            raise ValueError(f"{event_type} requires at least one source reference")
        if event_type == "status_changed":
            state = payload.get("state")
            if state not in TECHNOLOGY_STATES:
                raise ValueError("unsupported technology state")
            if state in {"independently_verified", "reproduced", "validated"} and not refs:
                raise ValueError("verification and validation state changes require source references")
        now = datetime.now(timezone.utc).isoformat()
        with self.store._connect() as connection:
            exists = connection.execute(
                "SELECT 1 FROM technology_dossiers WHERE technology_id=?", (technology_id,)
            ).fetchone()
            if not exists:
                raise ValueError("technology dossier does not exist")
            event_id = self._append(connection, technology_id, event_type, payload, refs, actor_id, now)
        return {"event_id": event_id, "technology_id": technology_id,
                "event_type": event_type, "created_at": now}

    def get(self, technology_id: str) -> dict:
        technology_id = self._identifier(technology_id, "technology_id")
        with self.store._connect() as connection:
            dossier = connection.execute(
                "SELECT * FROM technology_dossiers WHERE technology_id=?", (technology_id,)
            ).fetchone()
            if dossier is None:
                raise ValueError("technology dossier does not exist")
            rows = connection.execute(
                "SELECT * FROM technology_dossier_events WHERE technology_id=? "
                "ORDER BY created_at, event_id", (technology_id,)
            ).fetchall()
        events = [{
            "event_id": row["event_id"], "event_type": row["event_type"],
            "payload": json.loads(row["payload_json"]),
            "source_refs": json.loads(row["source_refs_json"]),
            "actor_id": row["actor_id"], "created_at": row["created_at"],
        } for row in rows]
        state = "concept"
        for event in events:
            if event["event_type"] == "status_changed":
                state = event["payload"]["state"]
        return {
            "technology_id": dossier["technology_id"],
            "title": dossier["title"], "domain": dossier["domain"],
            "created_at": dossier["created_at"], "current_recorded_state": state,
            "event_count": len(events), "events": events,
            "scientific_validity_established": False,
            "commercial_readiness_established": False,
            "interpretation": "This dossier is an immutable record of submitted work and reviews; recorded states are not independently certified by the registry.",
        }

    def list_dossiers(self, limit: int = 100) -> list[dict]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000")
        with self.store._connect() as connection:
            rows = connection.execute(
                "SELECT technology_id FROM technology_dossiers ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [self.get(row["technology_id"]) for row in rows]

"""Append-only, hash-chained public research journal for technology programmes."""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from typing import Any

TECHNOLOGIES = {"cellular", "longevity", "armor", "jetpack", "translator", "spacetime", "timetravel"}
EVENT_TYPES = {
    "research_question", "literature_review", "feasibility_assessment",
    "simulation", "prototype", "test", "independent_review",
    "milestone", "limitation",
}
CLASSIFICATIONS = {
    "hypothesis", "literature", "simulation", "prototype",
    "observation", "independent_review", "project_update",
}
STATES = {"planned", "in_progress", "completed", "blocked", "superseded"}


class ResearchJournal:
    """Records dated project updates without treating them as scientific proof."""

    def __init__(self, store) -> None:
        self.store = store
        with store._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS research_journal (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    entry_id TEXT NOT NULL UNIQUE,
                    technology TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    state TEXT NOT NULL,
                    classification TEXT NOT NULL,
                    evidence_refs TEXT NOT NULL,
                    author_label TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    entry_hash TEXT NOT NULL UNIQUE
                );
                CREATE INDEX IF NOT EXISTS idx_research_journal_technology
                    ON research_journal(technology, sequence DESC);
                CREATE TRIGGER IF NOT EXISTS research_journal_no_update
                    BEFORE UPDATE ON research_journal
                    BEGIN SELECT RAISE(ABORT, 'research journal is append-only'); END;
                CREATE TRIGGER IF NOT EXISTS research_journal_no_delete
                    BEFORE DELETE ON research_journal
                    BEGIN SELECT RAISE(ABORT, 'research journal is append-only'); END;
                """
            )

    @staticmethod
    def _canonical(payload: dict[str, Any]) -> str:
        return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    def append(
        self, *, technology: str, event_type: str, title: str, summary: str,
        state: str = "planned", classification: str = "project_update",
        evidence_refs: list[str] | None = None, author_label: str = "Project team",
    ) -> dict[str, Any]:
        technology = str(technology).strip().lower()
        event_type = str(event_type).strip().lower()
        state = str(state).strip().lower()
        classification = str(classification).strip().lower()
        title, summary = str(title).strip(), str(summary).strip()
        author_label = str(author_label).strip()
        if technology not in TECHNOLOGIES:
            raise ValueError("unknown technology")
        if event_type not in EVENT_TYPES:
            raise ValueError("unsupported event type")
        if state not in STATES:
            raise ValueError("unsupported journal state")
        if classification not in CLASSIFICATIONS:
            raise ValueError("unsupported evidence classification")
        if not title or len(title) > 180:
            raise ValueError("title must contain 1 to 180 characters")
        if not summary or len(summary) > 4000:
            raise ValueError("summary must contain 1 to 4000 characters")
        if not author_label or len(author_label) > 80:
            raise ValueError("author label must contain 1 to 80 characters")
        refs = evidence_refs or []
        if not isinstance(refs, list) or len(refs) > 30:
            raise ValueError("evidence_refs must be a list of at most 30 references")
        clean_refs = []
        for ref in refs:
            if not isinstance(ref, str) or not ref.strip() or len(ref.strip()) > 240:
                raise ValueError("each evidence reference must contain 1 to 240 characters")
            clean_refs.append(ref.strip())
        if len(set(clean_refs)) != len(clean_refs):
            raise ValueError("evidence references must be unique")
        with self.store._connect() as connection:
            previous = connection.execute(
                "SELECT entry_hash FROM research_journal ORDER BY sequence DESC LIMIT 1"
            ).fetchone()
            previous_hash = previous["entry_hash"] if previous else "0" * 64
            created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
            sequence = connection.execute(
                "SELECT COALESCE(MAX(sequence), 0) + 1 FROM research_journal"
            ).fetchone()[0]
            entry_id = f"journal-{sequence:08d}"
            payload = {
                "sequence": sequence, "entry_id": entry_id, "technology": technology,
                "event_type": event_type, "title": title, "summary": summary,
                "state": state, "classification": classification,
                "evidence_refs": clean_refs, "author_label": author_label,
                "created_at": created_at, "previous_hash": previous_hash,
            }
            entry_hash = hashlib.sha256(self._canonical(payload).encode("utf-8")).hexdigest()
            connection.execute(
                """INSERT INTO research_journal
                (sequence,entry_id,technology,event_type,title,summary,state,classification,
                 evidence_refs,author_label,created_at,previous_hash,entry_hash)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (sequence, entry_id, technology, event_type, title, summary, state,
                 classification, json.dumps(clean_refs, ensure_ascii=False), author_label,
                 created_at, previous_hash, entry_hash),
            )
        return {**payload, "entry_hash": entry_hash}

    def verify_chain(self) -> dict[str, Any]:
        with self.store._connect() as connection:
            rows = connection.execute("SELECT * FROM research_journal ORDER BY sequence").fetchall()
        previous_hash = "0" * 64
        checked = 0
        errors = []
        for row in rows:
            item = dict(row)
            payload = {
                "sequence": item["sequence"], "entry_id": item["entry_id"],
                "technology": item["technology"], "event_type": item["event_type"],
                "title": item["title"], "summary": item["summary"], "state": item["state"],
                "classification": item["classification"],
                "evidence_refs": json.loads(item["evidence_refs"]),
                "author_label": item["author_label"], "created_at": item["created_at"],
                "previous_hash": item["previous_hash"],
            }
            expected = hashlib.sha256(self._canonical(payload).encode("utf-8")).hexdigest()
            if item["previous_hash"] != previous_hash or item["entry_hash"] != expected:
                errors.append(item["entry_id"])
            previous_hash = item["entry_hash"]
            checked += 1
        return {
            "entries_checked": checked, "chain_intact": not errors,
            "invalid_entries": errors, "integrity_check_is_not_scientific_validation": True,
        }

    def overview(self, *, technology: str | None = None, limit: int = 100) -> dict[str, Any]:
        if not isinstance(limit, int) or limit < 1 or limit > 500:
            raise ValueError("limit must be between 1 and 500")
        if technology and technology not in TECHNOLOGIES:
            raise ValueError("unknown technology")
        with self.store._connect() as connection:
            if technology:
                rows = connection.execute(
                    "SELECT * FROM research_journal WHERE technology=? ORDER BY sequence DESC LIMIT ?",
                    (technology, limit),
                ).fetchall()
            else:
                rows = connection.execute(
                    "SELECT * FROM research_journal ORDER BY sequence DESC LIMIT ?", (limit,)
                ).fetchall()
        entries = []
        for row in rows:
            item = dict(row)
            item["evidence_refs"] = json.loads(item["evidence_refs"])
            entries.append(item)
        return {
            "entries": entries, "count": len(entries), "append_only": True,
            "scientific_validity_established": False, "chain_integrity": self.verify_chain(),
        }

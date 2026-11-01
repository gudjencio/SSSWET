"""Append-only storage for human-reviewed programme priority assessments."""
from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .priority_framework import score_assessment


class PriorityAssessmentStore:
    def __init__(self, database: str | Path) -> None:
        self.path = Path(database).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS priority_assessments (
                    assessment_id TEXT PRIMARY KEY,
                    programme_id TEXT NOT NULL,
                    scores_json TEXT NOT NULL,
                    score REAL,
                    coverage_percent REAL NOT NULL,
                    assessment_status TEXT NOT NULL,
                    rationale TEXT NOT NULL,
                    evidence_refs_json TEXT NOT NULL,
                    reviewer_label TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_priority_assessments_programme
                ON priority_assessments(programme_id, created_at DESC)
            """)
            connection.executescript("""
                CREATE TRIGGER IF NOT EXISTS priority_assessments_no_update
                BEFORE UPDATE ON priority_assessments
                BEGIN SELECT RAISE(ABORT, 'priority assessments are append-only'); END;
                CREATE TRIGGER IF NOT EXISTS priority_assessments_no_delete
                BEFORE DELETE ON priority_assessments
                BEGIN SELECT RAISE(ABORT, 'priority assessments are append-only'); END;
            """)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout = 10000")
        return connection

    @staticmethod
    def _clean_text(value: Any, field: str, maximum: int, required: bool = True) -> str:
        if not isinstance(value, str):
            raise ValueError(f"{field} must be text")
        result = value.strip()
        if required and not result:
            raise ValueError(f"{field} is required")
        if len(result) > maximum:
            raise ValueError(f"{field} must be {maximum} characters or fewer")
        return result

    def append(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, Mapping):
            raise ValueError("assessment must be an object")
        programme_id = self._clean_text(payload.get("programme_id"), "programme_id", 160)
        reviewer = self._clean_text(payload.get("reviewer_label"), "reviewer_label", 120)
        rationale = self._clean_text(payload.get("rationale"), "rationale", 4000)
        evidence_refs = payload.get("evidence_refs", [])
        if not isinstance(evidence_refs, list) or len(evidence_refs) > 30:
            raise ValueError("evidence_refs must be a list containing at most 30 entries")
        cleaned_refs = []
        for ref in evidence_refs:
            cleaned_refs.append(self._clean_text(ref, "evidence reference", 500))
        result = score_assessment(programme_id, payload.get("scores", {}))
        assessment_id = "priority-" + uuid.uuid4().hex
        created_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            connection.execute("""
                INSERT INTO priority_assessments (
                    assessment_id, programme_id, scores_json, score, coverage_percent,
                    assessment_status, rationale, evidence_refs_json, reviewer_label, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                assessment_id, programme_id, json.dumps(result["scores"], sort_keys=True),
                result["score"], result["coverage_percent"], result["assessment_status"],
                rationale, json.dumps(cleaned_refs), reviewer, created_at,
            ))
        return {
            **result, "assessment_id": assessment_id, "rationale": rationale,
            "evidence_refs": cleaned_refs, "reviewer_label": reviewer,
            "created_at": created_at, "append_only": True,
        }

    def overview(self, limit: int = 300) -> dict[str, Any]:
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 1000:
            raise ValueError("limit must be an integer between 1 and 1000")
        with self._connect() as connection:
            rows = connection.execute("""
                SELECT assessment_id, programme_id, scores_json, score, coverage_percent,
                       assessment_status, rationale, evidence_refs_json, reviewer_label, created_at
                FROM priority_assessments
                ORDER BY created_at DESC, assessment_id DESC LIMIT ?
            """, (limit,)).fetchall()
        history = [{
            "assessment_id": row["assessment_id"],
            "programme_id": row["programme_id"],
            "scores": json.loads(row["scores_json"]),
            "score": row["score"],
            "coverage_percent": row["coverage_percent"],
            "assessment_status": row["assessment_status"],
            "rationale": row["rationale"],
            "evidence_refs": json.loads(row["evidence_refs_json"]),
            "reviewer_label": row["reviewer_label"],
            "created_at": row["created_at"],
        } for row in rows]
        latest_by_programme: dict[str, dict[str, Any]] = {}
        for item in history:
            latest_by_programme.setdefault(item["programme_id"], item)
        latest = list(latest_by_programme.values())
        ranked = sorted(
            (item for item in latest if item["assessment_status"] == "complete"),
            key=lambda item: (-item["score"], item["programme_id"].casefold()),
        )
        incomplete = sorted(
            (item for item in latest if item["assessment_status"] != "complete"),
            key=lambda item: item["programme_id"].casefold(),
        )
        for rank, item in enumerate(ranked, 1):
            item["rank"] = rank
        return {
            "ranked": ranked, "incomplete": incomplete, "history": history,
            "assessed_programmes": len(latest), "ranked_count": len(ranked),
            "incomplete_count": len(incomplete), "history_count": len(history),
            "ranking_is_advisory": True, "automatic_funding_decisions": False,
            "scientific_validity_established": False,
        }

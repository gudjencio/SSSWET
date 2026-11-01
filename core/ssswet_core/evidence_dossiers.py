"""Evidence dossiers that assemble traceable research records without asserting validity."""
from __future__ import annotations

import json
import sqlite3
from hashlib import sha256
from typing import Any, Iterable


class EvidenceDossierService:
    """Build immutable evidence packets from existing local research records.

    A dossier is a traceability container, not a verification mechanism. It
    records what was available for review at assembly time and keeps reviewer
    decisions separate from scientific validity.
    """

    def __init__(self, store) -> None:
        self.store = store
        self._initialize()

    def _initialize(self) -> None:
        with self.store._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS evidence_dossiers (
                    dossier_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    result_summary TEXT NOT NULL,
                    dossier_json TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'assembled',
                    assembled_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS evidence_dossier_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dossier_id TEXT NOT NULL REFERENCES evidence_dossiers(dossier_id),
                    event_json TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_evidence_dossiers_time
                    ON evidence_dossiers(assembled_at DESC);
                CREATE INDEX IF NOT EXISTS idx_evidence_dossier_events_case
                    ON evidence_dossier_events(dossier_id, event_id);
                CREATE TRIGGER IF NOT EXISTS evidence_dossiers_no_update
                    BEFORE UPDATE ON evidence_dossiers
                    BEGIN SELECT RAISE(ABORT, 'evidence dossiers are immutable'); END;
                CREATE TRIGGER IF NOT EXISTS evidence_dossiers_no_delete
                    BEFORE DELETE ON evidence_dossiers
                    BEGIN SELECT RAISE(ABORT, 'evidence dossiers are immutable'); END;
                CREATE TRIGGER IF NOT EXISTS evidence_dossier_events_no_update
                    BEFORE UPDATE ON evidence_dossier_events
                    BEGIN SELECT RAISE(ABORT, 'evidence dossier events are immutable'); END;
                CREATE TRIGGER IF NOT EXISTS evidence_dossier_events_no_delete
                    BEFORE DELETE ON evidence_dossier_events
                    BEGIN SELECT RAISE(ABORT, 'evidence dossier events are immutable'); END;
                """
            )

    @staticmethod
    def _unique(values: Iterable[str]) -> list[str]:
        return list(dict.fromkeys(str(value) for value in values if str(value).strip()))

    def _rows(self, table: str, key: str, values: list[str]) -> list[dict[str, Any]]:
        if not values:
            return []
        placeholders = ",".join("?" for _ in values)
        with self.store._connect() as connection:
            rows = connection.execute(
                f"SELECT * FROM {table} WHERE {key} IN ({placeholders})",
                values,
            ).fetchall()
        return [dict(row) for row in rows]

    def assemble(
        self,
        dossier_id: str,
        title: str,
        result_summary: str,
        *,
        protocol_refs: Iterable[dict[str, Any]] = (),
        run_ids: Iterable[str] = (),
        dataset_refs: Iterable[dict[str, Any]] = (),
        comparison_ids: Iterable[str] = (),
        source_ids: Iterable[str] = (),
        peer_review_ids: Iterable[str] = (),
        dispute_case_ids: Iterable[str] = (),
        objections: Iterable[str] = (),
    ) -> dict[str, Any]:
        if not dossier_id.strip() or not title.strip() or not result_summary.strip():
            raise ValueError("dossier_id, title and result_summary are required")
        with self.store._connect() as connection:
            if connection.execute(
                "SELECT 1 FROM evidence_dossiers WHERE dossier_id=?", (dossier_id,)
            ).fetchone():
                raise ValueError("dossier_id already exists")

        protocols = []
        for ref in protocol_refs:
            protocol_id = str(ref.get("protocol_id", "")).strip()
            version = ref.get("version")
            if not protocol_id or not isinstance(version, int):
                raise ValueError("each protocol reference requires protocol_id and integer version")
            with self.store._connect() as connection:
                row = connection.execute(
                    "SELECT * FROM lab_protocols WHERE protocol_id=? AND version=?",
                    (protocol_id, version),
                ).fetchone()
            if not row:
                raise ValueError(f"unknown protocol reference: {protocol_id} v{version}")
            protocols.append(dict(row))

        runs = self._rows("lab_runs", "run_id", self._unique(run_ids))
        requested_runs = self._unique(run_ids)
        if len(runs) != len(requested_runs):
            missing = sorted(set(requested_runs) - {row["run_id"] for row in runs})
            raise ValueError(f"unknown run reference(s): {', '.join(missing)}")

        datasets = []
        for ref in dataset_refs:
            dataset_id = str(ref.get("dataset_id", "")).strip()
            version = ref.get("version")
            if not dataset_id or not isinstance(version, int):
                raise ValueError("each dataset reference requires dataset_id and integer version")
            with self.store._connect() as connection:
                row = connection.execute(
                    "SELECT * FROM lab_datasets WHERE dataset_id=? AND version=?",
                    (dataset_id, version),
                ).fetchone()
            if not row:
                raise ValueError(f"unknown dataset reference: {dataset_id} v{version}")
            datasets.append(dict(row))

        comparisons = self._rows("lab_comparisons", "comparison_id", self._unique(comparison_ids))
        requested_comparisons = self._unique(comparison_ids)
        if len(comparisons) != len(requested_comparisons):
            missing = sorted(set(requested_comparisons) - {row["comparison_id"] for row in comparisons})
            raise ValueError(f"unknown comparison reference(s): {', '.join(missing)}")

        sources = self._rows("sources", "source_id", self._unique(source_ids))
        requested_sources = self._unique(source_ids)
        if len(sources) != len(requested_sources):
            missing = sorted(set(requested_sources) - {row["source_id"] for row in sources})
            raise ValueError(f"unknown source reference(s): {', '.join(missing)}")

        peer_reviews = self._rows("peer_review_requests", "review_id", self._unique(peer_review_ids))
        requested_reviews = self._unique(peer_review_ids)
        if len(peer_reviews) != len(requested_reviews):
            missing = sorted(set(requested_reviews) - {row["review_id"] for row in peer_reviews})
            raise ValueError(f"unknown peer review reference(s): {', '.join(missing)}")

        disputes = self._rows("dispute_cases", "case_id", self._unique(dispute_case_ids))
        requested_disputes = self._unique(dispute_case_ids)
        if len(disputes) != len(requested_disputes):
            missing = sorted(set(requested_disputes) - {row["case_id"] for row in disputes})
            raise ValueError(f"unknown dispute reference(s): {', '.join(missing)}")

        snapshot = {
            "dossier_id": dossier_id,
            "title": title,
            "result_summary": result_summary,
            "protocols": protocols,
            "runs": runs,
            "datasets": datasets,
            "comparisons": comparisons,
            "sources": sources,
            "peer_reviews": peer_reviews,
            "disputes": disputes,
            "objections": self._unique(objections),
            "scientific_validity_established": False,
            "verification_state": "unverified",
            "assembled_from_existing_records": True,
        }
        canonical = json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        content_hash = sha256(canonical.encode("utf-8")).hexdigest()
        with self.store._connect() as connection:
            connection.execute(
                "INSERT INTO evidence_dossiers(dossier_id,title,result_summary,dossier_json,content_hash) VALUES(?,?,?,?,?)",
                (dossier_id, title, result_summary, canonical, content_hash),
            )
            event = {
                "kind": "assembled",
                "dossier_id": dossier_id,
                "content_hash": content_hash,
                "scientific_validity_established": False,
            }
            connection.execute(
                "INSERT INTO evidence_dossier_events(dossier_id,event_json) VALUES(?,?)",
                (dossier_id, json.dumps(event, ensure_ascii=False, sort_keys=True)),
            )
        return self.get(dossier_id)

    def review(self, dossier_id: str, reviewer_campaign_id: str, decision: str, note: str) -> dict[str, Any]:
        allowed = {"accepted_for_review", "needs_revision", "rejected_for_review"}
        if decision not in allowed:
            raise ValueError("decision must be accepted_for_review, needs_revision or rejected_for_review")
        if not reviewer_campaign_id.strip() or not note.strip():
            raise ValueError("reviewer_campaign_id and note are required")
        dossier = self.get(dossier_id)
        event = {
            "kind": "review",
            "dossier_id": dossier_id,
            "reviewer_campaign_id": reviewer_campaign_id,
            "decision": decision,
            "note": note,
            "scientific_validity_established": False,
        }
        with self.store._connect() as connection:
            connection.execute(
                "INSERT INTO evidence_dossier_events(dossier_id,event_json) VALUES(?,?)",
                (dossier_id, json.dumps(event, ensure_ascii=False, sort_keys=True)),
            )
        return self.get(dossier_id)

    def get(self, dossier_id: str) -> dict[str, Any]:
        with self.store._connect() as connection:
            row = connection.execute(
                "SELECT * FROM evidence_dossiers WHERE dossier_id=?", (dossier_id,)
            ).fetchone()
            if not row:
                raise ValueError("unknown evidence dossier")
            events = connection.execute(
                "SELECT event_id,event_json,created_at FROM evidence_dossier_events WHERE dossier_id=? ORDER BY event_id",
                (dossier_id,),
            ).fetchall()
        payload = json.loads(row["dossier_json"])
        payload.update({
            "content_hash": row["content_hash"],
            "status": row["status"],
            "assembled_at": row["assembled_at"],
            "events": [
                {"event_id": item["event_id"], **json.loads(item["event_json"]), "created_at": item["created_at"]}
                for item in events
            ],
        })
        return payload

    def overview(self, limit: int = 100) -> dict[str, Any]:
        if not isinstance(limit, int) or limit < 1 or limit > 500:
            raise ValueError("limit must be an integer between 1 and 500")
        with self.store._connect() as connection:
            rows = connection.execute(
                "SELECT dossier_id,title,result_summary,content_hash,status,assembled_at FROM evidence_dossiers ORDER BY assembled_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        dossiers = []
        for row in rows:
            item = dict(row)
            dossier = self.get(row["dossier_id"])
            item["verification_state"] = dossier["verification_state"]
            item["scientific_validity_established"] = False
            item["event_count"] = len(dossier["events"])
            item["source_count"] = len(dossier["sources"])
            item["run_count"] = len(dossier["runs"])
            item["comparison_count"] = len(dossier["comparisons"])
            dossiers.append(item)
        return {
            "dossiers": dossiers,
            "count": len(dossiers),
            "scientific_validity_established": False,
            "review_is_separate_from_verification": True,
        }

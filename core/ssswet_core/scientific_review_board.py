"""Structured, append-only scientific review board for evidence dossiers.

Reviewer assessments remain independent. Aggregation reports disagreement and
never declares scientific validity or selects a winning interpretation.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any


VERDICTS = {"supports", "challenges", "mixed", "abstains"}
CONFLICT_STATUSES = {"none_declared", "potential", "confirmed"}


class ScientificReviewBoard:
    def __init__(self, store: Any):
        self.store = store
        with self.store._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS scientific_review_events (
                    review_id TEXT PRIMARY KEY,
                    dossier_id TEXT NOT NULL REFERENCES evidence_dossiers(dossier_id),
                    reviewer_id TEXT NOT NULL,
                    reviewer_campaign_id TEXT NOT NULL DEFAULT '',
                    verdict TEXT NOT NULL,
                    conflict_status TEXT NOT NULL,
                    rationale TEXT NOT NULL,
                    methods_assessment TEXT NOT NULL,
                    limitations TEXT NOT NULL,
                    evidence_refs_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_scientific_review_dossier
                    ON scientific_review_events(dossier_id, created_at, review_id);
                CREATE TRIGGER IF NOT EXISTS scientific_review_events_no_update
                    BEFORE UPDATE ON scientific_review_events
                    BEGIN SELECT RAISE(ABORT, 'scientific reviews are append-only'); END;
                CREATE TRIGGER IF NOT EXISTS scientific_review_events_no_delete
                    BEFORE DELETE ON scientific_review_events
                    BEGIN SELECT RAISE(ABORT, 'scientific reviews are append-only'); END;
                """
            )

    @staticmethod
    def _required(value: Any, label: str, maximum: int) -> str:
        if not isinstance(value, str) or not value.strip() or len(value.strip()) > maximum:
            raise ValueError(f"{label} must contain 1 to {maximum} characters")
        return value.strip()

    def submit(
        self, dossier_id: str, reviewer_id: str, verdict: str,
        conflict_status: str, rationale: str, methods_assessment: str,
        limitations: str, evidence_refs: list[str] | None = None,
        reviewer_campaign_id: str = "",
    ) -> dict:
        dossier_id = self._required(dossier_id, "dossier_id", 200)
        reviewer_id = self._required(reviewer_id, "reviewer_id", 200)
        rationale = self._required(rationale, "rationale", 4000)
        methods_assessment = self._required(methods_assessment, "methods_assessment", 4000)
        limitations = self._required(limitations, "limitations", 4000)
        if verdict not in VERDICTS:
            raise ValueError("Unsupported review verdict")
        if conflict_status not in CONFLICT_STATUSES:
            raise ValueError("A conflict-of-interest declaration is required")
        if not isinstance(evidence_refs, list) or len(evidence_refs) > 100:
            raise ValueError("evidence_refs must be a list of at most 100 identifiers")
        refs = []
        for ref in evidence_refs:
            refs.append(self._required(ref, "evidence reference", 300))
        reviewer_campaign_id = str(reviewer_campaign_id or "").strip()
        if len(reviewer_campaign_id) > 200:
            raise ValueError("reviewer_campaign_id is too long")
        with self.store._connect() as connection:
            if not connection.execute(
                "SELECT 1 FROM evidence_dossiers WHERE dossier_id=?", (dossier_id,)
            ).fetchone():
                raise ValueError("Unknown evidence dossier")
        created_at = datetime.now(timezone.utc).isoformat()
        identity = json.dumps(
            [dossier_id, reviewer_id, verdict, conflict_status, rationale,
             methods_assessment, limitations, refs, created_at],
            ensure_ascii=False, separators=(",", ":"),
        )
        review = {
            "review_id": "srb:" + sha256(identity.encode("utf-8")).hexdigest()[:32],
            "dossier_id": dossier_id, "reviewer_id": reviewer_id,
            "reviewer_campaign_id": reviewer_campaign_id, "verdict": verdict,
            "conflict_status": conflict_status, "rationale": rationale,
            "methods_assessment": methods_assessment, "limitations": limitations,
            "evidence_refs": refs, "created_at": created_at,
            "scientific_validity_established": False,
        }
        with self.store._connect() as connection:
            connection.execute(
                """INSERT INTO scientific_review_events(
                    review_id, dossier_id, reviewer_id, reviewer_campaign_id,
                    verdict, conflict_status, rationale, methods_assessment,
                    limitations, evidence_refs_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (review["review_id"], dossier_id, reviewer_id, reviewer_campaign_id,
                 verdict, conflict_status, rationale, methods_assessment,
                 limitations, json.dumps(refs, ensure_ascii=False), created_at),
            )
        return review

    def report(self, dossier_id: str | None = None, limit: int = 500) -> dict:
        if not isinstance(limit, int) or not 1 <= limit <= 2000:
            raise ValueError("limit must be an integer between 1 and 2000")
        with self.store._connect() as connection:
            if dossier_id:
                rows = connection.execute(
                    """SELECT * FROM scientific_review_events WHERE dossier_id=?
                       ORDER BY created_at, review_id LIMIT ?""", (dossier_id, limit)
                ).fetchall()
            else:
                rows = connection.execute(
                    """SELECT * FROM scientific_review_events
                       ORDER BY created_at DESC, review_id LIMIT ?""", (limit,)
                ).fetchall()
        reviews = []
        for row in rows:
            item = dict(row)
            item["evidence_refs"] = json.loads(item.pop("evidence_refs_json"))
            item["scientific_validity_established"] = False
            reviews.append(item)
        grouped: dict[str, list[dict]] = {}
        for review in reviews:
            grouped.setdefault(review["dossier_id"], []).append(review)
        summaries = []
        for key, items in grouped.items():
            verdicts = sorted({item["verdict"] for item in items})
            positions = []
            for verdict in verdicts:
                position_reviews = [item for item in items if item["verdict"] == verdict]
                positions.append({
                    "position": verdict,
                    "review_count": len(position_reviews),
                    "reviewer_labels": sorted({item["reviewer_id"] for item in position_reviews}),
                    "rationales": [item["rationale"] for item in position_reviews],
                    "methods_assessments": [item["methods_assessment"] for item in position_reviews],
                    "limitations": [item["limitations"] for item in position_reviews],
                    "evidence_refs": sorted({
                        ref for item in position_reviews for ref in item["evidence_refs"]
                    }),
                })
            summaries.append({
                "dossier_id": key, "review_count": len(items),
                "distinct_reviewer_labels": len({item["reviewer_id"] for item in items}),
                "verdicts_present": verdicts,
                "disagreement_recorded": len(verdicts) > 1,
                "competing_positions": positions,
                "conflict_declarations": {
                    status: sum(item["conflict_status"] == status for item in items)
                    for status in sorted(CONFLICT_STATUSES)
                },
                "scientific_validity_established": False,
                "consensus_declared": False,
                "adjudication_required_for_resolution": len(verdicts) > 1,
            })
        return {
            "reviews": reviews, "summaries": summaries, "count": len(reviews),
            "append_only": True, "independent_assessments_preserved": True,
            "automatic_adjudication": False, "scientific_validity_established": False,
        }

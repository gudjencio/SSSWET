"""Append-only research integrity and ethics risk register.

The register records concerns and review decisions. It does not certify safety,
replace institutional review, or automatically authorize or execute research.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any

RISK_CATEGORIES = {
    "data_integrity", "bias", "conflict_of_interest", "reproducibility",
    "safety", "ethics", "legal_regulatory", "security", "other",
}
SEVERITIES = {"low", "medium", "high", "critical"}
RISK_STATES = {"open", "under_review", "mitigated", "accepted_with_controls", "closed", "escalated"}
UNRESOLVED_STATES = {"open", "under_review", "escalated"}


class ResearchIntegrityRegister:
    def __init__(self, store: Any):
        self.store = store
        # EvidenceDossierService owns the immutable dossier schema.
        from .evidence_dossiers import EvidenceDossierService
        EvidenceDossierService(store)
        with self.store._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS research_integrity_events (
                    event_id TEXT PRIMARY KEY,
                    risk_id TEXT NOT NULL,
                    dossier_id TEXT NOT NULL REFERENCES evidence_dossiers(dossier_id),
                    category TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    state TEXT NOT NULL,
                    description TEXT NOT NULL,
                    mitigation TEXT NOT NULL,
                    reviewer_label TEXT NOT NULL,
                    authorization_reference TEXT NOT NULL,
                    evidence_refs_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_integrity_events_risk
                    ON research_integrity_events(risk_id, created_at, event_id);
                CREATE INDEX IF NOT EXISTS idx_integrity_events_dossier
                    ON research_integrity_events(dossier_id, created_at);
                CREATE TRIGGER IF NOT EXISTS research_integrity_events_no_update
                    BEFORE UPDATE ON research_integrity_events
                    BEGIN SELECT RAISE(ABORT, 'integrity events are append-only'); END;
                CREATE TRIGGER IF NOT EXISTS research_integrity_events_no_delete
                    BEFORE DELETE ON research_integrity_events
                    BEGIN SELECT RAISE(ABORT, 'integrity events are append-only'); END;
                """
            )

    @staticmethod
    def _required(value: Any, label: str, maximum: int) -> str:
        if not isinstance(value, str) or not value.strip() or len(value.strip()) > maximum:
            raise ValueError(f"{label} must contain 1 to {maximum} characters")
        return value.strip()

    def record(
        self, dossier_id: str, category: str, severity: str, description: str,
        reviewer_label: str, *, state: str = "open", mitigation: str = "",
        authorization_reference: str = "", evidence_refs: list[str] | None = None,
    ) -> dict:
        dossier_id = self._required(dossier_id, "dossier_id", 200)
        description = self._required(description, "description", 4000)
        reviewer_label = self._required(reviewer_label, "reviewer_label", 200)
        if category not in RISK_CATEGORIES:
            raise ValueError("Unsupported integrity risk category")
        if severity not in SEVERITIES:
            raise ValueError("Unsupported risk severity")
        if state not in RISK_STATES:
            raise ValueError("Unsupported risk state")
        if not isinstance(mitigation, str) or len(mitigation.strip()) > 4000:
            raise ValueError("mitigation must not exceed 4000 characters")
        if not isinstance(authorization_reference, str) or len(authorization_reference.strip()) > 500:
            raise ValueError("authorization_reference must not exceed 500 characters")
        if evidence_refs is None:
            evidence_refs = []
        if not isinstance(evidence_refs, list) or len(evidence_refs) > 100:
            raise ValueError("evidence_refs must be a list of at most 100 identifiers")
        refs = [self._required(item, "evidence reference", 300) for item in evidence_refs]
        with self.store._connect() as connection:
            if not connection.execute(
                "SELECT 1 FROM evidence_dossiers WHERE dossier_id=?", (dossier_id,)
            ).fetchone():
                raise ValueError("Unknown evidence dossier")
            if state in {"mitigated", "accepted_with_controls", "closed"} and not mitigation.strip():
                raise ValueError("A documented mitigation or closure rationale is required")
            if category in {"safety", "ethics", "legal_regulatory"} and severity in {"high", "critical"} and state in {"mitigated", "accepted_with_controls", "closed"} and not authorization_reference.strip():
                raise ValueError("A qualified human authorization reference is required for this risk state")
        created_at = datetime.now(timezone.utc).isoformat()
        risk_id = "risk:" + sha256((dossier_id + "|" + category + "|" + description).encode("utf-8")).hexdigest()[:24]
        event_identity = json.dumps(
            [risk_id, severity, state, mitigation, reviewer_label, authorization_reference, refs, created_at],
            ensure_ascii=False, separators=(",", ":"),
        )
        event = {
            "event_id": sha256(event_identity.encode("utf-8")).hexdigest(),
            "risk_id": risk_id, "dossier_id": dossier_id, "category": category,
            "severity": severity, "state": state, "description": description,
            "mitigation": mitigation.strip(), "reviewer_label": reviewer_label,
            "authorization_reference": authorization_reference.strip(),
            "evidence_refs": refs, "created_at": created_at,
            "hold_recommended": severity in {"high", "critical"} and state in UNRESOLVED_STATES,
            "automatic_campaign_suspension": False,
            "research_authorized": False,
        }
        with self.store._connect() as connection:
            connection.execute(
                """INSERT INTO research_integrity_events(
                    event_id, risk_id, dossier_id, category, severity, state,
                    description, mitigation, reviewer_label, authorization_reference,
                    evidence_refs_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (event["event_id"], risk_id, dossier_id, category, severity, state,
                 description, mitigation.strip(), reviewer_label,
                 authorization_reference.strip(), json.dumps(refs, ensure_ascii=False), created_at),
            )
        return event

    def report(self, dossier_id: str | None = None, limit: int = 500) -> dict:
        if not isinstance(limit, int) or not 1 <= limit <= 2000:
            raise ValueError("limit must be an integer between 1 and 2000")
        with self.store._connect() as connection:
            if dossier_id:
                rows = connection.execute(
                    """SELECT * FROM research_integrity_events WHERE dossier_id=?
                       ORDER BY created_at DESC, event_id DESC LIMIT ?""", (dossier_id, limit)
                ).fetchall()
            else:
                rows = connection.execute(
                    """SELECT * FROM research_integrity_events
                       ORDER BY created_at DESC, event_id LIMIT ?""", (limit,)
                ).fetchall()
        events = []
        latest: dict[str, dict] = {}
        for row in reversed(rows):
            item = dict(row)
            item["evidence_refs"] = json.loads(item.pop("evidence_refs_json"))
            item["hold_recommended"] = item["severity"] in {"high", "critical"} and item["state"] in UNRESOLVED_STATES
            item["automatic_campaign_suspension"] = False
            item["research_authorized"] = False
            events.append(item)
            latest[item["risk_id"]] = item
        risks = list(latest.values())
        return {
            "events": events,
            "risks": risks,
            "risk_count": len(risks),
            "unresolved_high_or_critical": sum(
                item["severity"] in {"high", "critical"} and item["state"] in UNRESOLVED_STATES
                for item in risks
            ),
            "campaign_hold_recommendation": any(
                item["hold_recommended"] for item in risks
            ),
            "automatic_campaign_suspension": False,
            "automatic_research_authorization": False,
            "append_only": True,
        }

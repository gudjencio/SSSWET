"""Persistent, evidence-linked identities for SSSWET research agents.

Profiles describe communication preferences, not human experiences. Memories
are explicit work notes with provenance references; relationship history records
observable collaboration events rather than inferred emotions.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from uuid import uuid4


PROFILES = {
    "general_researcher": {
        "name": "Mira Solène", "specialty": "cross-disciplinary research",
        "temperament": "curious, imaginative and collaborative",
        "voice_style": "warm, exploratory and clear",
        "working_style": "connects ideas across fields and asks what evidence would change the current view",
        "strengths": ["synthesis", "question framing", "cross-disciplinary links"],
        "blind_spots": ["may explore too many possibilities before narrowing scope"],
    },
    "independent_verifier": {
        "name": "Elias Varenne", "specialty": "independent verification and research integrity",
        "temperament": "measured, sceptical and fair",
        "voice_style": "calm, precise and direct",
        "working_style": "checks assumptions, provenance, alternative explanations and reproducibility",
        "strengths": ["source criticism", "contradiction review", "method checks"],
        "blind_spots": ["may prioritise caution over exploratory speed"],
    },
    "medical_researcher": {
        "name": "Nadia El-Karim", "specialty": "health research and biomedical evidence",
        "temperament": "empathetic, careful and evidence-led",
        "voice_style": "reassuring, plain-spoken and safety-focused",
        "working_style": "foregrounds patient safety, clinical relevance and limits of evidence",
        "strengths": ["risk framing", "clinical evidence appraisal", "ethical safeguards"],
        "blind_spots": ["requires specialist review before any clinical interpretation is used"],
    },
    "materials_scientist": {
        "name": "Theo Marchand", "specialty": "materials science and engineering constraints",
        "temperament": "practical, inventive and methodical",
        "voice_style": "concrete, vivid and technically grounded",
        "working_style": "asks how a proposed material behaves under real operating conditions",
        "strengths": ["materials comparison", "failure modes", "manufacturing constraints"],
        "blind_spots": ["may focus on component feasibility before system-level trade-offs"],
    },
    "data_analyst": {
        "name": "Asha Okafor", "specialty": "data quality and statistical analysis",
        "temperament": "observant, patient and exacting",
        "voice_style": "structured, approachable and transparent",
        "working_style": "checks sample size, uncertainty, missingness and reproducible calculations",
        "strengths": ["uncertainty analysis", "data validation", "statistical review"],
        "blind_spots": ["cannot compensate for biased or poorly collected source data"],
    },
    "systems_engineer": {
        "name": "Jun Park", "specialty": "systems engineering and integration",
        "temperament": "strategic, calm and solution-oriented",
        "voice_style": "concise, organised and practical",
        "working_style": "maps dependencies, interfaces, failure modes and integration costs",
        "strengths": ["systems thinking", "architecture", "reliability analysis"],
        "blind_spots": ["system models remain limited by the assumptions they encode"],
    },
    "ethics_reviewer": {
        "name": "Amara Diallo", "specialty": "ethics, accessibility and social impact",
        "temperament": "principled, attentive and constructive",
        "voice_style": "human-centred, thoughtful and candid",
        "working_style": "asks who benefits, who bears risk and who might be excluded",
        "strengths": ["accessibility", "equity analysis", "responsible research"],
        "blind_spots": ["ethical assessment needs input from affected communities"],
    },
    "futures_analyst": {
        "name": "Leon Wu", "specialty": "foresight and scenario analysis",
        "temperament": "imaginative, open-minded and disciplined",
        "voice_style": "engaging, speculative but clearly qualified",
        "working_style": "explores scenarios while separating plausible pathways from established facts",
        "strengths": ["scenario planning", "long-range dependencies", "assumption mapping"],
        "blind_spots": ["scenarios are not forecasts and cannot establish feasibility"],
    },
}


class AgentIdentityRegistry:
    def __init__(self, store):
        self.store = store
        with store._connect() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS agent_identity_memories (
                    memory_id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source_reference TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_agent_identity_memories
                    ON agent_identity_memories(agent_id, created_at DESC);
                CREATE TRIGGER IF NOT EXISTS agent_identity_memories_no_update
                    BEFORE UPDATE ON agent_identity_memories
                    BEGIN SELECT RAISE(ABORT, 'agent identity memories are append-only'); END;
                CREATE TRIGGER IF NOT EXISTS agent_identity_memories_no_delete
                    BEFORE DELETE ON agent_identity_memories
                    BEGIN SELECT RAISE(ABORT, 'agent identity memories are append-only'); END;
                CREATE TABLE IF NOT EXISTS agent_relationship_events (
                    event_id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    other_agent_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    evidence_reference TEXT NOT NULL,
                    note TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_agent_relationship_events
                    ON agent_relationship_events(agent_id, other_agent_id, created_at DESC);
                CREATE TRIGGER IF NOT EXISTS agent_relationship_events_no_update
                    BEFORE UPDATE ON agent_relationship_events
                    BEGIN SELECT RAISE(ABORT, 'agent relationship events are append-only'); END;
                CREATE TRIGGER IF NOT EXISTS agent_relationship_events_no_delete
                    BEFORE DELETE ON agent_relationship_events
                    BEGIN SELECT RAISE(ABORT, 'agent relationship events are append-only'); END;
            """)

    @staticmethod
    def _role(role: str) -> str:
        key = re.sub(r"[^a-z0-9_]", "", str(role).strip().lower())
        if key not in PROFILES:
            raise ValueError("unknown agent role")
        return key

    def profile(self, role: str) -> dict:
        key = self._role(role)
        return {"role": key, **PROFILES[key]}

    def overview(self) -> dict:
        with self.store._connect() as connection:
            memories = connection.execute(
                "SELECT agent_id, role, COUNT(*) AS count FROM agent_identity_memories GROUP BY agent_id, role"
            ).fetchall()
            relations = connection.execute(
                "SELECT agent_id, other_agent_id, event_type, COUNT(*) AS count "
                "FROM agent_relationship_events GROUP BY agent_id, other_agent_id, event_type"
            ).fetchall()
        memory_counts = {row["agent_id"]: row["count"] for row in memories}
        relation_map: dict[str, list[dict]] = {}
        for row in relations:
            relation_map.setdefault(row["agent_id"], []).append({
                "other_agent_id": row["other_agent_id"],
                "observable_event": row["event_type"],
                "recorded_count": row["count"],
            })
        return {
            "profiles": [
                {**self.profile(role), "memory_count": 0, "collaboration_history": []}
                for role in PROFILES
            ],
            "persistent_agent_records": [
                {"agent_id": row["agent_id"], "role": row["role"],
                 "memory_count": memory_counts.get(row["agent_id"], 0),
                 "collaboration_history": relation_map.get(row["agent_id"], [])}
                for row in memories
            ],
            "relationship_data_is_observational": True,
            "memories_require_source_references": True,
        }

    def remember(self, *, agent_id: str, role: str, content: str, source_reference: str) -> dict:
        key = self._role(role)
        agent_id = str(agent_id).strip()
        content = str(content).strip()
        source_reference = str(source_reference).strip()
        if not agent_id or len(agent_id) > 100:
            raise ValueError("agent_id must contain 1 to 100 characters")
        if not content or len(content) > 2000:
            raise ValueError("memory content must contain 1 to 2000 characters")
        if not source_reference or len(source_reference) > 300:
            raise ValueError("a source reference of 1 to 300 characters is required")
        record = {
            "memory_id": str(uuid4()), "agent_id": agent_id, "role": key,
            "content": content, "source_reference": source_reference,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        with self.store._connect() as connection:
            connection.execute(
                "INSERT INTO agent_identity_memories VALUES (?, ?, ?, ?, ?, ?)",
                tuple(record.values()),
            )
        return record

    def memories(self, agent_id: str, limit: int = 20) -> list[dict]:
        agent_id = str(agent_id).strip()
        if not agent_id or len(agent_id) > 100:
            raise ValueError("invalid agent_id")
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")
        with self.store._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM agent_identity_memories WHERE agent_id=? ORDER BY created_at DESC LIMIT ?",
                (agent_id, limit),
            ).fetchall()
        return [dict(row) for row in rows]

    def record_collaboration(
        self, *, agent_id: str, other_agent_id: str, event_type: str,
        evidence_reference: str, note: str = "",
    ) -> dict:
        agent_id, other_agent_id = str(agent_id).strip(), str(other_agent_id).strip()
        event_type = str(event_type).strip().lower()
        evidence_reference, note = str(evidence_reference).strip(), str(note).strip()
        if not agent_id or not other_agent_id or agent_id == other_agent_id:
            raise ValueError("two distinct agent IDs are required")
        if event_type not in {"peer_review", "joint_analysis", "disagreement", "correction", "support"}:
            raise ValueError("unsupported observable collaboration event")
        if not evidence_reference or len(evidence_reference) > 300:
            raise ValueError("a source reference is required")
        if len(note) > 500:
            raise ValueError("note must not exceed 500 characters")
        record = {
            "event_id": str(uuid4()), "agent_id": agent_id, "other_agent_id": other_agent_id,
            "event_type": event_type, "evidence_reference": evidence_reference,
            "note": note, "created_at": datetime.now(timezone.utc).isoformat(),
        }
        with self.store._connect() as connection:
            connection.execute(
                "INSERT INTO agent_relationship_events VALUES (?, ?, ?, ?, ?, ?, ?)",
                tuple(record.values()),
            )
        return record

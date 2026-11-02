"""Evidence-aware, append-only dependency graph for technology dossiers.

Edges are hypotheses until independently supported by cited evidence.
The graph records relationships; it does not infer scientific truth.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4


RELATION_TYPES = {"prerequisite", "enables", "shares_component", "constrains", "informs"}
RELATION_STATES = {"proposed", "supported", "rejected", "superseded"}


class TechnologyDependencyGraph:
    def __init__(self, store):
        self.store = store
        with store._connect() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS technology_relations (
                    relation_id TEXT PRIMARY KEY,
                    prerequisite_id TEXT NOT NULL REFERENCES technology_dossiers(technology_id),
                    dependent_id TEXT NOT NULL REFERENCES technology_dossiers(technology_id),
                    relation_type TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS technology_relation_events (
                    event_id TEXT PRIMARY KEY,
                    relation_id TEXT NOT NULL REFERENCES technology_relations(relation_id),
                    state TEXT NOT NULL,
                    rationale TEXT NOT NULL,
                    source_refs_json TEXT NOT NULL,
                    actor_id TEXT NOT NULL,
                    verifier_actor_id TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_technology_relation_events
                    ON technology_relation_events(relation_id, created_at, event_id);
                CREATE INDEX IF NOT EXISTS idx_technology_relations_from
                    ON technology_relations(prerequisite_id, relation_type);
                CREATE INDEX IF NOT EXISTS idx_technology_relations_to
                    ON technology_relations(dependent_id, relation_type);
                CREATE TRIGGER IF NOT EXISTS technology_relation_events_no_update
                    BEFORE UPDATE ON technology_relation_events
                    BEGIN SELECT RAISE(ABORT, 'technology relation events are append-only'); END;
                CREATE TRIGGER IF NOT EXISTS technology_relation_events_no_delete
                    BEFORE DELETE ON technology_relation_events
                    BEGIN SELECT RAISE(ABORT, 'technology relation events are append-only'); END;
            """)

    @staticmethod
    def _refs(source_refs):
        if not isinstance(source_refs, (list, tuple)):
            raise ValueError("source_refs must be a list")
        refs = []
        for ref in source_refs:
            if not isinstance(ref, str) or not ref.strip() or len(ref.strip()) > 500:
                raise ValueError("source references must be non-empty strings up to 500 characters")
            refs.append(ref.strip())
        return list(dict.fromkeys(refs))

    @staticmethod
    def _event(connection, relation_id, state, rationale, refs, actor_id, verifier_actor_id, now):
        event_id = str(uuid4())
        connection.execute(
            "INSERT INTO technology_relation_events VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (event_id, relation_id, state, rationale, json.dumps(refs, ensure_ascii=False),
             actor_id, verifier_actor_id, now),
        )
        return event_id

    def add_relation(self, *, prerequisite_id, dependent_id, relation_type,
                     rationale, actor_id, source_refs=()):
        if prerequisite_id == dependent_id:
            raise ValueError("a technology cannot be related to itself")
        if relation_type not in RELATION_TYPES:
            raise ValueError("unsupported relation type")
        if not isinstance(rationale, str) or not rationale.strip() or len(rationale) > 4000:
            raise ValueError("rationale must contain 1 to 4000 characters")
        if not isinstance(actor_id, str) or not actor_id.strip():
            raise ValueError("actor_id is required")
        refs = self._refs(source_refs)
        now = datetime.now(timezone.utc).isoformat()
        relation_id = str(uuid4())
        with self.store._connect() as connection:
            for technology_id in (prerequisite_id, dependent_id):
                if not connection.execute(
                    "SELECT 1 FROM technology_dossiers WHERE technology_id=?", (technology_id,)
                ).fetchone():
                    raise ValueError(f"unknown technology dossier: {technology_id}")
            connection.execute(
                "INSERT INTO technology_relations VALUES (?, ?, ?, ?, ?)",
                (relation_id, prerequisite_id, dependent_id, relation_type, now),
            )
            self._event(connection, relation_id, "proposed", rationale.strip(), refs,
                        actor_id.strip(), "", now)
        return self.get_relation(relation_id)

    def review_relation(self, *, relation_id, state, rationale, actor_id,
                        source_refs=(), verifier_actor_id=""):
        if state not in RELATION_STATES:
            raise ValueError("unsupported relation state")
        if not isinstance(rationale, str) or not rationale.strip() or len(rationale) > 4000:
            raise ValueError("rationale must contain 1 to 4000 characters")
        if not isinstance(actor_id, str) or not actor_id.strip():
            raise ValueError("actor_id is required")
        refs = self._refs(source_refs)
        verifier = verifier_actor_id.strip() if isinstance(verifier_actor_id, str) else ""
        if state == "supported":
            if not refs:
                raise ValueError("supporting a relation requires source references")
            if not verifier or verifier == actor_id.strip():
                raise ValueError("support requires a distinct independent verifier")
        now = datetime.now(timezone.utc).isoformat()
        with self.store._connect() as connection:
            relation = connection.execute(
                "SELECT * FROM technology_relations WHERE relation_id=?", (relation_id,)
            ).fetchone()
            if relation is None:
                raise ValueError("technology relation does not exist")
            if state == "supported" and relation["relation_type"] == "prerequisite":
                if self._would_cycle(connection, relation["prerequisite_id"], relation["dependent_id"], relation_id):
                    raise ValueError("supported prerequisite would create a dependency cycle")
            event_id = self._event(connection, relation_id, state, rationale.strip(),
                                    refs, actor_id.strip(), verifier, now)
        return self.get_relation(relation_id)

    @staticmethod
    def _would_cycle(connection, prerequisite_id, dependent_id, excluded_relation_id):
        rows = connection.execute("""
            SELECT r.prerequisite_id, r.dependent_id
            FROM technology_relations r
            JOIN technology_relation_events e ON e.event_id = (
                SELECT e2.event_id FROM technology_relation_events e2
                WHERE e2.relation_id = r.relation_id
                ORDER BY e2.created_at DESC, e2.event_id DESC LIMIT 1
            )
            WHERE r.relation_type='prerequisite' AND e.state='supported'
              AND r.relation_id != ?
        """, (excluded_relation_id,)).fetchall()
        adjacency = {}
        for row in rows:
            adjacency.setdefault(row["prerequisite_id"], set()).add(row["dependent_id"])
        # Adding prerequisite -> dependent closes a cycle iff dependent already reaches prerequisite.
        pending, visited = [dependent_id], set()
        while pending:
            node = pending.pop()
            if node == prerequisite_id:
                return True
            if node in visited:
                continue
            visited.add(node)
            pending.extend(adjacency.get(node, ()))
        return False

    def get_relation(self, relation_id):
        with self.store._connect() as connection:
            relation = connection.execute(
                "SELECT * FROM technology_relations WHERE relation_id=?", (relation_id,)
            ).fetchone()
            if relation is None:
                raise ValueError("technology relation does not exist")
            events = connection.execute(
                "SELECT * FROM technology_relation_events WHERE relation_id=? "
                "ORDER BY created_at, event_id", (relation_id,)
            ).fetchall()
        history = [{
            "event_id": row["event_id"], "state": row["state"],
            "rationale": row["rationale"], "source_refs": json.loads(row["source_refs_json"]),
            "actor_id": row["actor_id"], "verifier_actor_id": row["verifier_actor_id"],
            "created_at": row["created_at"],
        } for row in events]
        return {
            "relation_id": relation["relation_id"],
            "prerequisite_id": relation["prerequisite_id"],
            "dependent_id": relation["dependent_id"],
            "relation_type": relation["relation_type"],
            "state": history[-1]["state"], "history": history,
        }

    def graph(self, *, include_unverified=True):
        with self.store._connect() as connection:
            rows = connection.execute("""
                SELECT r.relation_id FROM technology_relations r
                ORDER BY r.created_at, r.relation_id
            """).fetchall()
        relations = [self.get_relation(row["relation_id"]) for row in rows]
        if not include_unverified:
            relations = [item for item in relations if item["state"] == "supported"]
        return {
            "relations": relations,
            "relation_count": len(relations),
            "supported_count": sum(item["state"] == "supported" for item in relations),
            "proposed_count": sum(item["state"] == "proposed" for item in relations),
            "rejected_count": sum(item["state"] == "rejected" for item in relations),
            "scientific_validity_established": False,
        }

    def dependencies_for(self, technology_id, *, supported_only=False):
        relations = self.graph(include_unverified=not supported_only)["relations"]
        return [item for item in relations
                if item["dependent_id"] == technology_id
                and item["relation_type"] == "prerequisite"]

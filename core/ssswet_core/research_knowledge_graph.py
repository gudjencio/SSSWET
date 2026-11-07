"""Append-only research knowledge graph with bounded provenance-aware impact tracing.

The graph connects research artefacts; it does not certify that any artefact or
relationship is scientifically true.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from uuid import uuid4

NODE_TYPES = {"memory", "claim", "decision", "experiment", "evidence", "technology_dossier", "hypothesis"}
RELATIONS = {"supports", "contradicts", "informs", "tests", "supersedes", "documents", "motivates", "depends_on", "derived_from"}
EDGE_STATES = {"proposed", "reviewed", "withdrawn"}
_ACYCLIC_RELATIONS = {"supersedes", "derived_from"}


class ResearchKnowledgeGraph:
    """Persist immutable research nodes and typed, source-linked relationships."""

    def __init__(self, store):
        self.store = store
        with store._connect() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS research_knowledge_nodes (
                    node_id TEXT PRIMARY KEY,
                    node_type TEXT NOT NULL,
                    label TEXT NOT NULL,
                    source_refs_json TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    actor_id TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS research_knowledge_edges (
                    edge_id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    relation TEXT NOT NULL,
                    state TEXT NOT NULL,
                    rationale TEXT NOT NULL,
                    evidence_refs_json TEXT NOT NULL,
                    actor_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(source_id) REFERENCES research_knowledge_nodes(node_id),
                    FOREIGN KEY(target_id) REFERENCES research_knowledge_nodes(node_id)
                );
                CREATE INDEX IF NOT EXISTS idx_rkg_edges_source ON research_knowledge_edges(source_id);
                CREATE INDEX IF NOT EXISTS idx_rkg_edges_target ON research_knowledge_edges(target_id);
                CREATE TRIGGER IF NOT EXISTS rkg_nodes_no_update BEFORE UPDATE ON research_knowledge_nodes BEGIN
                    SELECT RAISE(ABORT, 'research knowledge nodes are append-only'); END;
                CREATE TRIGGER IF NOT EXISTS rkg_nodes_no_delete BEFORE DELETE ON research_knowledge_nodes BEGIN
                    SELECT RAISE(ABORT, 'research knowledge nodes are append-only'); END;
                CREATE TRIGGER IF NOT EXISTS rkg_edges_no_update BEFORE UPDATE ON research_knowledge_edges BEGIN
                    SELECT RAISE(ABORT, 'research knowledge edges are append-only'); END;
                CREATE TRIGGER IF NOT EXISTS rkg_edges_no_delete BEFORE DELETE ON research_knowledge_edges BEGIN
                    SELECT RAISE(ABORT, 'research knowledge edges are append-only'); END;
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
        return list(dict.fromkeys(cls._text(value, field, 500) for value in values))

    @staticmethod
    def _metadata(value):
        if not isinstance(value, dict):
            raise ValueError("metadata must be a dictionary")
        try:
            encoded = json.dumps(value, ensure_ascii=False, sort_keys=True)
        except (TypeError, ValueError) as exc:
            raise ValueError("metadata must be JSON serializable") from exc
        if len(encoded) > 8000:
            raise ValueError("metadata is too large")
        return encoded

    def add_node(self, *, node_id, node_type, label, actor_id, source_refs=(), metadata=None):
        node_id = self._identifier(node_id, "node_id")
        actor_id = self._identifier(actor_id, "actor_id")
        if node_type not in NODE_TYPES:
            raise ValueError("unsupported node type")
        label = self._text(label, "label", 500)
        refs = self._refs(source_refs, "source reference")
        metadata_json = self._metadata(metadata or {})
        now = datetime.now(timezone.utc).isoformat()
        with self.store._connect() as connection:
            try:
                connection.execute(
                    "INSERT INTO research_knowledge_nodes VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (node_id, node_type, label, json.dumps(refs, ensure_ascii=False), metadata_json, now, actor_id),
                )
            except Exception as exc:
                if "UNIQUE" in str(exc).upper():
                    raise ValueError("node already exists") from exc
                raise
        return self.get_node(node_id)

    def get_node(self, node_id):
        node_id = self._identifier(node_id, "node_id")
        with self.store._connect() as connection:
            row = connection.execute("SELECT * FROM research_knowledge_nodes WHERE node_id=?", (node_id,)).fetchone()
        if row is None:
            raise ValueError("node does not exist")
        return {
            "node_id": row["node_id"], "node_type": row["node_type"], "label": row["label"],
            "source_refs": json.loads(row["source_refs_json"]), "metadata": json.loads(row["metadata_json"]),
            "created_at": row["created_at"], "actor_id": row["actor_id"],
        }

    def _path_exists(self, connection, start, target, relation):
        if start == target:
            return True
        seen = {start}
        frontier = [start]
        while frontier:
            current = frontier.pop()
            rows = connection.execute(
                "SELECT target_id FROM research_knowledge_edges WHERE source_id=? AND relation=? AND state!='withdrawn'",
                (current, relation),
            ).fetchall()
            for row in rows:
                nxt = row["target_id"]
                if nxt == target:
                    return True
                if nxt not in seen:
                    seen.add(nxt)
                    frontier.append(nxt)
        return False

    def link(self, *, source_id, target_id, relation, actor_id, rationale, evidence_refs=(), state="proposed"):
        source_id = self._identifier(source_id, "source_id")
        target_id = self._identifier(target_id, "target_id")
        actor_id = self._identifier(actor_id, "actor_id")
        rationale = self._text(rationale, "rationale", 4000)
        if source_id == target_id:
            raise ValueError("self-links are not allowed")
        if relation not in RELATIONS:
            raise ValueError("unsupported relation")
        if state not in EDGE_STATES:
            raise ValueError("unsupported edge state")
        refs = self._refs(evidence_refs, "evidence reference")
        if not refs:
            raise ValueError("evidence references are required for graph relationships")
        now = datetime.now(timezone.utc).isoformat()
        with self.store._connect() as connection:
            for node_id in (source_id, target_id):
                if connection.execute("SELECT 1 FROM research_knowledge_nodes WHERE node_id=?", (node_id,)).fetchone() is None:
                    raise ValueError(f"node does not exist: {node_id}")
            if relation in _ACYCLIC_RELATIONS and self._path_exists(connection, target_id, source_id, relation):
                raise ValueError(f"{relation} relationship would create a cycle")
            edge_id = str(uuid4())
            connection.execute(
                "INSERT INTO research_knowledge_edges VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (edge_id, source_id, target_id, relation, state, rationale,
                 json.dumps(refs, ensure_ascii=False), actor_id, now),
            )
        return self.get_edge(edge_id)

    def get_edge(self, edge_id):
        edge_id = self._identifier(edge_id, "edge_id")
        with self.store._connect() as connection:
            row = connection.execute("SELECT * FROM research_knowledge_edges WHERE edge_id=?", (edge_id,)).fetchone()
        if row is None:
            raise ValueError("edge does not exist")
        return {
            "edge_id": row["edge_id"], "source_id": row["source_id"], "target_id": row["target_id"],
            "relation": row["relation"], "state": row["state"], "rationale": row["rationale"],
            "evidence_refs": json.loads(row["evidence_refs_json"]), "actor_id": row["actor_id"],
            "created_at": row["created_at"],
        }

    def impact(self, node_id, *, max_depth=5, limit=100, direction="outgoing", relations=None):
        """Trace bounded graph impact in either direction with optional relation filters.

        Outgoing-only traversal remains the default for backwards compatibility.
        """
        node_id = self._identifier(node_id, "node_id")
        if not isinstance(max_depth, int) or isinstance(max_depth, bool) or not 0 <= max_depth <= 20:
            raise ValueError("max_depth must be between 0 and 20")
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 500:
            raise ValueError("limit must be between 1 and 500")
        if direction not in {"outgoing", "incoming", "both"}:
            raise ValueError("direction must be outgoing, incoming or both")
        if relations is not None:
            if not isinstance(relations, (list, tuple, set)) or not relations or any(item not in RELATIONS for item in relations):
                raise ValueError("relations must contain supported relationship types")
            relation_filter = set(relations)
        else:
            relation_filter = None

        self.get_node(node_id)
        results = []
        queue = [(node_id, 0, [node_id], [])]
        visited = {node_id}
        with self.store._connect() as connection:
            while queue and len(results) < limit:
                current, depth, path, path_relations = queue.pop(0)
                if depth >= max_depth:
                    continue
                rows = []
                if direction in {"outgoing", "both"}:
                    rows.extend((row, row["target_id"], "outgoing") for row in connection.execute(
                        "SELECT * FROM research_knowledge_edges WHERE source_id=? AND state!='withdrawn' ORDER BY rowid",
                        (current,),
                    ).fetchall())
                if direction in {"incoming", "both"}:
                    rows.extend((row, row["source_id"], "incoming") for row in connection.execute(
                        "SELECT * FROM research_knowledge_edges WHERE target_id=? AND state!='withdrawn' ORDER BY rowid",
                        (current,),
                    ).fetchall())
                for row, target, traversal in rows:
                    if target in visited or (relation_filter is not None and row["relation"] not in relation_filter):
                        continue
                    visited.add(target)
                    next_depth = depth + 1
                    next_path = path + [target]
                    next_relations = path_relations + [row["relation"]]
                    node_row = connection.execute(
                        "SELECT * FROM research_knowledge_nodes WHERE node_id=?", (target,)
                    ).fetchone()
                    if node_row is None:
                        continue
                    node = {
                        "node_id": node_row["node_id"], "node_type": node_row["node_type"],
                        "label": node_row["label"], "source_refs": json.loads(node_row["source_refs_json"]),
                        "metadata": json.loads(node_row["metadata_json"]),
                        "created_at": node_row["created_at"], "actor_id": node_row["actor_id"],
                    }
                    results.append({
                        "node": node, "depth": next_depth, "path": next_path,
                        "relations": next_relations, "edge_id": row["edge_id"],
                        "traversal": traversal,
                    })
                    if next_depth < max_depth:
                        queue.append((target, next_depth, next_path, next_relations))
                    if len(results) >= limit:
                        break
        return results

"""Local, read-only HTTP interface for the SSSWET research core."""
from __future__ import annotations

import argparse
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from .engine import SSSWETEngine
from .persistence import SQLiteResearchStore

WEB_ROOT = Path(__file__).resolve().parents[2] / "web"


def public_status(engine: SSSWETEngine, store: SQLiteResearchStore | None = None) -> dict[str, Any]:
    agents = list(engine.orchestrator.bot_manager.agents.values())
    return {
        "service": "SSSWET",
        "mode": "local_read_only",
        "agents_total": len(agents),
        "agents_active": sum(1 for agent in agents if agent.load > 0),
        "tasks_queued": len(engine.orchestrator.tasks),
        "events_total": len(store.recent_events(200)) if store else len(engine.orchestrator.events),
        "research_runs": len(store.recent_tasks(100)) if store else 0,
        "verified_knowledge": len(engine.memory.validated()),
    }


def public_events(engine: SSSWETEngine, store: SQLiteResearchStore | None = None) -> list[dict[str, Any]]:
    if store:
        return store.recent_events(50)
    return [
        {"kind": event.kind, "message": event.message, "task_id": event.task_id, "agent_id": event.agent_id}
        for event in engine.orchestrator.events[-50:]
    ]


def make_handler(engine: SSSWETEngine, store: SQLiteResearchStore):
    class SSSWETHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

        def _json(self, payload: Any, status: int = 200) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            from urllib.parse import parse_qs, urlsplit
            parsed = urlsplit(self.path)
            path = parsed.path
            if path == "/api/status":
                self._json(public_status(engine, store))
            elif path == "/api/events":
                self._json(public_events(engine, store))
            elif path == "/api/work":
                self._json(store.recent_tasks(30))
            elif path == "/api/discoveries":
                self._json(store.recent_steps(50))
            elif path == "/api/verified":
                self._json(engine.memory.export_validated())
            elif path == "/api/memory":
                self._json({"items": store.collective_memory_items(limit=200)})
            elif path == "/api/memory/search":
                from .collective_memory import search_collective_memory
                params = parse_qs(parsed.query)
                query = params.get("q", [""])[0]
                try:
                    limit = int(params.get("limit", ["20"])[0])
                except ValueError:
                    self._json({"error": "The limit parameter must be an integer"}, 400)
                    return
                if not query.strip():
                    self._json({"error": "A non-empty q parameter is required"}, 400)
                    return
                self._json({
                    "query": query,
                    "method": "lexical_overlap",
                    "scientific_validity_established": False,
                    "results": search_collective_memory(
                        store.collective_memory_items(limit=500),
                        query,
                        limit=limit,
                    ),
                })
            elif path == "/api/scientific-memory":
                from .scientific_memory import ScientificMemoryService
                params = parse_qs(parsed.query)
                query = params.get("q", [""])[0]
                try:
                    limit = int(params.get("limit", ["200"])[0])
                except ValueError:
                    self._json({"error": "The limit parameter must be an integer"}, 400)
                    return
                self._json(ScientificMemoryService(store).overview(query=query, limit=limit))
            elif path == "/api/research-timeline":
                from .research_timeline import ResearchTimeline
                params = parse_qs(parsed.query)
                campaign_id = params.get("campaign_id", [""])[0]
                try:
                    limit = int(params.get("limit", ["200"])[0])
                except ValueError:
                    self._json({"error": "The limit parameter must be an integer"}, 400)
                    return
                self._json(ResearchTimeline(store).build(campaign_id=campaign_id, limit=limit))
            elif path == "/api/scientific-memory/suggestions":
                from .scientific_memory import ScientificMemoryService
                from .research_gaps import ResearchGapAnalyzer
                overview = ScientificMemoryService(store).overview(limit=500)
                gaps = ResearchGapAnalyzer().report(store.knowledge_graph(limit=500))
                contested = [
                    {"version_id": item["version_id"], "memory_key": item["memory_key"],
                     "topic": item["topic"], "statement": item["statement"],
                     "graph_node_ids": item["contested_graph_node_ids"],
                     "suggestion": "Review the linked contradiction and compare source methods and provenance."}
                    for item in overview["versions"] if item["contested_by_graph"]
                ]
                self._json({
                    "research_gaps": gaps.get("gaps", []),
                    "contested_memory": contested,
                    "automatic_task_creation": False,
                    "scientific_validity_established": False,
                })
            elif path == "/api/literature-watch":
                self._json({"reports": store.literature_watch_history(limit=100)})
            elif path == "/api/literature-watch/campaigns":
                self._json({
                    "subscriptions": store.campaign_watch_subscriptions(),
                    "runs": store.campaign_watch_run_history(limit=200),
                })
            elif path == "/api/knowledge-graph":
                self._json(store.knowledge_graph(limit=500))
            elif path == "/api/research-gaps":
                from .research_gaps import ResearchGapAnalyzer
                self._json(ResearchGapAnalyzer().report(store.knowledge_graph(limit=500)))
            elif path == "/api/research-opportunities":
                from .research_opportunities import ResearchOpportunitySynthesizer
                params = parse_qs(parsed.query)
                try:
                    limit = int(params.get("limit", ["100"])[0])
                except ValueError:
                    self._json({"error": "limit must be an integer"}, 400)
                    return
                self._json(ResearchOpportunitySynthesizer(store).build(limit=limit))
            elif path == "/api/research-relations":
                from .research_relations import ResearchRelationDiscovery
                params = parse_qs(parsed.query)
                try:
                    limit = int(params.get("limit", ["100"])[0])
                    minimum = int(params.get("minimum_shared_terms", ["2"])[0])
                except ValueError:
                    self._json({"error": "limit and minimum_shared_terms must be integers"}, 400)
                    return
                self._json(ResearchRelationDiscovery(store).discover(limit=limit, minimum_shared_terms=minimum))
            elif path == "/api/digital-lab":
                from .digital_lab import DigitalLabService
                params = parse_qs(parsed.query)
                try:
                    limit = int(params.get("limit", ["200"])[0])
                except ValueError:
                    self._json({"error": "The limit parameter must be an integer"}, 400)
                    return
                self._json(DigitalLabService(store).overview(limit=limit))
            elif path == "/api/digital-lab/proposals":
                from .protocol_proposals import ProtocolProposalService
                params = parse_qs(parsed.query)
                try:
                    limit = int(params.get("limit", ["200"])[0])
                except ValueError:
                    self._json({"error": "The limit parameter must be an integer"}, 400)
                    return
                self._json(ProtocolProposalService(store).overview(limit=limit))
            elif path == "/api/digital-lab/reproduction-matrix":
                from .digital_lab import DigitalLabService
                params = parse_qs(parsed.query)
                try:
                    limit = int(params.get("limit", ["200"])[0])
                except ValueError:
                    self._json({"error": "The limit parameter must be an integer"}, 400)
                    return
                self._json(DigitalLabService(store).reproduction_matrix(limit=limit))
            elif path == "/api/digital-lab/datasets":
                from .dataset_registry import DatasetRegistry
                params = parse_qs(parsed.query)
                try:
                    limit = int(params.get("limit", ["200"])[0])
                except ValueError:
                    self._json({"error": "The limit parameter must be an integer"}, 400)
                    return
                self._json(DatasetRegistry(store).overview(limit=limit))
            elif path == "/api/evidence-dossiers":
                from .evidence_dossiers import EvidenceDossierService
                params = parse_qs(parsed.query)
                try:
                    limit = int(params.get("limit", ["100"])[0])
                except ValueError:
                    self._json({"error": "The limit parameter must be an integer"}, 400)
                    return
                try:
                    self._json(EvidenceDossierService(store).overview(limit=limit))
                except ValueError as exc:
                    self._json({"error": str(exc)}, 400)
            elif path.startswith("/api/evidence-dossiers/"):
                from .evidence_dossiers import EvidenceDossierService
                dossier_id = path[len("/api/evidence-dossiers/"):].strip("/")
                if not dossier_id:
                    self._json({"error": "dossier id is required"}, 400)
                    return
                try:
                    self._json(EvidenceDossierService(store).get(dossier_id))
                except ValueError as exc:
                    self._json({"error": str(exc)}, 404)
            elif path == "/api/experiments":
                self._json({"experiments": store.experiment_overview(limit=100)})
            elif path == "/api/optimization":
                self._json({"cycles": store.adaptive_cycle_history(limit=100)})
            elif path == "/api/campaigns":
                self._json({"campaigns": store.campaign_history(limit=100)})
            elif path == "/api/resources":
                self._json({"snapshots": store.resource_snapshot_history(limit=50)})
            elif path == "/api/lab-discrepancies":
                from .lab_discrepancies import LabDiscrepancyAnalyzer
                params = parse_qs(parsed.query)
                try:
                    limit = int(params.get("limit", ["200"])[0])
                except ValueError:
                    self._json({"error": "limit must be an integer"}, 400)
                    return
                try:
                    self._json(LabDiscrepancyAnalyzer(store).build(limit=limit))
                except ValueError as exc:
                    self._json({"error": str(exc)}, 400)
            elif path == "/api/lab-verification-plans":
                from .lab_verification import LabVerificationPlanner
                params = parse_qs(parsed.query)
                try:
                    limit = int(params.get("limit", ["200"])[0])
                except ValueError:
                    self._json({"error": "limit must be an integer"}, 400)
                    return
                try:
                    self._json(LabVerificationPlanner(store).build(limit=limit))
                except ValueError as exc:
                    self._json({"error": str(exc)}, 400)
            elif path == "/api/disputes":
                from .disputes import DisputeResolutionService
                service = DisputeResolutionService(store)
                self._json({
                    "detected_contradictions": service.detected(),
                    "review_cases": store.dispute_history(limit=500),
                    "automatic_adjudication": False,
                    "scientific_validity_changed": False,
                })
            elif path == "/api/collaboration/peer-reviews":
                from .peer_review import PeerReviewService
                params = parse_qs(parsed.query)
                try:
                    limit = int(params.get("limit", ["200"])[0])
                except ValueError:
                    self._json({"error": "The limit parameter must be an integer"}, 400)
                    return
                self._json(PeerReviewService(store).report(limit=limit))
            elif path == "/api/collaboration/recommendations":
                from .collaboration_recommender import CollaborationRecommender, recommendation_to_dict
                self._json({
                    "recommendations": [recommendation_to_dict(item) for item in CollaborationRecommender(store).recommend()],
                    "automatic_transfers": False,
                    "scientific_validity_established": False,
                })
            elif path == "/api/collaboration/transfers":
                self._json({"transfers": store.knowledge_transfer_history(limit=200)})
            elif path.startswith("/api/collaboration/campaign/") and path.endswith("/conflicts"):
                campaign_id = path[len("/api/collaboration/campaign/"):-len("/conflicts")].strip("/")
                from urllib.parse import unquote
                self._json(store.campaign_conflict_report(unquote(campaign_id)))
            elif path == "/health":
                self._json({"status": "ok"})
            elif path.startswith("/api/"):
                self._json({"error": "Unknown read-only API endpoint"}, 404)
            else:
                super().do_GET()

        def do_POST(self) -> None:
            self.send_error(405, "The public interface is read-only")

        def do_PUT(self) -> None:
            self.send_error(405, "The public interface is read-only")

        def do_DELETE(self) -> None:
            self.send_error(405, "The public interface is read-only")

    return SSSWETHandler


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local SSSWET interface")
    parser.add_argument("--host", default="127.0.0.1", help="Bind address (default: loopback only)")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--database", default=".ssswet/ssswet.sqlite3", help="SQLite research history path")
    args = parser.parse_args()

    store = SQLiteResearchStore(args.database)
    engine = SSSWETEngine(store=store)
    server = ThreadingHTTPServer((args.host, args.port), make_handler(engine, store))
    print(f"SSSWET local interface: http://{args.host}:{args.port}")
    print(f"Persistent research history: {store.path}")
    print("Read-only mode: arbitrary public task submission is disabled.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

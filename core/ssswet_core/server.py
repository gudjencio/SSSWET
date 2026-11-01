"""Local, read-only HTTP interface for the SSSWET research core."""
from __future__ import annotations

import argparse
import json
import hmac
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from .engine import SSSWETEngine
from .persistence import SQLiteResearchStore

WEB_ROOT = Path(__file__).resolve().parents[2] / "web"
ALLOWED_WEB_ORIGINS = {
    "https://gudjencio.github.io",
    "https://sites.google.com",
    "http://sites.google.com",
}


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


def make_handler(engine: SSSWETEngine, store: SQLiteResearchStore, order_registry=None, admin_token: str | None = None, priority_assessments=None):
    if priority_assessments is None:
        from .priority_assessments import PriorityAssessmentStore
        priority_assessments = PriorityAssessmentStore(store.path)
    class SSSWETHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

        def _json(self, payload: Any, status: int = 200) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            origin = self.headers.get("Origin")
            if origin in ALLOWED_WEB_ORIGINS and self.path.startswith("/api/"):
                self.send_header("Access-Control-Allow-Origin", origin)
                self.send_header("Vary", "Origin")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)

        def _private_admin_allowed(self) -> bool:
            from urllib.parse import urlsplit
            if self.client_address[0] not in {"127.0.0.1", "::1"}:
                return False
            host = (self.headers.get("Host") or "").split(":")[0].strip("[]").lower()
            if host not in {"localhost", "127.0.0.1", "::1"}:
                return False
            origin = self.headers.get("Origin")
            if origin and urlsplit(origin).hostname not in {"localhost", "127.0.0.1", "::1"}:
                return False
            supplied = self.headers.get("X-SSSWET-Admin-Token", "")
            return bool(admin_token) and hmac.compare_digest(supplied, admin_token)

        def do_OPTIONS(self) -> None:
            from urllib.parse import urlsplit
            origin = self.headers.get("Origin", "")
            path = urlsplit(self.path).path
            if origin not in ALLOWED_WEB_ORIGINS or not path.startswith("/api/"):
                self.send_error(403, "Origin is not allowed")
                return
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Accept, Content-Type")
            self.send_header("Access-Control-Max-Age", "600")
            if self.headers.get("Access-Control-Request-Private-Network", "").lower() == "true":
                self.send_header("Access-Control-Allow-Private-Network", "true")
            self.end_headers()

        def do_GET(self) -> None:
            from urllib.parse import parse_qs, urlsplit
            parsed = urlsplit(self.path)
            path = parsed.path
            if path.startswith("/api/private/orders"):
                if not self._private_admin_allowed():
                    self._json({"error": "Local administrator authentication required"}, 401)
                    return
                if order_registry is None:
                    self._json({"error": "Private order register is not configured"}, 503)
                    return
                if path == "/api/private/orders":
                    try:
                        limit = int(parse_qs(parsed.query).get("limit", ["100"])[0])
                        self._json(order_registry.list_orders(limit=limit))
                    except ValueError as exc:
                        self._json({"error": str(exc)}, 400)
                else:
                    order_id = path[len("/api/private/orders/"):].strip("/")
                    try:
                        self._json(order_registry.get_order(order_id))
                    except ValueError as exc:
                        self._json({"error": str(exc)}, 404)
            elif path == "/api/status":
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
            elif path == "/api/research-priority-assessments":
                try:
                    self._json(priority_assessments.overview(limit=int(parse_qs(parsed.query).get("limit", ["300"])[0])))
                except ValueError as exc:
                    self._json({"error": str(exc)}, 400)
            elif path == "/api/research-priority-framework":
                from .priority_framework import framework_definition
                self._json(framework_definition())
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
            elif path == "/api/technology-feasibility":
                from .technology_feasibility import TechnologyFeasibilityObservatory
                params = parse_qs(parsed.query)
                technology = params.get("technology", [""])[0] or None
                try:
                    self._json(TechnologyFeasibilityObservatory(store).build(technology=technology))
                except ValueError as exc:
                    self._json({"error": str(exc)}, 400)
            elif path == "/api/research-journal":
                from .research_journal import ResearchJournal
                params = parse_qs(parsed.query)
                technology = params.get("technology", [""])[0] or None
                try:
                    limit = int(params.get("limit", ["100"])[0])
                    self._json(ResearchJournal(store).overview(technology=technology, limit=limit))
                except ValueError as exc:
                    self._json({"error": str(exc)}, 400)
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
            elif path == "/api/lab-statistical-summaries":
                from .lab_statistics import LabStatisticalSummarizer
                params = parse_qs(parsed.query)
                try:
                    limit = int(params.get("limit", ["200"])[0])
                    self._json(LabStatisticalSummarizer(store).build(limit=limit))
                except ValueError as exc:
                    self._json({"error": str(exc)}, 400)
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
            elif path == "/api/parameter-interaction-plans":
                from .parameter_interactions import ParameterInteractionPlanner
                params = parse_qs(parsed.query)
                try:
                    limit = int(params.get("limit", ["200"])[0])
                    self._json(ParameterInteractionPlanner(store).build(limit=limit))
                except ValueError as exc:
                    self._json({"error": str(exc)}, 400)
            elif path == "/api/parameter-sensitivity-plans":
                from .parameter_sensitivity import ParameterSensitivityPlanner
                params = parse_qs(parsed.query)
                try:
                    limit = int(params.get("limit", ["200"])[0])
                    self._json(ParameterSensitivityPlanner(store).build(limit=limit))
                except ValueError as exc:
                    self._json({"error": str(exc)}, 400)
            elif path == "/api/reproducibility-intelligence":
                from .reproducibility_intelligence import ReproducibilityIntelligence
                params = parse_qs(parsed.query)
                try:
                    limit = int(params.get("limit", ["200"])[0])
                    self._json(ReproducibilityIntelligence(store).build(limit=limit))
                except ValueError as exc:
                    self._json({"error": str(exc)}, 400)
            elif path == "/api/lab-verification-events":
                self._json({"events": store.lab_verification_event_history(limit=1000), "append_only": True})
            elif path == "/api/disputes":
                from .disputes import DisputeResolutionService
                service = DisputeResolutionService(store)
                self._json({
                    "detected_contradictions": service.detected(),
                    "review_cases": store.dispute_history(limit=500),
                    "automatic_adjudication": False,
                    "scientific_validity_changed": False,
                })
            elif path == "/api/research-integrity":
                from .research_integrity import ResearchIntegrityRegister
                params = parse_qs(parsed.query)
                dossier_id = params.get("dossier_id", [""])[0] or None
                try:
                    limit = int(params.get("limit", ["500"])[0])
                    self._json(ResearchIntegrityRegister(store).report(dossier_id=dossier_id, limit=limit))
                except ValueError as exc:
                    self._json({"error": str(exc)}, 400)
            elif path == "/api/scientific-review-board":
                from .scientific_review_board import ScientificReviewBoard
                params = parse_qs(parsed.query)
                dossier_id = params.get("dossier_id", [""])[0] or None
                try:
                    limit = int(params.get("limit", ["500"])[0])
                    self._json(ScientificReviewBoard(store).report(dossier_id=dossier_id, limit=limit))
                except ValueError as exc:
                    self._json({"error": str(exc)}, 400)
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
            from urllib.parse import urlsplit
            if self.client_address[0] not in {"127.0.0.1", "::1"}:
                self.send_error(403, "Verification reviews are restricted to the local machine")
                return
            request_path = urlsplit(self.path).path
            private_order_write = (
                request_path == "/api/private/orders"
                or request_path.endswith("/payments")
                or request_path.endswith("/fulfilment")
            ) and request_path.startswith("/api/private/orders")
            if private_order_write and not self._private_admin_allowed():
                self._json({"error": "Local administrator authentication required"}, 401)
                return
            if request_path not in {"/api/lab-verification-events", "/api/scientific-review-board/reviews", "/api/research-integrity/risks", "/api/research-journal", "/api/research-priority-assessments"} and not private_order_write:
                self.send_error(405, "Unsupported write operation")
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length < 1 or length > 8192:
                    self._json({"error": "Request body must be between 1 and 8192 bytes"}, 400)
                    return
                payload = json.loads(self.rfile.read(length))
                if not isinstance(payload, dict):
                    raise ValueError("A JSON object is required")
                if private_order_write:
                    if order_registry is None:
                        self._json({"error": "Private order register is not configured"}, 503)
                        return
                    if request_path == "/api/private/orders":
                        order = order_registry.create_order(
                            technology=payload.get("technology", ""),
                            currency=payload.get("currency", ""),
                            base_price=payload.get("base_price", ""),
                            access_contribution=payload.get("access_contribution", "0"),
                        )
                        self._json({"order": order, "personal_data_stored": False}, 201)
                    elif request_path.endswith("/payments"):
                        order_id = request_path[len("/api/private/orders/"):-len("/payments")].strip("/")
                        order = order_registry.record_verified_payment(
                            order_id=order_id, amount=payload.get("amount", ""),
                            currency=payload.get("currency", ""),
                            provider=payload.get("provider", ""),
                            provider_reference=payload.get("provider_reference", ""),
                            verified_by=payload.get("verified_by", ""),
                        )
                        self._json({"order": order, "manual_verification_required": True}, 201)
                    else:
                        order_id = request_path[len("/api/private/orders/"):-len("/fulfilment")].strip("/")
                        order = order_registry.update_fulfilment(
                            order_id=order_id, state=payload.get("state", ""),
                            operator=payload.get("operator", ""),
                            evidence_reference=payload.get("evidence_reference", ""),
                        )
                        self._json({"order": order}, 201)
                elif request_path == "/api/research-priority-assessments":
                    assessment = priority_assessments.append(payload)
                    self._json({"assessment": assessment, "append_only": True,
                                "automatic_funding_decisions": False,
                                "scientific_validity_established": False}, 201)
                elif request_path == "/api/research-journal":
                    from .research_journal import ResearchJournal
                    entry = ResearchJournal(store).append(
                        technology=payload.get("technology", ""), event_type=payload.get("event_type", ""),
                        title=payload.get("title", ""), summary=payload.get("summary", ""),
                        state=payload.get("state", "planned"), classification=payload.get("classification", "project_update"),
                        evidence_refs=payload.get("evidence_refs", []), author_label=payload.get("author_label", "Project team"),
                    )
                    self._json({"entry": entry, "append_only": True, "scientific_validity_established": False}, 201)
                elif request_path == "/api/lab-verification-events":
                    from .lab_verification import LabVerificationPlanner
                    event = LabVerificationPlanner(store).record_check_review(
                        str(payload.get("plan_id", "")), str(payload.get("check_code", "")),
                        str(payload.get("state", "")), str(payload.get("note", "")),
                        str(payload.get("reviewer", "")),
                    )
                    self._json({"event": event, "append_only": True}, 201)
                elif request_path == "/api/scientific-review-board/reviews":
                    from .scientific_review_board import ScientificReviewBoard
                    review = ScientificReviewBoard(store).submit(
                        dossier_id=payload.get("dossier_id", ""),
                        reviewer_id=payload.get("reviewer_id", ""),
                        reviewer_campaign_id=payload.get("reviewer_campaign_id", ""),
                        verdict=payload.get("verdict", ""),
                        conflict_status=payload.get("conflict_status", ""),
                        rationale=payload.get("rationale", ""),
                        methods_assessment=payload.get("methods_assessment", ""),
                        limitations=payload.get("limitations", ""),
                        evidence_refs=payload.get("evidence_refs", []),
                    )
                    self._json({"review": review, "append_only": True}, 201)
                else:
                    from .research_integrity import ResearchIntegrityRegister
                    event = ResearchIntegrityRegister(store).record(
                        dossier_id=payload.get("dossier_id", ""),
                        category=payload.get("category", ""),
                        severity=payload.get("severity", ""),
                        description=payload.get("description", ""),
                        reviewer_label=payload.get("reviewer_label", ""),
                        state=payload.get("state", "open"),
                        mitigation=payload.get("mitigation", ""),
                        authorization_reference=payload.get("authorization_reference", ""),
                        evidence_refs=payload.get("evidence_refs", []),
                    )
                    self._json({"event": event, "append_only": True}, 201)
            except (ValueError, TypeError, json.JSONDecodeError) as exc:
                self._json({"error": str(exc)}, 400)

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
    parser.add_argument("--orders-database", default=".ssswet/orders.sqlite3", help="Private order register path")
    parser.add_argument("--admin-token", default=os.environ.get("SSSWET_ADMIN_TOKEN"), help="Private order dashboard token (or SSSWET_ADMIN_TOKEN environment variable)")
    args = parser.parse_args()

    store = SQLiteResearchStore(args.database)
    engine = SSSWETEngine(store=store)
    from .order_registry import PrivateOrderRegistry
    order_registry = PrivateOrderRegistry(args.orders_database)
    if args.admin_token and len(args.admin_token) < 32:
        parser.error("SSSWET_ADMIN_TOKEN must contain at least 32 characters when configured.")
    server = ThreadingHTTPServer((args.host, args.port), make_handler(engine, store, order_registry, args.admin_token))
    print(f"SSSWET local interface: http://{args.host}:{args.port}")
    print(f"Persistent research history: {store.path}")
    print("Private order administration: token-protected and loopback-only.")
    print("Public browser API access: restricted to the official GitHub Pages and Google Sites origins.")
    if not args.admin_token:
        print("Private order dashboard is disabled until SSSWET_ADMIN_TOKEN is configured.")
    print("Read-only mode: arbitrary public task submission is disabled.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

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
            path = self.path.split("?", 1)[0]
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
            elif path == "/api/knowledge-graph":
                self._json(store.knowledge_graph(limit=500))
            elif path == "/api/research-gaps":
                from .research_gaps import ResearchGapAnalyzer
                self._json(ResearchGapAnalyzer().report(store.knowledge_graph(limit=500)))
            elif path == "/api/experiments":
                self._json({"experiments": store.experiment_overview(limit=100)})
            elif path == "/api/optimization":
                self._json({"cycles": store.adaptive_cycle_history(limit=100)})
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

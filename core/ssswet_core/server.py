"""Local, read-only HTTP interface for the SSSWET research core.

Run with: python -m ssswet_core.server
The server binds to loopback by default and does not accept public research input.
"""
from __future__ import annotations

import argparse
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from .engine import SSSWETEngine

WEB_ROOT = Path(__file__).resolve().parents[2] / "web"


def public_status(engine: SSSWETEngine) -> dict[str, Any]:
    agents = list(engine.orchestrator.bot_manager.agents.values())
    return {
        "service": "SSSWET",
        "mode": "local_read_only",
        "agents_total": len(agents),
        "agents_active": sum(1 for agent in agents if agent.load > 0),
        "tasks_queued": len(engine.orchestrator.tasks),
        "events_total": len(engine.orchestrator.events),
        "verified_knowledge": len(engine.memory.validated()),
    }


def public_events(engine: SSSWETEngine) -> list[dict[str, Any]]:
    return [
        {
            "kind": event.kind,
            "message": event.message,
            "task_id": event.task_id,
            "agent_id": event.agent_id,
        }
        for event in engine.orchestrator.events[-50:]
    ]


def make_handler(engine: SSSWETEngine):
    class SSSWETHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

        def do_GET(self) -> None:
            routes = {
                "/api/status": lambda: public_status(engine),
                "/api/events": lambda: public_events(engine),
                "/api/verified": lambda: engine.memory.export_validated(),
            }
            if self.path in routes:
                payload = json.dumps(routes[self.path](), ensure_ascii=False).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(payload)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(payload)
                return
            if self.path == "/health":
                payload = b'{"status":"ok"}'
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return
            if self.path.startswith("/api/"):
                self.send_error(404, "Unknown read-only API endpoint")
                return
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
    args = parser.parse_args()

    engine = SSSWETEngine()
    server = ThreadingHTTPServer((args.host, args.port), make_handler(engine))
    print(f"SSSWET local interface: http://{args.host}:{args.port}")
    print("Read-only mode: arbitrary public task submission is disabled.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

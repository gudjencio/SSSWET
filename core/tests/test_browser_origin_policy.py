from __future__ import annotations

import json
import threading
from http.server import ThreadingHTTPServer
from types import SimpleNamespace
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from ssswet_core.engine import SSSWETEngine
from ssswet_core.persistence import SQLiteResearchStore
from ssswet_core import server as server_module
from ssswet_core.server import make_handler


def start_server(tmp_path):
    store = SQLiteResearchStore(tmp_path / "origin-policy.sqlite3")
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        make_handler(SSSWETEngine(store=store), store),
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, f"http://127.0.0.1:{server.server_port}"


def stop_server(server, thread):
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)


def test_shared_google_sites_origin_remains_read_only_by_default():
    assert "https://sites.google.com" in server_module.DEFAULT_WEB_ORIGINS
    assert "http://sites.google.com" in server_module.DEFAULT_WEB_ORIGINS
    assert "https://sites.google.com" not in server_module.DEFAULT_WRITE_ORIGINS
    assert "http://sites.google.com" not in server_module.DEFAULT_WRITE_ORIGINS


def test_google_sites_can_read_but_cannot_write_even_if_accidentally_allowlisted(tmp_path, monkeypatch):
    monkeypatch.setattr(server_module, "ALLOWED_WEB_ORIGINS", {
        "https://gudjencio.github.io", "https://sites.google.com",
    })
    monkeypatch.setattr(server_module, "ALLOWED_WRITE_ORIGINS", {
        "https://gudjencio.github.io", "https://sites.google.com",
    })
    monkeypatch.setenv("SSSWET_GITHUB_TOKEN", "test-token")
    server, thread, base = start_server(tmp_path)
    body = json.dumps({
        "category": "bug", "title": "Origin test",
        "description": "A browser-origin policy regression test",
    }).encode()
    try:
        read = Request(base + "/api/status", headers={"Origin": "https://sites.google.com"})
        with urlopen(read) as response:
            assert response.status == 200
            assert response.headers["Access-Control-Allow-Origin"] == "https://sites.google.com"

        preflight = Request(
            base + "/api/project-reports",
            headers={
                "Origin": "https://sites.google.com",
                "Access-Control-Request-Method": "POST",
            },
            method="OPTIONS",
        )
        with pytest.raises(HTTPError) as rejected_preflight:
            urlopen(preflight)
        assert rejected_preflight.value.code == 403

        report = Request(
            base + "/api/project-reports", data=body,
            headers={"Origin": "https://sites.google.com", "Content-Type": "application/json"},
            method="POST",
        )
        with pytest.raises(HTTPError) as rejected_report:
            urlopen(report)
        assert rejected_report.value.code == 403

        journal = Request(
            base + "/api/research-journal",
            data=json.dumps({
                "technology": "test", "event_type": "research_question",
                "title": "Origin policy", "summary": "Must reject shared Google Sites writes.",
            }).encode(),
            headers={"Origin": "https://sites.google.com", "Content-Type": "application/json"},
            method="POST",
        )
        with pytest.raises(HTTPError) as rejected_journal:
            urlopen(journal)
        assert rejected_journal.value.code == 403
    finally:
        stop_server(server, thread)


def test_dedicated_github_pages_origin_can_submit_reports_and_missing_origin_cannot(tmp_path, monkeypatch):
    from ssswet_core import project_reports

    monkeypatch.setenv("SSSWET_GITHUB_TOKEN", "test-token")
    monkeypatch.setattr(
        project_reports, "create_project_report",
        lambda payload: {"submitted": True, "changes_applied": False},
    )
    server, thread, base = start_server(tmp_path)
    body = json.dumps({
        "category": "bug", "title": "Approved origin",
        "description": "A controlled test submission",
    }).encode()
    try:
        approved = Request(
            base + "/api/project-reports", data=body,
            headers={
                "Origin": "https://gudjencio.github.io",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urlopen(approved) as response:
            assert response.status == 201
            assert response.headers["Access-Control-Allow-Origin"] == "https://gudjencio.github.io"
            assert json.loads(response.read())["submitted"] is True

        missing = Request(
            base + "/api/project-reports", data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with pytest.raises(HTTPError) as rejected:
            urlopen(missing)
        assert rejected.value.code == 403
    finally:
        stop_server(server, thread)


def test_local_cli_write_without_origin_remains_supported(tmp_path):
    server, thread, base = start_server(tmp_path)
    request = Request(
        base + "/api/research-journal",
        data=json.dumps({
            "technology": "timetravel", "event_type": "research_question",
            "title": "Local CLI compatibility", "summary": "No browser Origin header.",
        }).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request) as response:
            assert response.status == 201
    finally:
        stop_server(server, thread)


def test_loopback_origin_cannot_be_spoofed_by_a_remote_client(tmp_path):
    store = SQLiteResearchStore(tmp_path / "loopback-origin.sqlite3")
    handler = make_handler(SSSWETEngine(store=store), store)
    remote = SimpleNamespace(client_address=("203.0.113.10", 45678))
    local = SimpleNamespace(client_address=("127.0.0.1", 45678))

    assert not handler._public_browser_origin_allowed(remote, "http://localhost:8765")
    assert not handler._public_browser_origin_allowed(remote, "http://127.0.0.1:8765")
    assert handler._public_browser_origin_allowed(local, "http://localhost:8765")
    assert handler._public_browser_origin_allowed(remote, "https://gudjencio.github.io")


@pytest.mark.parametrize("origin", [
    "null",
    "ftp://gudjencio.github.io",
    "https://user@gudjencio.github.io",
    "https://sites.google.com/path",
    "https://evil.sites.google.com",
    "https://sites.google.com.evil.example",
    "http://localhost:99999",
])
def test_malformed_or_shared_origins_are_rejected_for_writes(tmp_path, origin):
    store = SQLiteResearchStore(tmp_path / "invalid-origin.sqlite3")
    handler = make_handler(SSSWETEngine(store=store), store)
    local = SimpleNamespace(client_address=("127.0.0.1", 45678))
    assert not handler._public_browser_origin_allowed(local, origin)


def test_private_admin_accepts_ipv6_loopback_host_header(tmp_path):
    store = SQLiteResearchStore(tmp_path / "ipv6-admin.sqlite3")
    handler = make_handler(
        SSSWETEngine(store=store), store, admin_token="test-admin-token"
    )
    ipv6_local = SimpleNamespace(
        client_address=("::1", 45678),
        headers={
            "Host": "[::1]:8765",
            "X-SSSWET-Admin-Token": "test-admin-token",
        },
    )
    assert handler._private_admin_allowed(ipv6_local)

    remote = SimpleNamespace(
        client_address=("203.0.113.10", 45678),
        headers={
            "Host": "[::1]:8765",
            "X-SSSWET-Admin-Token": "test-admin-token",
        },
    )
    assert not handler._private_admin_allowed(remote)

    malformed = SimpleNamespace(
        client_address=("::1", 45678),
        headers={
            "Host": "[::1]:99999",
            "X-SSSWET-Admin-Token": "test-admin-token",
        },
    )
    assert not handler._private_admin_allowed(malformed)

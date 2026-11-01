import json
import threading
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from ssswet_core.priority_assessments import PriorityAssessmentStore
from ssswet_core.priority_framework import CRITERION_KEYS


def scores(value=3):
    return {key: value for key in CRITERION_KEYS}


def test_assessments_are_persisted_as_append_only_history(tmp_path):
    database = tmp_path / "priority.sqlite3"
    store = PriorityAssessmentStore(database)
    first = store.append({
        "programme_id": "clean-water", "scores": scores(4),
        "reviewer_label": "Research team", "rationale": "Initial documented review.",
        "evidence_refs": ["https://example.org/source"],
    })
    partial = scores(2)
    partial["evidence_maturity"] = None
    second = store.append({
        "programme_id": "clean-water", "scores": partial,
        "reviewer_label": "Independent reviewer", "rationale": "Evidence review remains pending.",
    })
    report = PriorityAssessmentStore(database).overview()
    assert report["history_count"] == 2
    assert report["assessed_programmes"] == 1
    assert report["ranked_count"] == 0
    assert report["incomplete"][0]["assessment_id"] == second["assessment_id"]
    assert report["history"][1]["assessment_id"] == first["assessment_id"]


def test_assessment_validation_requires_reason_and_reviewer(tmp_path):
    store = PriorityAssessmentStore(tmp_path / "priority.sqlite3")
    with pytest.raises(ValueError, match="rationale is required"):
        store.append({"programme_id": "x", "scores": scores(), "reviewer_label": "Team"})
    with pytest.raises(ValueError, match="reviewer_label is required"):
        store.append({"programme_id": "x", "scores": scores(), "rationale": "Reason"})


def test_assessment_api_is_readable_and_writes_only_from_loopback(tmp_path):
    from ssswet_core.engine import SSSWETEngine
    from ssswet_core.persistence import SQLiteResearchStore
    from ssswet_core.priority_assessments import PriorityAssessmentStore
    from ssswet_core.server import make_handler

    store = SQLiteResearchStore(tmp_path / "research.sqlite3")
    assessments = PriorityAssessmentStore(store.path)
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), make_handler(SSSWETEngine(store=store), store, priority_assessments=assessments)
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        request = Request(base + "/api/research-priority-assessments", data=json.dumps({
            "programme_id": "clean-water", "scores": scores(),
            "reviewer_label": "Local team", "rationale": "Documented preliminary review.",
        }).encode(), headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(request) as response:
            saved = json.loads(response.read())
            assert response.status == 201
            assert saved["assessment"]["append_only"] is True
        with urlopen(base + "/api/research-priority-assessments") as response:
            report = json.loads(response.read())
        assert report["assessed_programmes"] == 1
        assert report["ranked"][0]["programme_id"] == "clean-water"
        blocked = Request(base + "/api/research-priority-assessments", data=b"{}", headers={
            "Origin": "https://example.org", "Content-Type": "application/json"
        }, method="POST")
        with pytest.raises(HTTPError) as error:
            urlopen(blocked)
        assert error.value.code == 403
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

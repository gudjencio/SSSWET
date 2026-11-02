from __future__ import annotations

import json

import pytest

from ssswet_core import project_reports


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def test_public_report_creates_issue_and_returns_receipt(monkeypatch):
    monkeypatch.setenv("SSSWET_GITHUB_TOKEN", "test-token")
    monkeypatch.setenv("SSSWET_REPORT_REPOSITORY", "gudjencio/SSSWET")
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["payload"] = json.loads(request.data.decode("utf-8"))
        captured["authorization"] = request.get_header("Authorization")
        return FakeResponse({"number": 321, "html_url": "https://github.com/gudjencio/SSSWET/issues/321"})

    monkeypatch.setattr(project_reports, "urlopen", fake_urlopen)
    result = project_reports.create_project_report({
        "category": "accessibility",
        "title": "Voice control visibility",
        "description": "Make the voice toggle easier to find.",
        "language": "en",
        "page": "/",
    })

    assert result == {
        "issue_number": 321,
        "issue_url": "https://github.com/gudjencio/SSSWET/issues/321",
        "submitted": True,
        "changes_applied": False,
    }
    assert captured["payload"]["labels"] == ["public report", "enhancement"]
    assert captured["authorization"] == "Bearer test-token"


def test_public_report_requires_github_intake_token(monkeypatch):
    monkeypatch.delenv("SSSWET_GITHUB_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="not configured"):
        project_reports.create_project_report({
            "category": "bug", "title": "A bug", "description": "A reproducible issue"
        })


def test_public_report_rejects_invalid_category():
    with pytest.raises(ValueError, match="Unsupported"):
        project_reports.create_project_report({
            "category": "unknown", "title": "A bug", "description": "A reproducible issue"
        })

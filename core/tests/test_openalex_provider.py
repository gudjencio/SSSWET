import json

from ssswet_core.providers import OpenAlexProvider


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def test_openalex_returns_traceable_metadata_without_claiming_validation(monkeypatch):
    payload = {"results": [{
        "id": "https://openalex.org/W123",
        "doi": "https://doi.org/10.5555/example",
        "title": "A study of orbital dynamics",
        "publication_year": 2025,
        "cited_by_count": 12,
        "authorships": [{"author": {"display_name": "Ada Lovelace"}}],
        "primary_location": {"source": {"display_name": "Journal of Examples"}},
    }]}
    seen = {}

    def fake_urlopen(request, timeout):
        seen["url"] = request.full_url
        seen["timeout"] = timeout
        return FakeResponse(payload)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    result = OpenAlexProvider(mailto="research@example.org").investigate(
        "orbital dynamics", "literature"
    )

    assert result.source_ids == ("https://doi.org/10.5555/example",)
    assert "A study of orbital dynamics" in result.evidence[0]
    assert "Ada Lovelace" in result.evidence[0]
    assert "Journal of Examples" in result.evidence[0]
    assert "cited-by count: 12" in result.evidence[0]
    assert result.uncertainty == 1.0
    assert "do not establish" in result.summary
    assert "mailto=research%40example.org" in seen["url"]
    assert seen["timeout"] <= 30


def test_openalex_network_failure_does_not_fabricate_records(monkeypatch):
    def failed_urlopen(request, timeout):
        raise TimeoutError("network timeout")

    monkeypatch.setattr("urllib.request.urlopen", failed_urlopen)
    result = OpenAlexProvider().investigate("orbital dynamics", "literature")
    assert result.evidence == ()
    assert result.source_ids == ()
    assert result.uncertainty == 1.0
    assert "unavailable" in result.summary


def test_openalex_empty_query_skips_network(monkeypatch):
    def unexpected_urlopen(request, timeout):
        raise AssertionError("network should not be called")

    monkeypatch.setattr("urllib.request.urlopen", unexpected_urlopen)
    result = OpenAlexProvider().investigate(" ", "literature")
    assert result.evidence == ()
    assert "empty" in result.summary

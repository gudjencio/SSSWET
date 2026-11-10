import json

from ssswet_core.providers import CrossrefProvider


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def test_crossref_provider_returns_traceable_bibliographic_records(monkeypatch):
    payload = {
        "message": {
            "items": [
                {
                    "title": ["A reproducible study of wave propagation"],
                    "DOI": "10.1234/example.1",
                    "URL": "https://doi.org/10.1234/example.1",
                    "publisher": "Example Society",
                    "published-print": {"date-parts": [[2024, 5, 1]]},
                    "author": [{"given": "Ada", "family": "Lovelace"}],
                    "container-title": ["Journal of Reproducible Examples"],
                    "type": "journal-article",
                    "relation": {"is-corrected-by": [{"id-type": "doi", "id": "10.1234/correction"}]},
                }
            ]
        }
    }
    seen = {}

    def fake_urlopen(request, timeout):
        seen["url"] = request.full_url
        seen["agent"] = request.get_header("User-agent")
        seen["timeout"] = timeout
        return FakeResponse(payload)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    result = CrossrefProvider(mailto="research@example.org").investigate(
        "wave propagation reproducibility", "literature"
    )

    assert result.source_ids == ("10.1234/example.1",)
    assert "A reproducible study" in result.evidence[0]
    assert "Ada Lovelace" in result.evidence[0]
    assert "2024" in result.evidence[0]
    assert result.uncertainty == 1.0
    record = result.bibliographic_records[0]
    assert record["doi"] == "10.1234/example.1"
    assert record["venue"] == "Journal of Reproducible Examples"
    assert record["type"] == "journal-article"
    assert record["relation"]["is-corrected-by"][0]["id"] == "10.1234/correction"
    assert record["peer_review_status"] == "not_established_by_crossref_metadata"
    assert "discovery leads only" in result.summary
    assert "mailto=research%40example.org" in seen["url"]
    assert "SSSWET/0.1" in seen["agent"]
    assert seen["timeout"] <= 30


def test_crossref_provider_handles_network_errors_without_fabricating_results(monkeypatch):
    def failed_urlopen(request, timeout):
        raise TimeoutError("network timeout")

    monkeypatch.setattr("urllib.request.urlopen", failed_urlopen)
    result = CrossrefProvider().investigate("quantum materials", "literature")

    assert result.evidence == ()
    assert result.source_ids == ()
    assert result.uncertainty == 1.0
    assert "unavailable" in result.summary


def test_crossref_provider_rejects_empty_query_without_network_call(monkeypatch):
    def unexpected_urlopen(request, timeout):
        raise AssertionError("network should not be called for an empty query")

    monkeypatch.setattr("urllib.request.urlopen", unexpected_urlopen)
    result = CrossrefProvider().investigate("   ", "literature")
    assert result.evidence == ()
    assert "empty" in result.summary

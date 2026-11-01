import json

from ssswet_core.providers import OpenAICompatibleProvider


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def test_llm_provider_sends_prompt_and_returns_unverified_draft(monkeypatch):
    seen = {}

    def fake_urlopen(request, timeout):
        seen["url"] = request.full_url
        seen["authorization"] = request.get_header("Authorization")
        seen["body"] = json.loads(request.data.decode("utf-8"))
        seen["timeout"] = timeout
        return FakeResponse({
            "choices": [{"message": {"content": "Summary: a testable hypothesis.\nLimitations: source review needed."}}]
        })

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    provider = OpenAICompatibleProvider(
        api_key="test-secret",
        model="test-model",
        endpoint="https://example.org/v1/chat/completions",
    )
    result = provider.investigate("Study a harmless physics question", "initial")

    assert "MODEL-GENERATED DRAFT" in result.summary
    assert "testable hypothesis" in result.summary
    assert result.evidence == ()
    assert result.source_ids == ()
    assert result.uncertainty == 1.0
    assert seen["authorization"] == "Bearer test-secret"
    assert seen["body"]["model"] == "test-model"
    assert "Never invent citations" in seen["body"]["messages"][0]["content"]
    assert "warm, approachable, encouraging" in seen["body"]["messages"][0]["content"]
    assert "remain rigorous" in seen["body"]["messages"][0]["content"]
    assert seen["timeout"] <= 90


def test_llm_provider_does_not_leak_api_key_in_error(monkeypatch):
    def failed_urlopen(request, timeout):
        raise TimeoutError("request timed out")

    monkeypatch.setattr("urllib.request.urlopen", failed_urlopen)
    provider = OpenAICompatibleProvider(
        api_key="private-test-key",
        model="test-model",
        endpoint="https://example.org/v1/chat/completions",
    )
    result = provider.investigate("A safe research objective", "initial")

    assert "unavailable" in result.summary
    assert "private-test-key" not in result.summary
    assert result.uncertainty == 1.0


def test_llm_provider_requires_credentials_and_secure_endpoint():
    import pytest

    with pytest.raises(ValueError):
        OpenAICompatibleProvider(api_key="", model="test-model")
    with pytest.raises(ValueError):
        OpenAICompatibleProvider(api_key="secret", model="test-model", endpoint="http://example.org/api")

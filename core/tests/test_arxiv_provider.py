import xml.etree.ElementTree as ET

from ssswet_core.providers import ArxivProvider


ATOM = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>https://arxiv.org/abs/2601.01234v1</id>
    <published>2026-01-15T10:00:00Z</published>
    <title>  A study of quantum spacetime  </title>
    <author><name>Ada Lovelace</name></author>
    <summary>We investigate a hypothetical model and report limitations.</summary>
  </entry>
</feed>
"""


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, size=-1):
        payload = ATOM.encode("utf-8")
        return payload if size < 0 else payload[:size]


def test_arxiv_returns_traceable_preprint_metadata():
    seen = {}

    def fake_urlopen(request, timeout):
        seen["url"] = request.full_url
        seen["timeout"] = timeout
        return FakeResponse()

    result = ArxivProvider(opener=fake_urlopen).investigate("quantum spacetime", "literature")

    assert result.source_ids == ("arxiv:2601.01234",)
    assert "A study of quantum spacetime" in result.evidence[0]
    assert "Ada Lovelace" in result.evidence[0]
    assert "2026" in result.evidence[0]
    assert "arXiv 2601.01234v1" in result.evidence[0]
    assert "URL: https://arxiv.org/abs/2601.01234v1" in result.evidence[0]
    assert "do not establish peer review or scientific validity" in result.summary
    assert result.uncertainty == 1.0
    assert "search_query=all%3Aquantum" in seen["url"]
    assert seen["timeout"] <= 30


def test_arxiv_network_failure_does_not_fabricate_records():
    def failed_urlopen(request, timeout):
        raise TimeoutError("network timeout")

    result = ArxivProvider(opener=failed_urlopen).investigate("quantum spacetime", "literature")

    assert result.evidence == ()
    assert result.source_ids == ()
    assert result.uncertainty == 1.0
    assert "unavailable" in result.summary


def test_arxiv_empty_query_skips_network():
    def unexpected_urlopen(request, timeout):
        raise AssertionError("network should not be called")

    result = ArxivProvider(opener=unexpected_urlopen).investigate(" ", "literature")

    assert result.evidence == ()
    assert "empty" in result.summary

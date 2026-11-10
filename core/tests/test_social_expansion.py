import io
import json
from urllib.parse import parse_qs, urlparse

import pytest

from ssswet_core.social_expansion import (
    BlueskySearchProvider, RedditSearchProvider, ThreadsKeywordSearchProvider,
    FacebookPublicPageProvider, QiitaSearchProvider, PublicRSSFeedProvider,
    DeepLTranslationClient,
)
from ssswet_core.social_research import SocialItem, triage_social_item


def test_bluesky_public_atproto_search_preserves_post_uri_and_language():
    seen = {}
    def fake(url, headers, timeout):
        seen["url"] = url
        return {"posts": [{"post": {
            "uri": "at://did:plc:abc/app.bsky.feed.post/xyz",
            "indexedAt": "2026-11-01T00:00:00Z",
            "author": {"handle": "lab.example"},
            "record": {"text": "研究成果の公開", "langs": ["ja"]},
        }}]}
    item = BlueskySearchProvider(request_json=fake).search("量子材料")[0]
    assert item.platform == "bluesky"
    assert item.url == "https://bsky.app/profile/lab.example/post/xyz"
    assert item.metadata["language"] == "ja"
    assert parse_qs(urlparse(seen["url"]).query)["q"] == ["量子材料"]


def test_reddit_search_requires_oauth_and_keeps_subreddit_provenance():
    seen = {}
    def fake(url, headers, timeout):
        seen.update(headers)
        return {"data": {"children": [{"data": {
            "id": "abc", "title": "Research discussion", "selftext": "Methods and dataset",
            "permalink": "/r/science/comments/abc/", "subreddit": "science",
            "author": "researcher", "created_utc": 1790000000,
        }}]}}
    item = RedditSearchProvider("oauth-token", "SSSWET research/0.3", request_json=fake).search("research")[0]
    assert item.url == "https://www.reddit.com/r/science/comments/abc/"
    assert item.metadata["subreddit"] == "science"
    assert seen["Authorization"] == "Bearer oauth-token"


def test_threads_search_marks_meta_permission_scope_and_keeps_original_link():
    def fake(url, headers, timeout):
        return {"data": [{"id": "t1", "text": "New materials paper", 
                          "permalink": "https://www.threads.net/@lab/post/t1",
                          "timestamp": "2026-11-01T00:00:00Z", "username": "lab"}]}
    item = ThreadsKeywordSearchProvider("token", request_json=fake).search("materials")[0]
    assert item.source_id == "threads:t1"
    assert item.metadata["api_scope_required"] == "threads_keyword_search"


def test_facebook_adapter_is_limited_to_explicit_page_ids():
    calls = []
    def fake(url, headers, timeout):
        calls.append(url)
        return {"data": [{"id": "123_456", "message": "public research update",
                          "created_time": "2026-11-01T00:00:00Z",
                          "permalink_url": "https://www.facebook.com/123/posts/456",
                          "from": {"name": "Public Science Page"}}]}
    provider = FacebookPublicPageProvider("token", ["123", "bad;id"], request_json=fake)
    item = provider.search("research")[0]
    assert len(calls) == 1
    assert item.platform == "facebook"
    assert item.metadata["access_scope"] == "configured_public_page"


def test_qiita_api_parses_japanese_technical_articles(monkeypatch):
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self, size):
            return json.dumps([{"id": "q1", "title": "量子材料の研究", "url": "https://qiita.com/lab/items/q1",
                                "body": "実験データと方法", "created_at": "2026-11-01T00:00:00Z",
                                "user": {"id": "lab"}, "tags": [{"name": "science"}]}]).encode()
    monkeypatch.setattr("ssswet_core.social_expansion.urlopen", lambda *a, **k: Response())
    item = QiitaSearchProvider().search("量子材料")[0]
    assert item.platform == "qiita"
    assert item.metadata["language"] == "ja"
    assert item.title == "量子材料の研究"


def test_public_feed_rejects_non_https_and_private_networks(monkeypatch):
    with pytest.raises(ValueError):
        PublicRSSFeedProvider(["http://example.org/feed"])._validate_url("http://example.org/feed")
    monkeypatch.setattr("ssswet_core.social_expansion.socket.getaddrinfo",
                        lambda *a, **k: [(None, None, None, None, ("127.0.0.1", 443))])
    with pytest.raises(ValueError):
        PublicRSSFeedProvider([])._validate_url("https://internal.example/feed")


def test_deepl_translation_preserves_original_and_marks_translation_unverified(monkeypatch):
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self, size):
            return json.dumps({"translations": [{"text": "Published research findings", 
                                                "detected_source_language": "JA"}]}).encode()
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **k: Response())
    item = SocialItem("qiita", "qiita:q", "研究成果", "実験結果", "https://qiita.com/lab/items/q",
                      metadata={"language": "ja"})
    translated = DeepLTranslationClient("test-key").translate_item(item)
    assert translated.title == item.title and translated.text == item.text
    assert translated.metadata["translation"]["text"] == "Published research findings"
    assert translated.metadata["translation"]["original_preserved"] is True
    assert translated.metadata["translation"]["translation_is_not_fact_verification"] is True


@pytest.mark.parametrize("phrase,expected", [
    ("Increíble cura milagrosa, riesgo cero", "clickbait_language_es"),
    ("Não querem que você saiba: cura milagrosa", "clickbait_language_pt"),
    ("Wundermittel ohne Risiko", "clickbait_language_de"),
    ("علاج سحري بدون مخاطر", "clickbait_language_ar"),
    ("चमत्कारी इलाज", "clickbait_language_hi"),
    ("奇跡の治療、リスクゼロ", "clickbait_language_ja"),
    ("神奇疗法，零风险", "clickbait_language_zh"),
    ("기적의 치료, 위험 제로", "clickbait_language_ko"),
    ("шокирующий прорыв", "clickbait_language_ru"),
    ("mucize tedavi, sıfır risk", "clickbait_language_tr"),
])
def test_multilingual_clickbait_flags_never_assign_truth(phrase, expected):
    item = SocialItem("forum-test", "source:1", phrase, phrase, "https://example.org/post")
    result = triage_social_item(item)
    assert expected in result.flags
    assert result.verification_status == "not_verified"
    assert result.status == "manual_review_required"

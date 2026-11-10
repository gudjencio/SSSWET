import json
from urllib.parse import parse_qs, urlparse

import pytest

from ssswet_core.social_research import (
    InstagramBusinessDiscoveryProvider, SocialItem, SocialResearchProvider,
    XRecentSearchProvider, YouTubeDataAPIProvider, build_claim_review_packet,
    triage_social_item,
)


def test_youtube_adapter_uses_official_search_and_retains_video_provenance():
    calls = []
    def fake(url, headers, timeout):
        calls.append(url)
        return {"items": [{"id": {"videoId": "abc123"}, "snippet": {
            "title": "A physics lecture", "description": "Methods and data: https://example.org/paper",
            "channelTitle": "University", "channelId": "UC1", "publishedAt": "2026-01-01T00:00:00Z",
        }}]}
    items = YouTubeDataAPIProvider("secret", request_json=fake).search("physics lecture")
    assert len(items) == 1 and items[0].source_id == "youtube:abc123"
    assert items[0].url == "https://www.youtube.com/watch?v=abc123"
    assert items[0].metadata["transcript_retrieved"] is False
    assert parse_qs(urlparse(calls[0]).query)["safeSearch"] == ["strict"]


def test_youtube_adapter_requires_key_and_caps_results():
    with pytest.raises(ValueError):
        YouTubeDataAPIProvider("")
    assert YouTubeDataAPIProvider("key", max_results=999).max_results == 10


def test_x_adapter_uses_official_api_and_preserves_post_metadata():
    seen = {}
    def fake(url, headers, timeout):
        seen["url"], seen["headers"] = url, headers
        return {"data": [{"id": "77", "text": "A testable science claim", "author_id": "u1",
                          "created_at": "2026-02-01T00:00:00Z", "lang": "en",
                          "public_metrics": {"like_count": 900}}],
                "includes": {"users": [{"id": "u1", "username": "lab_account", "verified": True}]}}
    item = XRecentSearchProvider("bearer", request_json=fake).search("science claim")[0]
    assert item.source_id == "x:77" and item.url == "https://x.com/lab_account/status/77"
    assert item.metadata["public_metrics"]["like_count"] == 900
    assert item.metadata["engagement_is_not_evidence"] is True
    assert seen["headers"]["Authorization"] == "Bearer bearer"


def test_instagram_adapter_is_scoped_to_configured_handles_and_official_graph_api():
    calls = []
    def fake(url, headers, timeout):
        calls.append(url)
        return {"business_discovery": {"username": "science_lab", "media": {"data": [{
            "id": "m1", "caption": "New materials science experiment", "media_type": "VIDEO",
            "permalink": "https://www.instagram.com/p/abc/", "timestamp": "2026-02-01T00:00:00Z",
        }]}}}
    provider = InstagramBusinessDiscoveryProvider("token", "123", ["@science_lab", "bad handle", "another_lab"], request_json=fake)
    items = provider.search("materials science")
    assert [item.source_id for item in items] == ["instagram:m1"]
    assert items[0].metadata["account_scope"] == "configured_public_professional_account"
    assert "science_lab" in calls[0]


def test_instagram_does_not_return_unrelated_posts():
    provider = InstagramBusinessDiscoveryProvider("token", "123", ["science_lab"], request_json=lambda *a: {
        "business_discovery": {"media": {"data": [{
            "id": "m2", "caption": "Cooking today", "permalink": "https://www.instagram.com/p/xyz/"
        }]}}})
    assert provider.search("quantum physics") == []


def test_instagram_account_allowlist_is_validated_and_bounded():
    provider = InstagramBusinessDiscoveryProvider("token", "123", ["ok_name", "bad name", "@another", *[f"user{i}" for i in range(20)]])
    assert "bad name" not in provider.usernames and len(provider.usernames) <= 10


def test_social_provider_deduplicates_and_bounds_results():
    class Fake:
        name = "fake"
        def search(self, query):
            return [
                SocialItem("youtube", "youtube:1", "A", "text", "https://www.youtube.com/watch?v=1"),
                SocialItem("youtube", "youtube:1", "A duplicate", "text", "https://www.youtube.com/watch?v=1"),
            ]
    items, errors = SocialResearchProvider([Fake()], max_results=1).search("science")
    assert len(items) == 1 and errors == ()


def test_social_provider_enables_public_no_key_sources_without_live_network_in_tests(monkeypatch):
    from ssswet_core.social_expansion import BlueskySearchProvider, QiitaSearchProvider
    for key in ("SSSWET_YOUTUBE_API_KEY", "SSSWET_X_BEARER_TOKEN", "SSSWET_INSTAGRAM_ACCESS_TOKEN",
                "SSSWET_INSTAGRAM_USER_ID", "SSSWET_INSTAGRAM_BUSINESS_ACCOUNTS",
                "SSSWET_REDDIT_ACCESS_TOKEN", "SSSWET_THREADS_ACCESS_TOKEN",
                "SSSWET_FACEBOOK_ACCESS_TOKEN", "SSSWET_FACEBOOK_PAGE_IDS", "SSSWET_PUBLIC_FEEDS"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setattr(BlueskySearchProvider, "search", lambda self, query: [])
    monkeypatch.setattr(QiitaSearchProvider, "search", lambda self, query: [])
    provider = SocialResearchProvider.from_environment()
    assert {source.name for source in provider.providers} >= {"bluesky-atproto", "qiita-api-v2"}
    items, errors = provider.search("materials science")
    assert items == [] and errors == ()

def test_social_provider_contains_provider_failure_without_losing_other_results():
    class Broken:
        name = "broken"
        def search(self, query):
            raise RuntimeError("upstream unavailable")
    class Healthy:
        name = "healthy"
        def search(self, query):
            return [SocialItem("x", "x:1", "science", "data", "https://x.com/a/status/1")]
    items, errors = SocialResearchProvider([Broken(), Healthy()]).search("science")
    assert [item.source_id for item in items] == ["x:1"]
    assert errors and "broken: RuntimeError" in errors[0]


def test_clickbait_and_absolute_claims_are_flagged_not_declared_false():
    item = SocialItem("youtube", "youtube:2", "Shocking miracle cure, 100% guaranteed",
                      "Scientists confirm this instant breakthrough", "https://www.youtube.com/watch?v=2")
    triage = triage_social_item(item)
    assert triage.status == "manual_review_required"
    assert "sensational_language" in triage.flags
    assert "extraordinary_absolute_claim" in triage.flags
    assert triage.verification_status == "not_verified"


def test_source_free_post_is_flagged():
    item = SocialItem("x", "x:2", "A claim", "Trust me", "https://x.com/a/status/2")
    assert "no_source_reference_in_post" in triage_social_item(item).flags


def test_metrics_and_verified_badge_never_remove_review_flags():
    item = SocialItem("x", "x:3", "Miracle cure", "100% guaranteed", "https://x.com/a/status/3",
                      author="@verified", metadata={"public_metrics": {"like_count": 1000000},
                      "author_verified_badge": True})
    triage = triage_social_item(item)
    assert "extraordinary_absolute_claim" in triage.flags
    assert triage.status == "manual_review_required"


def test_claim_packet_marks_cross_platform_recurrence_as_not_confirmation():
    items = [
        SocialItem("youtube", "youtube:a", "Quantum claim", "Quantum claim explained", "https://www.youtube.com/watch?v=a"),
        SocialItem("x", "x:b", "Quantum claim", "Quantum claim is real", "https://x.com/a/status/b"),
    ]
    packet = build_claim_review_packet("Quantum claim", items)
    assert packet["cross_platform_recurrence"] is True
    assert packet["cross_platform_recurrence_is_not_confirmation"] is True
    assert packet["status"] == "unverified_requires_human_review"


def test_claim_packet_is_bounded_and_rejects_empty_claim():
    with pytest.raises(ValueError):
        build_claim_review_packet(" ", [])
    items = (SocialItem("x", f"x:{i}", "science", "science", f"https://x.com/a/status/{i}") for i in range(30))
    assert build_claim_review_packet("science", items, limit=5)["matching_source_count"] == 5


def test_social_investigate_returns_machine_readable_provenance():
    class Fake:
        name = "fake"
        def search(self, query):
            return [SocialItem("youtube", "youtube:42", "Physics", "description", "https://www.youtube.com/watch?v=42")]
    result = SocialResearchProvider([Fake()]).investigate("physics", "initial")
    record = json.loads(result.evidence[0])
    assert record["source_id"] == "youtube:42"
    assert record["automated_triage"]["verification_status"] == "not_verified"
    assert result.source_ids == ("youtube:42",) and result.uncertainty == 1.0


def test_social_item_rejects_non_https_and_unknown_platforms():
    with pytest.raises(ValueError):
        SocialItem("x", "x:1", "title", "text", "http://x.com/a")
    with pytest.raises(ValueError):
        SocialItem("Bad Platform", "bad:1", "title", "text", "https://example.org")



def test_combined_provider_keeps_scholarly_results_when_social_is_unconfigured():
    from ssswet_core.providers import ProviderResult
    from ssswet_core.social_research import MultiSourceResearchProvider

    class Literature:
        name = "literature"
        def investigate(self, objective, strategy):
            return ProviderResult("Scholarly leads", ("paper metadata",), 1.0, ("doi:10.1000/x",))

    class Social:
        name = "social"
        def investigate(self, objective, strategy):
            return ProviderResult("No social credentials", (), 1.0, ())

    result = MultiSourceResearchProvider(Literature(), Social()).investigate("science", "initial")
    assert result.source_ids == ("doi:10.1000/x",)
    assert result.evidence == ("paper metadata",)
    assert "No social credentials" in result.summary


def test_combined_provider_deduplicates_sources_and_survives_provider_errors():
    from ssswet_core.providers import ProviderResult
    from ssswet_core.social_research import MultiSourceResearchProvider

    class Literature:
        name = "literature"
        def investigate(self, objective, strategy):
            return ProviderResult("Paper", ("paper",), 0.8, ("shared-source",))

    class Social:
        name = "social"
        def investigate(self, objective, strategy):
            return ProviderResult("Social", ("duplicate", "post"), 1.0, ("shared-source", "x:123"))

    result = MultiSourceResearchProvider(Literature(), Social()).investigate("science", "initial")
    assert result.source_ids == ("shared-source", "x:123")
    assert result.evidence == ("paper", "post")
    assert result.uncertainty == 1.0



def test_french_clickbait_phrases_are_flagged_without_truth_classification():
    item = SocialItem("x", "x:fr", "Remède miracle, zéro risque",
                      "La science prouve une percée révolutionnaire",
                      "https://x.com/lab/status/fr")
    triage = triage_social_item(item)
    assert triage.status == "manual_review_required"
    assert "extraordinary_absolute_claim" in triage.flags
    assert "unsupported_certainty_language" in triage.flags
    assert "breakthrough_or_speed_claim" in triage.flags
    assert triage.verification_status == "not_verified"

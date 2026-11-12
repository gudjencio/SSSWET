"""Additional public-community adapters and optional source-preserving translation.

All adapters use documented/public endpoints or operator-configured public feeds.
They never scrape logged-in pages or access private communities.
"""
from __future__ import annotations

from dataclasses import replace
from email.utils import parsedate_to_datetime
import ipaddress
import hashlib
import json
import os
import re
import socket
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler, urlopen
import xml.etree.ElementTree as ET

from .social_research import SocialItem, _fetch_json, MAX_RESPONSE_BYTES, DEFAULT_TIMEOUT


def _lang_from_text(value: str) -> str:
    """Conservative script-based language hint; never presented as certain."""
    sample = value[:1500]
    if any("\u3040" <= c <= "\u30ff" for c in sample):
        return "ja"
    if any("\uac00" <= c <= "\ud7af" for c in sample):
        return "ko"
    if any("\u4e00" <= c <= "\u9fff" for c in sample):
        return "zh"
    if any("\u0600" <= c <= "\u06ff" for c in sample):
        return "ar"
    if any("\u0400" <= c <= "\u04ff" for c in sample):
        return "ru"
    if any("\u0900" <= c <= "\u097f" for c in sample):
        return "hi"
    return ""



class BraveWebSearchProvider:
    """Search the public web index for community/forum material across domains."""
    name = "brave-web-search"
    endpoint = "https://api.search.brave.com/res/v1/web/search"

    def __init__(self, subscription_token: str, max_results=10, request_json=_fetch_json):
        if not subscription_token.strip():
            raise ValueError("A Brave Search API subscription token is required.")
        self.token = subscription_token.strip()
        self.max_results = max(1, min(int(max_results), 20))
        self.request_json = request_json

    def search(self, query: str) -> list[SocialItem]:
        if not query.strip():
            return []
        url = self.endpoint + "?" + urlencode({"q": query[:300], "count": self.max_results, "safesearch": "moderate"})
        payload = self.request_json(url, {"X-Subscription-Token": self.token}, DEFAULT_TIMEOUT)
        results = (payload.get("web") or {}).get("results", [])
        output = []
        for row in results[:self.max_results]:
            title, link = str(row.get("title") or ""), str(row.get("url") or "")
            if not title or not link.startswith("https://"):
                continue
            description = str(row.get("description") or "")
            source_id = hashlib.sha256(link.encode("utf-8")).hexdigest()[:24]
            output.append(SocialItem(
                platform="web-search", source_id="web-search:" + source_id,
                title=title[:500], text=description[:5000], url=link[:1500],
                author=str((row.get("profile") or {}).get("long_name") or "")[:150],
                published_at=str(row.get("page_age") or "")[:40],
                content_type="indexed_public_web_page",
                metadata={"search_provider": "Brave Search API",
                          "domain": str(urlparse(link).hostname or "")[:200],
                          "language": _lang_from_text(title + " " + description),
                          "search_snippet_is_not_primary_evidence": True},
            ))
        return output


class BlueskySearchProvider:
    name = "bluesky-atproto"
    endpoint = "https://api.bsky.app/xrpc/app.bsky.feed.searchPosts"

    def __init__(self, max_results=10, request_json=_fetch_json):
        self.max_results = max(1, min(int(max_results), 25))
        self.request_json = request_json

    def search(self, query: str) -> list[SocialItem]:
        if not query.strip():
            return []
        url = self.endpoint + "?" + urlencode({"q": query[:300], "limit": self.max_results, "sort": "latest"})
        payload = self.request_json(url, {}, DEFAULT_TIMEOUT)
        output = []
        for row in payload.get("posts", [])[:self.max_results]:
            post = row.get("post") or {}
            record = post.get("record") or {}
            author = post.get("author") or {}
            uri = str(post.get("uri") or "")
            rkey = uri.rsplit("/", 1)[-1]
            handle = str(author.get("handle") or "")
            text = str(record.get("text") or "")
            if not rkey or not handle or not text:
                continue
            langs = record.get("langs") or []
            lang = str(langs[0]) if langs else _lang_from_text(text)
            output.append(SocialItem(
                platform="bluesky", source_id="bluesky:" + uri,
                title=text[:180], text=text[:5000],
                url=f"https://bsky.app/profile/{handle}/post/{rkey}",
                author="@" + handle,
                published_at=str(post.get("indexedAt") or "")[:40],
                content_type="public_post",
                metadata={"language": lang, "protocol": "AT Protocol",
                          "engagement_is_not_evidence": True},
            ))
        return output


class RedditSearchProvider:
    name = "reddit-oauth-search"
    endpoint = "https://oauth.reddit.com/search"

    def __init__(self, access_token: str, user_agent: str, max_results=10, request_json=_fetch_json):
        if not access_token.strip():
            raise ValueError("A Reddit OAuth access token is required.")
        if not user_agent.strip() or len(user_agent) > 200:
            raise ValueError("A descriptive Reddit API user agent is required.")
        self.token, self.user_agent = access_token.strip(), user_agent.strip()
        self.max_results = max(1, min(int(max_results), 25))
        self.request_json = request_json

    def search(self, query: str) -> list[SocialItem]:
        if not query.strip():
            return []
        url = self.endpoint + "?" + urlencode({
            "q": query[:300], "sort": "relevance", "limit": self.max_results,
            "type": "link", "restrict_sr": "false",
        })
        payload = self.request_json(url, {
            "Authorization": "Bearer " + self.token,
            "User-Agent": self.user_agent,
        }, DEFAULT_TIMEOUT)
        output = []
        for child in (payload.get("data") or {}).get("children", [])[:self.max_results]:
            row = child.get("data") or {}
            ident, permalink = str(row.get("id") or ""), str(row.get("permalink") or "")
            title = str(row.get("title") or "")
            if not ident or not title or not permalink.startswith("/"):
                continue
            text = str(row.get("selftext") or row.get("title") or "")
            output.append(SocialItem(
                platform="reddit", source_id="reddit:" + ident,
                title=title[:500], text=text[:5000],
                url="https://www.reddit.com" + permalink,
                author=str(row.get("author") or "")[:120],
                published_at=str(row.get("created_utc") or "")[:40],
                content_type="community_post",
                metadata={"subreddit": str(row.get("subreddit") or "")[:100],
                          "language": _lang_from_text(title + " " + text),
                          "score_is_not_evidence": True},
            ))
        return output


class ThreadsKeywordSearchProvider:
    """Meta Threads public keyword search; public discovery requires approved scope."""
    name = "threads-keyword-search"
    endpoint = "https://graph.threads.net/v1.0/keyword_search"

    def __init__(self, access_token: str, max_results=10, request_json=_fetch_json):
        if not access_token.strip():
            raise ValueError("A Threads access token is required.")
        self.token = access_token.strip()
        self.max_results = max(1, min(int(max_results), 25))
        self.request_json = request_json

    def search(self, query: str) -> list[SocialItem]:
        if not query.strip():
            return []
        url = self.endpoint + "?" + urlencode({
            "q": query[:300], "search_type": "RECENT",
            "fields": "id,text,permalink,timestamp,username,media_type",
            "limit": self.max_results,
        })
        payload = self.request_json(url, {"Authorization": "Bearer " + self.token}, DEFAULT_TIMEOUT)
        output = []
        for row in payload.get("data", [])[:self.max_results]:
            ident, text = str(row.get("id") or ""), str(row.get("text") or "")
            permalink = str(row.get("permalink") or "")
            if not ident or not text or not permalink.startswith("https://www.threads.net/"):
                continue
            output.append(SocialItem(
                platform="threads", source_id="threads:" + ident,
                title=text[:180], text=text[:5000], url=permalink,
                author=str(row.get("username") or "")[:120],
                published_at=str(row.get("timestamp") or "")[:40],
                content_type=str(row.get("media_type") or "post").lower(),
                metadata={"language": _lang_from_text(text),
                          "api_scope_required": "threads_keyword_search",
                          "verification_status": "not_verified"},
            ))
        return output


class FacebookPublicPageProvider:
    """Limited public Facebook Page posts from explicitly configured Page IDs."""
    name = "facebook-public-page-posts"
    endpoint = "https://graph.facebook.com/v22.0"

    def __init__(self, access_token: str, page_ids, max_results_per_page=5, request_json=_fetch_json):
        if not access_token.strip():
            raise ValueError("A Facebook Graph API access token is required.")
        self.token = access_token.strip()
        self.page_ids = tuple(dict.fromkeys(
            x.strip() for x in page_ids if re.fullmatch(r"[0-9]{3,40}", x.strip())
        ))[:10]
        self.max_results = max(1, min(int(max_results_per_page), 10))
        self.request_json = request_json

    def search(self, query: str) -> list[SocialItem]:
        terms = {x.casefold() for x in re.findall(r"[\w-]{3,}", query)}
        output = {}
        for page_id in self.page_ids:
            url = self.endpoint + "/" + page_id + "/posts?" + urlencode({
                "fields": "id,message,created_time,permalink_url,from",
                "limit": self.max_results,
            })
            payload = self.request_json(url, {"Authorization": "Bearer " + self.token}, DEFAULT_TIMEOUT)
            for row in payload.get("data", [])[:self.max_results]:
                ident, message = str(row.get("id") or ""), str(row.get("message") or "")
                link = str(row.get("permalink_url") or "")
                if not ident or not link.startswith("https://www.facebook.com/"):
                    continue
                if terms and not any(term in message.casefold() for term in terms):
                    continue
                output.setdefault(ident, SocialItem(
                    platform="facebook", source_id="facebook:" + ident,
                    title=message[:180] or "Public Facebook Page post",
                    text=message[:5000], url=link,
                    author=str((row.get("from") or {}).get("name") or page_id)[:150],
                    published_at=str(row.get("created_time") or "")[:40],
                    content_type="public_page_post",
                    metadata={"access_scope": "configured_public_page",
                              "api_permission_may_be_required": "Page Public Content Access",
                              "language": _lang_from_text(message)},
                ))
        return list(output.values())


class QiitaSearchProvider:
    """Japanese technical/scientific community posts via the official Qiita API."""
    name = "qiita-api-v2"
    endpoint = "https://qiita.com/api/v2/items"

    def __init__(self, access_token="", max_results=10, request_json=_fetch_json):
        self.token = access_token.strip()
        self.max_results = max(1, min(int(max_results), 20))
        self.request_json = request_json

    def search(self, query: str) -> list[SocialItem]:
        if not query.strip():
            return []
        url = self.endpoint + "?" + urlencode({"query": query[:200], "per_page": self.max_results})
        headers = {"Authorization": "Bearer " + self.token} if self.token else {}
        request = Request(url, headers={"Accept": "application/json", **headers,
                                        "User-Agent": "SSSWET/0.3 Qiita API client"})
        with urlopen(request, timeout=DEFAULT_TIMEOUT) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
        if len(raw) > MAX_RESPONSE_BYTES:
            raise ValueError("Qiita response exceeds the configured size limit.")
        payload = json.loads(raw.decode("utf-8"))
        output = []
        for row in payload[:self.max_results] if isinstance(payload, list) else []:
            ident, title, link = str(row.get("id") or ""), str(row.get("title") or ""), str(row.get("url") or "")
            if not ident or not title or not link.startswith("https://qiita.com/"):
                continue
            user = row.get("user") or {}
            body = str(row.get("body") or "")
            output.append(SocialItem(
                platform="qiita", source_id="qiita:" + ident,
                title=title[:500], text=body[:5000], url=link,
                author=str(user.get("name") or user.get("id") or "")[:150],
                published_at=str(row.get("created_at") or "")[:40],
                content_type="technical_article",
                metadata={"language": "ja", "tags": [str(t.get("name") or "") for t in row.get("tags", [])[:12]]},
            ))
        return output


class PublicRSSFeedProvider:
    """Operator-configured public RSS/Atom feeds for forums and regional platforms.

    Feed URLs must be HTTPS and resolve only to globally routable addresses.
    Redirects are disabled; configure the final canonical feed URL directly.
    """
    name = "configured-public-rss-feeds"

    def __init__(self, feed_urls, max_results_per_feed=5, timeout=DEFAULT_TIMEOUT):
        self.feed_urls = tuple(dict.fromkeys(str(x).strip() for x in feed_urls if str(x).strip()))[:20]
        self.max_results = max(1, min(int(max_results_per_feed), 10))
        self.timeout = max(2.0, min(float(timeout), 15.0))

    @staticmethod
    def _validate_url(url):
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("Feed URLs must be credential-free HTTPS URLs.")
        if parsed.port not in (None, 443):
            raise ValueError("Non-standard feed ports are not permitted.")
        addresses = socket.getaddrinfo(parsed.hostname, 443, type=socket.SOCK_STREAM)
        if not addresses:
            raise ValueError("Feed host did not resolve.")
        for result in addresses:
            ip = ipaddress.ip_address(result[4][0])
            if not ip.is_global:
                raise ValueError("Feed host resolves to a non-public address.")
        return parsed.hostname.lower()

    def _read(self, url):
        host = self._validate_url(url)
        class NoRedirect(HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                raise ValueError("Feed redirects are disabled; configure the final HTTPS feed URL.")
        opener = build_opener(NoRedirect)
        request = Request(url, headers={"Accept": "application/atom+xml, application/rss+xml, application/xml, text/xml",
                                        "User-Agent": "SSSWET/0.3 public-feed-reader"})
        with opener.open(request, timeout=self.timeout) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
        if len(raw) > MAX_RESPONSE_BYTES:
            raise ValueError("Feed exceeds the configured response-size limit.")
        root = ET.fromstring(raw)
        entries = []
        for node in root.iter():
            if node.tag.rsplit("}", 1)[-1] in {"item", "entry"}:
                entries.append(node)
        output = []
        base_host = host[4:] if host.startswith("www.") else host
        known_platforms = {
            "mewe.com": "mewe", "snapchat.com": "snapchat", "bilibili.com": "bilibili",
            "nicovideo.jp": "niconico", "qiita.com": "qiita", "zenn.dev": "zenn",
            "note.com": "note", "weibo.com": "weibo", "zhihu.com": "zhihu",
        }
        platform = known_platforms.get(base_host, "forum-" + re.sub(r"[^a-z0-9-]", "-", base_host.split(".")[0])[:24])
        for entry in entries[:self.max_results]:
            fields = {}
            for node in entry.iter():
                key = node.tag.rsplit("}", 1)[-1]
                if key == "link":
                    fields.setdefault("link", node.attrib.get("href") or (node.text or ""))
                elif key in {"title", "description", "summary", "content", "pubDate", "published", "updated", "id", "guid", "author", "name"}:
                    fields.setdefault(key, "".join(node.itertext()).strip())
            title = fields.get("title", "")[:500]
            link = fields.get("link", "")
            if not title or not link.startswith("https://"):
                continue
            body = (fields.get("summary") or fields.get("description") or fields.get("content") or "")[:5000]
            ident = fields.get("id") or fields.get("guid") or link
            output.append(SocialItem(
                platform=platform, source_id=platform + ":" + ident[:180],
                title=title, text=body, url=link[:1500],
                author=(fields.get("author") or fields.get("name") or "")[:150],
                published_at=(fields.get("published") or fields.get("updated") or fields.get("pubDate") or "")[:40],
                content_type="public_feed_entry",
                metadata={"feed_host": host, "language": _lang_from_text(title + " " + body),
                          "feed_is_discovery_not_peer_review": True},
            ))
        return output

    def search(self, query: str) -> list[SocialItem]:
        if not query.strip():
            return []
        output = []
        terms = [x.casefold() for x in re.findall(r"[\w-]{3,}", query)]
        for url in self.feed_urls:
            try:
                for item in self._read(url):
                    text = (item.title + " " + item.text).casefold()
                    if not terms or any(term in text for term in terms):
                        output.append(item)
            except Exception:
                # One unavailable feed must not block other configured sources.
                continue
        return output[:self.max_results * max(1, len(self.feed_urls))]


class DeepLTranslationClient:
    """Optional translation that stores the original and translation side by side."""
    endpoint = "https://api-free.deepl.com/v2/translate"

    def __init__(self, auth_key: str, target_lang="EN", endpoint=None):
        if not auth_key.strip():
            raise ValueError("DeepL API key is required.")
        self.auth_key = auth_key.strip()
        self.target_lang = re.sub(r"[^A-Za-z-]", "", target_lang.upper())[:8] or "EN"
        self.endpoint = endpoint or self.endpoint
        if self.endpoint not in {"https://api-free.deepl.com/v2/translate", "https://api.deepl.com/v2/translate"}:
            raise ValueError("Only the official DeepL API endpoints are permitted.")

    def translate_item(self, item: SocialItem) -> SocialItem:
        text = (item.title + "\n" + item.text).strip()
        if not text or str(item.metadata.get("language") or "").lower() in {"en", "en-us", "en-gb"}:
            return item
        from urllib.parse import urlencode
        body = urlencode({"text": text[:4500], "target_lang": self.target_lang}).encode()
        request = Request(self.endpoint, data=body, method="POST", headers={
            "Authorization": "DeepL-Auth-Key " + self.auth_key,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "User-Agent": "SSSWET/0.3 research translation",
        })
        from urllib.request import urlopen
        with urlopen(request, timeout=12) as response:
            raw = response.read(200_001)
        if len(raw) > 200_000:
            raise ValueError("Translation response exceeds limit.")
        payload = json.loads(raw.decode("utf-8"))
        translations = payload.get("translations") or []
        if not translations:
            return item
        translated = str(translations[0].get("text") or "")[:5000]
        if not translated:
            return item
        metadata = dict(item.metadata)
        metadata["translation"] = {
            "provider": "DeepL API", "target_language": self.target_lang,
            "detected_source_language": str(translations[0].get("detected_source_language") or ""),
            "text": translated,
            "original_preserved": True,
            "translation_is_not_fact_verification": True,
        }
        return replace(item, metadata=metadata)


def configured_expansion_providers(max_results=10):
    """Build only adapters for which explicit credentials/configuration exist."""
    providers = [BlueskySearchProvider(max_results=max_results)]
    brave_key = os.getenv("SSSWET_BRAVE_SEARCH_API_KEY", "").strip()
    if brave_key:
        providers.append(BraveWebSearchProvider(brave_key, max_results=max_results))
    reddit_token = os.getenv("SSSWET_REDDIT_ACCESS_TOKEN", "").strip()
    if reddit_token:
        providers.append(RedditSearchProvider(
            reddit_token, os.getenv("SSSWET_REDDIT_USER_AGENT", "SSSWET research/0.3"),
            max_results=max_results,
        ))
    threads_token = os.getenv("SSSWET_THREADS_ACCESS_TOKEN", "").strip()
    if threads_token:
        providers.append(ThreadsKeywordSearchProvider(threads_token, max_results=max_results))
    facebook_token = os.getenv("SSSWET_FACEBOOK_ACCESS_TOKEN", "").strip()
    page_ids = os.getenv("SSSWET_FACEBOOK_PAGE_IDS", "").split(",")
    if facebook_token and any(page_ids):
        providers.append(FacebookPublicPageProvider(facebook_token, page_ids))
    providers.append(QiitaSearchProvider(os.getenv("SSSWET_QIITA_ACCESS_TOKEN", ""), max_results=max_results))
    feeds = os.getenv("SSSWET_PUBLIC_FEEDS", "").splitlines()
    if feeds:
        providers.append(PublicRSSFeedProvider(feeds, max_results_per_feed=max_results))
    return providers


def translate_items_if_configured(items):
    key = os.getenv("SSSWET_DEEPL_AUTH_KEY", "").strip()
    if not key:
        return items
    translator = DeepLTranslationClient(
        key, os.getenv("SSSWET_TRANSLATION_TARGET_LANG", "EN"),
        os.getenv("SSSWET_DEEPL_API_URL", "https://api-free.deepl.com/v2/translate"),
    )
    output = []
    for item in items:
        try:
            output.append(translator.translate_item(item))
        except Exception:
            metadata = dict(item.metadata)
            metadata["translation"] = {"status": "unavailable", "original_preserved": True}
            output.append(replace(item, metadata=metadata))
    return output

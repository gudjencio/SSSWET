"""Official-API social/video discovery with conservative evidence triage.

Social posts and videos are discovery leads, never verified scientific evidence.
No scraping, login automation, transcript circumvention, or private-content access.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from itertools import islice
import json
import os
import re
from typing import Callable, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .providers import ProviderResult

MAX_RESULTS = 10
MAX_RESPONSE_BYTES = 2_000_000
DEFAULT_TIMEOUT = 12.0
USER_AGENT = "SSSWET/0.2 (official-API research discovery)"


@dataclass(frozen=True)
class SocialItem:
    """Normalized public content metadata. Engagement is context, not evidence."""
    platform: str
    source_id: str
    title: str
    text: str
    url: str
    author: str = ""
    published_at: str = ""
    content_type: str = "post"
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.platform not in {"youtube", "x", "instagram"}:
            raise ValueError("Unsupported social platform.")
        if not self.source_id.strip() or not self.url.startswith("https://"):
            raise ValueError("Social items require a stable source ID and HTTPS URL.")
        if len(self.title) > 500 or len(self.text) > 5000:
            raise ValueError("Social item text exceeds the retention limit.")
        if len(self.metadata) > 30:
            raise ValueError("Social item metadata exceeds the field limit.")

    def as_record(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class SocialTriage:
    source_id: str
    status: str
    flags: tuple[str, ...]
    verification_status: str = "not_verified"
    note: str = (
        "Automated triage identifies review needs; it cannot determine whether a claim is true or false."
    )


_CLICKBAIT = (
    (re.compile(r"\b(shocking|unbelievable|they don't want you to know|secret they hide)\b", re.I), "sensational_language"),
    (re.compile(r"\b(miracle cure|cures? (all|every)|100% guaranteed|zero risk)\b", re.I), "extraordinary_absolute_claim"),
    (re.compile(r"\b(proven|scientists confirm|science proves)\b", re.I), "unsupported_certainty_language"),
    (re.compile(r"\b(instant|overnight|revolutionary breakthrough)\b", re.I), "breakthrough_or_speed_claim"),
)
_URL_PATTERN = re.compile(r"https?://[^\s<>()]+", re.I)
_TOKEN_PATTERN = re.compile(r"[\w-]{3,}", re.UNICODE)
_STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "have", "your",
    "about", "into", "are", "was", "were", "has", "had", "les", "des",
    "une", "pour", "dans", "avec", "sur", "est", "sont", "qui", "que",
}


def _tokens(value: str) -> set[str]:
    return {t for t in _TOKEN_PATTERN.findall(value.casefold()) if t not in _STOPWORDS}


def triage_social_item(item: SocialItem) -> SocialTriage:
    """Flag observable review risks without assigning a truth score."""
    text = f"{item.title} {item.text}"
    flags: list[str] = []
    for pattern, label in _CLICKBAIT:
        if pattern.search(text):
            flags.append(label)
    if not _URL_PATTERN.search(item.text) and not item.metadata.get("referenced_sources"):
        flags.append("no_source_reference_in_post")
    if not item.author:
        flags.append("author_identity_not_supplied")
    if item.metadata.get("sponsored") is True:
        flags.append("sponsored_or_promotional_context")
    if item.metadata.get("is_repost") is True:
        flags.append("repost_or_reshare")
    if item.metadata.get("language") in {"", None}:
        flags.append("language_not_identified")
    return SocialTriage(
        source_id=item.source_id,
        status="manual_review_required" if flags else "unverified_discovery",
        flags=tuple(dict.fromkeys(flags)),
    )


def build_claim_review_packet(claim: str, items: Iterable[SocialItem], limit: int = 20) -> dict:
    """Prepare a bounded human-review packet; recurrence is not corroboration."""
    if not claim.strip():
        raise ValueError("A non-empty claim is required.")
    limit = max(1, min(int(limit), 50))
    claim_terms = _tokens(claim)
    matches = []
    for item in islice(items, limit):
        overlap = sorted(claim_terms & _tokens(item.title + " " + item.text))
        if not overlap:
            continue
        matches.append({
            "source_id": item.source_id, "platform": item.platform, "url": item.url,
            "author": item.author, "published_at": item.published_at,
            "matching_terms": overlap, "triage": asdict(triage_social_item(item)),
        })
    platforms = sorted({entry["platform"] for entry in matches})
    return {
        "claim": claim.strip()[:1000],
        "status": "unverified_requires_human_review",
        "matching_source_count": len(matches),
        "platforms_seen": platforms,
        "cross_platform_recurrence": len(platforms) > 1,
        "cross_platform_recurrence_is_not_confirmation": True,
        "matches": matches,
        "required_next_steps": [
            "Locate the original paper, dataset, patent, standard, or primary experiment.",
            "Check methods, sample size, controls, uncertainty, date, and limitations.",
            "Search for independent replication and credible contradictory evidence.",
            "Record a qualified human review before changing any verification state.",
        ],
    }


def _fetch_json(url: str, headers: dict[str, str], timeout: float = DEFAULT_TIMEOUT) -> dict:
    request = Request(url, headers={**headers, "Accept": "application/json", "User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=max(2.0, min(float(timeout), 20.0))) as response:
            declared = response.headers.get("Content-Length")
            if declared and int(declared) > MAX_RESPONSE_BYTES:
                raise ValueError("Social API response exceeds the configured size limit.")
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"Platform API request failed: {type(exc).__name__}") from None
    if len(raw) > MAX_RESPONSE_BYTES:
        raise ValueError("Social API response exceeds the configured size limit.")
    payload = json.loads(raw.decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Social API returned an unexpected response shape.")
    if payload.get("error"):
        error = payload["error"]
        message = error.get("message", "API error") if isinstance(error, dict) else "API error"
        raise RuntimeError(str(message)[:240])
    return payload


class YouTubeDataAPIProvider:
    """Search public video metadata through official YouTube Data API v3.

    The Data API does not grant arbitrary transcript access. This adapter does
    not download videos or bypass caption permissions.
    """
    name = "youtube-data-api"
    endpoint = "https://www.googleapis.com/youtube/v3/search"

    def __init__(self, api_key: str, max_results: int = 5, timeout: float = DEFAULT_TIMEOUT,
                 request_json: Callable = _fetch_json):
        if not api_key.strip():
            raise ValueError("A YouTube Data API key is required.")
        self._api_key = api_key.strip()
        self.max_results = max(1, min(int(max_results), MAX_RESULTS))
        self.timeout = timeout
        self.request_json = request_json

    def search(self, query: str) -> list[SocialItem]:
        if not query.strip():
            return []
        params = urlencode({
            "part": "snippet", "type": "video", "q": query[:300],
            "maxResults": self.max_results, "order": "relevance",
            "safeSearch": "strict", "key": self._api_key,
        })
        payload = self.request_json(self.endpoint + "?" + params, {}, self.timeout)
        items = []
        for row in payload.get("items", [])[:self.max_results]:
            if not isinstance(row, dict):
                continue
            ident, snippet = row.get("id") or {}, row.get("snippet") or {}
            video_id = str(ident.get("videoId") or "").strip() if isinstance(ident, dict) else ""
            title = str(snippet.get("title") or "").strip()
            if not video_id or not title:
                continue
            items.append(SocialItem(
                platform="youtube", source_id=f"youtube:{video_id}",
                title=title[:500], text=str(snippet.get("description") or "")[:5000],
                url=f"https://www.youtube.com/watch?v={video_id}",
                author=str(snippet.get("channelTitle") or "")[:200],
                published_at=str(snippet.get("publishedAt") or "")[:40],
                content_type="video_metadata",
                metadata={
                    "channel_id": str(snippet.get("channelId") or "")[:120],
                    "language": str(snippet.get("defaultLanguage") or snippet.get("defaultAudioLanguage") or ""),
                    "transcript_retrieved": False, "engagement_is_not_evidence": True,
                },
            ))
        return items


class XRecentSearchProvider:
    """Search public recent posts through official X API v2."""
    name = "x-api-v2"
    endpoint = "https://api.x.com/2/tweets/search/recent"

    def __init__(self, bearer_token: str, max_results: int = 10, timeout: float = DEFAULT_TIMEOUT,
                 request_json: Callable = _fetch_json):
        if not bearer_token.strip():
            raise ValueError("An X API bearer token is required.")
        self._token = bearer_token.strip()
        self.max_results = max(10, min(int(max_results), 100))
        self.timeout = timeout
        self.request_json = request_json

    def search(self, query: str) -> list[SocialItem]:
        if not query.strip():
            return []
        params = urlencode({
            "query": f"({query[:240]}) -is:retweet", "max_results": self.max_results,
            "tweet.fields": "created_at,lang,public_metrics,context_annotations,entities,author_id",
            "expansions": "author_id",
            "user.fields": "name,username,verified,description",
        })
        payload = self.request_json(
            self.endpoint + "?" + params,
            {"Authorization": f"Bearer {self._token}"}, self.timeout,
        )
        users = {
            str(user.get("id")): user
            for user in payload.get("includes", {}).get("users", []) if isinstance(user, dict)
        }
        items = []
        for row in payload.get("data", [])[:self.max_results]:
            if not isinstance(row, dict):
                continue
            post_id, text = str(row.get("id") or "").strip(), str(row.get("text") or "").strip()
            if not post_id or not text:
                continue
            user = users.get(str(row.get("author_id", "")), {})
            username = str(user.get("username") or "")
            metrics = row.get("public_metrics") or {}
            items.append(SocialItem(
                platform="x", source_id=f"x:{post_id}", title=text[:180], text=text[:5000],
                url=f"https://x.com/{username}/status/{post_id}" if username else f"https://x.com/i/web/status/{post_id}",
                author=f"@{username}" if username else "",
                published_at=str(row.get("created_at") or "")[:40],
                content_type="public_post",
                metadata={
                    "language": str(row.get("lang") or ""),
                    "author_verified_badge": bool(user.get("verified", False)),
                    "author_description": str(user.get("description") or "")[:300],
                    "public_metrics": metrics if isinstance(metrics, dict) else {},
                    "engagement_is_not_evidence": True,
                    "verification_badge_is_not_scientific_validation": True,
                },
            ))
        return items


class InstagramBusinessDiscoveryProvider:
    """Discover posts only from configured public professional accounts.

    Instagram Graph API does not provide unrestricted public-post search.
    This adapter intentionally does not scrape Instagram pages.
    """
    name = "instagram-graph-business-discovery"
    graph_version = "v22.0"
    endpoint = "https://graph.facebook.com"

    def __init__(self, access_token: str, instagram_user_id: str, usernames: Iterable[str],
                 max_results_per_account: int = 10, timeout: float = DEFAULT_TIMEOUT,
                 request_json: Callable = _fetch_json):
        if not access_token.strip() or not instagram_user_id.strip():
            raise ValueError("Instagram Graph API access token and professional user ID are required.")
        self._token = access_token.strip()
        self.instagram_user_id = instagram_user_id.strip()
        self.usernames = tuple(dict.fromkeys(
            re.sub(r"^@", "", str(name).strip()).lower()
            for name in usernames if re.fullmatch(r"@?[A-Za-z0-9._]{1,30}", str(name).strip())
        ))[:10]
        self.max_results = max(1, min(int(max_results_per_account), 25))
        self.timeout = timeout
        self.request_json = request_json

    def search(self, query: str) -> list[SocialItem]:
        terms = _tokens(query)
        if not terms:
            return []
        results = []
        for username in self.usernames:
            fields = f"business_discovery.username({username}){{username,media.limit({self.max_results}){{id,caption,media_type,permalink,timestamp}}}}"
            params = urlencode({"fields": fields, "access_token": self._token})
            url = f"{self.endpoint}/{self.graph_version}/{self.instagram_user_id}?{params}"
            payload = self.request_json(url, {}, self.timeout)
            discovery = payload.get("business_discovery") or {}
            account = str(discovery.get("username") or username)
            for media in discovery.get("media", {}).get("data", [])[:self.max_results]:
                if not isinstance(media, dict):
                    continue
                caption = str(media.get("caption") or "")
                if not (terms & _tokens(caption)):
                    continue
                permalink, media_id = str(media.get("permalink") or ""), str(media.get("id") or "")
                if not permalink.startswith("https://www.instagram.com/") or not media_id:
                    continue
                results.append(SocialItem(
                    platform="instagram", source_id=f"instagram:{media_id}",
                    title=caption[:180] or f"Instagram post from @{account}",
                    text=caption[:5000], url=permalink, author=f"@{account}",
                    published_at=str(media.get("timestamp") or "")[:40],
                    content_type=str(media.get("media_type") or "post").lower(),
                    metadata={"account_scope": "configured_public_professional_account"},
                ))
        return results[:MAX_RESULTS]


class SocialResearchProvider:
    """Aggregate configured official-platform adapters into a bounded ProviderResult."""
    name = "social-video-research-discovery"

    def __init__(self, providers: Iterable[object], max_results: int = MAX_RESULTS):
        self.providers = tuple(providers)[:3]
        self.max_results = max(1, min(int(max_results), MAX_RESULTS))

    @classmethod
    def from_environment(cls, max_results: int = MAX_RESULTS) -> "SocialResearchProvider":
        providers = []
        youtube_key = os.getenv("SSSWET_YOUTUBE_API_KEY", "").strip()
        x_token = os.getenv("SSSWET_X_BEARER_TOKEN", "").strip()
        instagram_token = os.getenv("SSSWET_INSTAGRAM_ACCESS_TOKEN", "").strip()
        instagram_user_id = os.getenv("SSSWET_INSTAGRAM_USER_ID", "").strip()
        instagram_accounts = os.getenv("SSSWET_INSTAGRAM_BUSINESS_ACCOUNTS", "").split(",")
        if youtube_key:
            providers.append(YouTubeDataAPIProvider(youtube_key, max_results=max_results))
        if x_token:
            providers.append(XRecentSearchProvider(x_token, max_results=max_results))
        if instagram_token and instagram_user_id and any(x.strip() for x in instagram_accounts):
            providers.append(InstagramBusinessDiscoveryProvider(
                instagram_token, instagram_user_id, instagram_accounts,
                max_results_per_account=max_results,
            ))
        return cls(providers, max_results=max_results)

    def search(self, query: str) -> tuple[list[SocialItem], tuple[str, ...]]:
        if not query.strip():
            raise ValueError("A non-empty social research query is required.")
        if not self.providers:
            return [], (
                "No official social-platform API credentials are configured. "
                "Set the relevant SSSWET environment variables; no scraping fallback is used.",
            )
        items: list[SocialItem] = []
        errors: list[str] = []
        with ThreadPoolExecutor(max_workers=min(3, len(self.providers)), thread_name_prefix="ssswet-social") as pool:
            futures = {pool.submit(provider.search, query): provider for provider in self.providers}
            for future in as_completed(futures):
                provider = futures[future]
                try:
                    items.extend(future.result())
                except Exception as exc:
                    errors.append(f"{provider.name}: {type(exc).__name__}: {str(exc)[:180]}")
        unique: dict[str, SocialItem] = {}
        for item in items:
            unique.setdefault(item.source_id, item)
        ordered = sorted(
            unique.values(), key=lambda item: (item.published_at or "", item.platform, item.source_id),
            reverse=True,
        )
        return ordered[:self.max_results], tuple(errors)

    def investigate(self, objective: str, strategy: str) -> ProviderResult:
        items, errors = self.search(objective)
        if not items:
            detail = " ".join(errors) if errors else "No matching public items were returned."
            return ProviderResult("Social discovery returned no usable items. " + detail, uncertainty=1.0)
        records, source_ids = [], []
        for item in items:
            record = item.as_record()
            record["automated_triage"] = asdict(triage_social_item(item))
            records.append(json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
            source_ids.append(item.source_id)
        summary = (
            f"Discovered {len(items)} public social/video item(s). These are contextual leads only, "
            "not scientific evidence or verified claims. Popularity, views, likes and verification badges "
            "are not evidence. Review original studies, methods, independent replication and counter-evidence."
        )
        if errors:
            summary += " Platform errors: " + "; ".join(errors)
        return ProviderResult(summary, tuple(records), 1.0, tuple(source_ids))

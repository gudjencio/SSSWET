"""Bounded, permission-aware research query plans for public discovery channels."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date

MAX_TERMS = 50
MAX_QUERIES = 100
CHANNELS = {
    "scholarly_index": "official_public_index_or_api",
    "preprint_server": "official_public_api",
    "technical_standards": "authorized_catalogue_access",
    "institutional_repository": "public_repository_or_official_api",
    "youtube": "official_public_api",
    "x": "official_api_or_authorized_public_search",
    "instagram": "approved_meta_graph_api_scope_for_public_professional_accounts",
    "facebook": "approved_graph_api_scope_for_configured_public_pages",
    "threads": "approved_threads_api_scope",
    "bluesky": "public_atproto_appview",
    "reddit": "official_api_or_permitted_public_access",
    "snapchat": "official_approved_public_discovery_only",
    "mewe": "operator_configured_authorized_public_feed",
    "weibo": "official_or_authorized_public_api",
    "bilibili": "official_or_authorized_public_search",
    "niconico": "official_or_authorized_public_search",
    "qiita": "official_public_api",
    "web_forum": "public_pages_subject_to_site_terms",
}


def _clean(value, field, maximum=240):
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > maximum:
        raise ValueError(f"{field} must contain 1 to {maximum} characters")
    return value.strip()


def _date(value, field):
    if value in (None, ""):
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field} must be an ISO date")
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO date") from exc


def build_query_plan(*, objective: str, terms: list[dict], source_channels: list[str],
                     languages: list[str] | None = None, date_from: str | None = None,
                     date_to: str | None = None, inclusion_terms: list[str] | None = None,
                     exclusion_terms: list[str] | None = None, max_queries: int = 100) -> dict:
    """Create a reproducible search plan; never logs in, scrapes private data or executes it."""
    objective = _clean(objective, "objective", 2000)
    if not isinstance(terms, list) or not 1 <= len(terms) <= MAX_TERMS:
        raise ValueError(f"terms must contain 1 to {MAX_TERMS} items")
    normalized_terms = []
    for item in terms:
        if not isinstance(item, dict):
            raise ValueError("each term must include term and language")
        term = _clean(item.get("term"), "term")
        language = _clean(item.get("language"), "language", 12).lower()
        if not re.fullmatch(r"[a-z]{2,3}(?:-[a-z0-9]{2,8})*", language):
            raise ValueError("language must be a BCP-47-like language tag")
        normalized_terms.append({"term": term, "language": language})
    if not isinstance(source_channels, list) or not source_channels or any(not isinstance(item, str) or not item.strip() for item in source_channels):
        raise ValueError("source_channels must be a non-empty list of channel names")
    channels = sorted(set(item.strip().lower() for item in source_channels))
    unknown = sorted(set(channels) - set(CHANNELS))
    if unknown:
        raise ValueError("unsupported source channels: " + ", ".join(unknown))
    if not isinstance(max_queries, int) or isinstance(max_queries, bool) or not 1 <= max_queries <= MAX_QUERIES:
        raise ValueError(f"max_queries must be between 1 and {MAX_QUERIES}")
    if languages is not None and (not isinstance(languages, list) or len(languages) > 100):
        raise ValueError("languages must be a list of at most 100 language tags")
    raw_languages = languages if languages is not None else [item["language"] for item in normalized_terms]
    if any(not isinstance(code, str) or not re.fullmatch(r"[a-z]{2,3}(?:-[a-z0-9]{2,8})*", code.strip().lower()) for code in raw_languages):
        raise ValueError("languages must contain valid language tags")
    langs = sorted(set(code.strip().lower() for code in raw_languages))
    start, end = _date(date_from, "date_from"), _date(date_to, "date_to")
    if start and end and start > end:
        raise ValueError("date_from must not be later than date_to")

    def phrase_list(values, field):
        if not isinstance(values, list) or len(values) > 50:
            raise ValueError(f"{field} must be a list of at most 50 terms")
        return [_clean(item, field, 160) for item in values]

    include = phrase_list(inclusion_terms or [], "inclusion term")
    exclude = phrase_list(exclusion_terms or [], "exclusion term")
    queries = []
    for item in normalized_terms:
        parts = ['"' + item["term"].replace('"', '\\"') + '"']
        if include:
            parts.append("(" + " OR ".join('"' + value.replace('"', '\\"') + '"' for value in include) + ")")
        if exclude:
            parts.append(" ".join("-" + '"' + value.replace('"', '\\"') + '"' for value in exclude))
        queries.append({
            "query": " ".join(parts),
            "language": item["language"],
            "concept": item["term"],
            "date_from": start,
            "date_to": end,
        })
    queries = queries[:max_queries]
    channel_policy = [{
        "channel": channel,
        "access_mode": CHANNELS[channel],
        "operator_configuration_required": channel in {
            "instagram", "facebook", "threads", "snapchat", "mewe", "weibo", "bilibili", "niconico",
        },
        "private_or_restricted_content_access": False,
    } for channel in channels]
    payload = {
        "schema_version": 1, "objective": objective, "queries": queries,
        "source_channels": channel_policy, "languages": langs,
        "inclusion_terms": include, "exclusion_terms": exclude,
        "query_count": len(queries), "truncated": len(normalized_terms) > len(queries),
        "execution_started": False, "private_data_accessed": False,
        "terms_of_service_bypass": False,
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return {**payload, "plan_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest()}

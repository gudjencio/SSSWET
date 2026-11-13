"""Permission-aware normalization of public social/video metadata.

This module accepts records already obtained through an official API or a
permitted public feed. It does not fetch pages, authenticate, download media,
or access private/restricted content.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from urllib.parse import urlsplit

MAX_BATCH = 500
MAX_TEXT = 5_000
MAX_COUNTER = 10**12

CHANNEL_ACCESS = {
    "youtube": {"official_api"},
    "x": {"official_api", "authorized_public_search"},
    "instagram": {"approved_meta_graph_api"},
    "facebook": {"approved_meta_graph_api"},
    "threads": {"approved_threads_api"},
    "bluesky": {"public_atproto_appview"},
    "reddit": {"official_api", "permitted_public_feed"},
    "snapchat": {"approved_public_discovery"},
    "mewe": {"authorized_public_feed"},
    "weibo": {"official_api", "authorized_public_api"},
    "bilibili": {"official_api", "authorized_public_api"},
    "niconico": {"official_api", "authorized_public_api"},
    "qiita": {"official_api"},
    "web_forum": {"permitted_public_page", "authorized_public_feed"},
}

CHANNEL_FIELDS = {
    "youtube": {"video_id", "title", "description", "channel_title", "published_at", "duration_seconds", "language", "captions_available", "view_count", "like_count", "comment_count"},
    "x": {"post_id", "text", "published_at", "language", "author_display_name", "like_count", "reply_count", "repost_count", "quote_count", "public_permalink"},
    "instagram": {"media_id", "caption", "published_at", "media_type", "author_display_name", "like_count", "comment_count", "public_permalink"},
    "facebook": {"post_id", "text", "published_at", "page_name", "like_count", "comment_count", "public_permalink"},
    "threads": {"thread_id", "text", "published_at", "language", "author_display_name", "like_count", "reply_count", "public_permalink"},
    "bluesky": {"uri", "text", "published_at", "language", "author_display_name", "like_count", "reply_count", "repost_count", "public_permalink"},
    "reddit": {"post_id", "title", "text", "published_at", "subreddit", "score", "reply_count", "flair_text", "public_permalink"},
    "snapchat": {"story_id", "caption", "published_at", "public_profile_name", "view_count", "public_permalink"},
    "mewe": {"post_id", "text", "published_at", "public_group_name", "reply_count", "public_permalink"},
    "weibo": {"post_id", "text", "published_at", "author_display_name", "like_count", "reply_count", "repost_count", "public_permalink"},
    "bilibili": {"video_id", "title", "description", "published_at", "duration_seconds", "author_display_name", "view_count", "reply_count", "public_permalink"},
    "niconico": {"content_id", "title", "description", "published_at", "duration_seconds", "channel_title", "view_count", "public_permalink"},
    "qiita": {"post_id", "title", "text", "published_at", "updated_at", "author_display_name", "like_count", "tags", "public_permalink"},
    "web_forum": {"thread_id", "title", "text", "published_at", "forum_name", "reply_count", "tags", "public_permalink"},
}

_TEXT_FIELDS = {
    "title", "description", "text", "caption", "channel_title", "page_name",
    "subreddit", "flair_text", "public_profile_name", "public_group_name",
    "forum_name", "author_display_name", "media_type",
}
_COUNTER_FIELDS = {"view_count", "like_count", "comment_count", "reply_count", "repost_count", "quote_count", "score"}
_ID_FIELDS = {"video_id", "post_id", "media_id", "thread_id", "story_id", "content_id", "uri"}
_SENSITIVE_NAMES = {
    "email", "phone", "telephone", "private_message", "direct_message", "dm",
    "access_token", "refresh_token", "authorization", "cookie", "password",
    "precise_location", "latitude", "longitude", "ip_address", "home_address",
    "private_profile_id", "follower_list", "friend_list",
}


def _text(value: object, field: str, maximum: int = 240) -> str:
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > maximum:
        raise ValueError(f"{field} must contain 1 to {maximum} characters")
    return value.strip()


def _timestamp(value: object, field: str, *, required: bool = False) -> str | None:
    if value in (None, "") and not required:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a timezone-aware ISO timestamp")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be a timezone-aware ISO timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc).isoformat()


def _https_url(value: object, field: str) -> str:
    url = _text(value, field, 2_000)
    try:
        parsed = urlsplit(url)
        parsed.port
    except ValueError as exc:
        raise ValueError(f"{field} is not a valid URL") from exc
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError(f"{field} must be an HTTPS URL without embedded credentials")
    return url


def _sensitive_names(value: object, prefix: str = "") -> list[str]:
    if not isinstance(value, dict):
        return []
    found = []
    for key, nested in value.items():
        normalized = re.sub(r"[^a-z0-9]+", "_", str(key).casefold()).strip("_")
        path = f"{prefix}.{key}" if prefix else str(key)
        if normalized in _SENSITIVE_NAMES:
            found.append(path)
        if isinstance(nested, dict):
            found.extend(_sensitive_names(nested, path))
    return sorted(set(found))


def normalize_public_record(record: dict) -> dict:
    """Normalize one already-authorized public record; unknown fields are omitted."""
    if not isinstance(record, dict):
        raise ValueError("record must be an object")
    platform = _text(record.get("platform"), "platform", 40).lower()
    if platform not in CHANNEL_ACCESS:
        raise ValueError("unsupported public platform")
    visibility = _text(record.get("visibility"), "visibility", 40).lower()
    if visibility not in {"public", "public_professional"}:
        raise ValueError("only explicitly public content may be normalized")
    access_mode = _text(record.get("access_mode"), "access_mode", 80).lower()
    if access_mode not in CHANNEL_ACCESS[platform]:
        raise ValueError("access_mode is not approved for this platform")
    source_url = _https_url(record.get("source_url"), "source_url")
    captured_at = _timestamp(record.get("captured_at"), "captured_at", required=True)
    published_at = _timestamp(record.get("published_at"), "published_at")
    source_id = record.get("source_id")
    if source_id in (None, ""):
        provider_id = _text(record.get("provider_item_id"), "provider_item_id", 240)
        source_id = f"{platform}:{provider_id}"
    source_id = _text(source_id, "source_id", 300)
    content_type = _text(record.get("content_type"), "content_type", 30).lower()
    if content_type not in {"video", "post", "thread", "forum_post"}:
        raise ValueError("content_type must be video, post, thread or forum_post")
    raw_metadata = record.get("metadata", {})
    if not isinstance(raw_metadata, dict):
        raise ValueError("metadata must be an object")
    allowed = CHANNEL_FIELDS[platform]
    safe_metadata = {}
    discarded = sorted(str(key) for key in raw_metadata if key not in allowed)
    sensitive = _sensitive_names(raw_metadata)
    for key in sorted(allowed & set(raw_metadata)):
        value = raw_metadata[key]
        if key in _TEXT_FIELDS:
            if value is None or value == "":
                continue
            safe_metadata[key] = _text(value, f"metadata.{key}", MAX_TEXT)
        elif key in _COUNTER_FIELDS:
            if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= MAX_COUNTER:
                raise ValueError(f"metadata.{key} must be a bounded non-negative integer")
            safe_metadata[key] = value
        elif key in _ID_FIELDS:
            safe_metadata[key] = _text(value, f"metadata.{key}", 300)
        elif key in {"published_at", "updated_at"}:
            safe_metadata[key] = _timestamp(value, f"metadata.{key}", required=True)
        elif key == "duration_seconds":
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 604_800:
                raise ValueError("metadata.duration_seconds must be between 0 and 604800")
            safe_metadata[key] = float(value)
        elif key == "captions_available":
            if not isinstance(value, bool):
                raise ValueError("metadata.captions_available must be boolean")
            safe_metadata[key] = value
        elif key == "language":
            language = _text(value, "metadata.language", 20).lower()
            if not re.fullmatch(r"[a-z]{2,3}(?:-[a-z0-9]{2,8})*", language):
                raise ValueError("metadata.language must be a BCP-47-like language tag")
            safe_metadata[key] = language
        elif key == "tags":
            if not isinstance(value, list) or len(value) > 50:
                raise ValueError("metadata.tags must be a list of at most 50 strings")
            safe_metadata[key] = [_text(item, "metadata tag", 80) for item in value]
    if "published_at" in safe_metadata:
        published_at = safe_metadata["published_at"]
    safe = {
        "schema_version": 1,
        "source_id": source_id,
        "platform": platform,
        "content_type": content_type,
        "visibility": visibility,
        "access_mode": access_mode,
        "source_url": source_url,
        "published_at": published_at,
        "captured_at": captured_at,
        "metadata": safe_metadata,
        "discarded_field_names": discarded,
        "sensitive_field_names_flagged": sensitive,
        "private_content_accessed": False,
        "media_downloaded": False,
        "terms_of_service_bypass": False,
        "scientific_evidence_established": False,
        "discovery_only": True,
    }
    canonical = json.dumps(safe, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    safe["snapshot_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    content_basis = {key: safe[key] for key in ("source_id", "platform", "content_type", "source_url", "published_at", "metadata")}
    content_json = json.dumps(content_basis, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    safe["content_sha256"] = hashlib.sha256(content_json.encode("utf-8")).hexdigest()
    return safe


def normalize_public_batch(records: list[dict]) -> dict:
    if not isinstance(records, list) or len(records) > MAX_BATCH:
        raise ValueError(f"records must be a list of at most {MAX_BATCH}")
    normalized = [normalize_public_record(item) for item in records]
    by_id: dict[str, list[str]] = {}
    for item in normalized:
        by_id.setdefault(item["source_id"], []).append(item["snapshot_sha256"])
    duplicates = [
        {"source_id": source_id, "snapshot_count": len(hashes), "snapshot_hashes": hashes}
        for source_id, hashes in sorted(by_id.items()) if len(hashes) > 1
    ]
    return {
        "records": normalized,
        "record_count": len(normalized),
        "duplicate_candidates": duplicates,
        "records_discarded": 0,
        "private_content_accessed": False,
        "scientific_evidence_established": False,
    }

"""Bounded extensions for permitted public-media evidence workflows.

All inputs are supplied by the caller. This module never fetches feeds, calls
platform APIs, downloads media, authenticates, or decides scientific truth.
"""
from __future__ import annotations

import hashlib
import html
import ipaddress
import json
import re
import unicodedata
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from urllib.parse import urlsplit, urlunsplit

from .multilingual_research_triage import script_profile, tokenize, triage_title
from .public_media_ingestion import CHANNEL_ACCESS, CHANNEL_FIELDS, normalize_public_record
from .public_media_research_workbench import extract_claim_candidates

SCHEMA_VERSION = 1
MAX_FEED_BYTES = 2 * 1024 * 1024
MAX_FEED_ENTRIES = 250
MAX_FEED_TEXT_CHARS = 20_000
MAX_PAGINATION_PAGES = 500
MAX_PAGE_ITEMS = 1_000
MAX_CURSOR_CHARS = 2_048
MAX_TRANSCRIPT_BYTES = 2 * 1024 * 1024
MAX_TRANSCRIPT_CUES = 5_000
MAX_TRANSCRIPT_TEXT_CHARS = 1_000_000
MAX_LEDGER_EVENTS = 500
MAX_PRIVACY_TEXT_CHARS = 100_000
MAX_REVIEW_PACKET_BYTES = 5 * 1024 * 1024
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_LANGUAGE_TAG = re.compile(r"^[a-z]{2,3}(?:-[a-z0-9]{2,8})*$")
_TIMESTAMP = re.compile(
    r"^(?P<start>(?:\d{2,}:)?\d{2}:\d{2}[.,]\d{3})\s+-->\s+"
    r"(?P<end>(?:\d{2,}:)?\d{2}:\d{2}[.,]\d{3})(?:\s+.*)?$"
)
_TEXT_FIELDS = ("title", "description", "text", "caption", "summary", "content")
_SCRIPT_BY_LANGUAGE = {
    "ar": "arabic", "fa": "arabic", "ur": "arabic",
    "bn": "bengali", "as": "bengali",
    "ru": "cyrillic", "uk": "cyrillic", "bg": "cyrillic",
    "he": "hebrew", "yi": "hebrew",
    "hi": "devanagari", "mr": "devanagari", "ne": "devanagari",
    "th": "thai", "ko": "hangul",
    "en": "latin", "fr": "latin", "de": "latin", "es": "latin",
    "pt": "latin", "it": "latin", "nl": "latin", "sv": "latin",
    "da": "latin", "no": "latin", "fi": "latin", "id": "latin",
    "vi": "latin", "tr": "latin", "pl": "latin", "cs": "latin",
    "ro": "latin", "hu": "latin", "el": "greek",
}
_CERTAINTY_CUES = (
    "proves", "guaranteed", "cures", "always works", "never fails",
    "prouve", "garanti", "guérit", "fonctionne toujours", "ne rate jamais",
    "証明", "必ず治る", "絶対", "保证", "治愈", "绝对有效",
    "증명", "완치", "절대적으로",
)
_QUALIFIER_CUES = (
    "may", "might", "could", "preliminary", "pilot", "in vitro",
    "not statistically significant", "small sample", "limited evidence",
    "pourrait", "peut", "préliminaire", "étude pilote", "in vitro",
    "échantillon limité", "証拠は限定的", "可能性", "予備的",
    "可能", "初步", "样本有限", "증거가 제한적",
)


def _canonical(value: object) -> bytes:
    try:
        return json.dumps(
            value, ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("value must be finite and canonically JSON serializable") from exc


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _clean(value: object, field: str, maximum: int, *, empty: bool = False) -> str:
    if not isinstance(value, str) or len(value) > maximum:
        raise ValueError(f"{field} must be text of at most {maximum} characters")
    result = value.strip()
    if not result and not empty:
        raise ValueError(f"{field} must not be empty")
    if any(ord(char) < 32 and char not in "\n\r\t" for char in result):
        raise ValueError(f"{field} contains control characters")
    return result


def _sha(value: object, field: str) -> str:
    result = _clean(value, field, 64)
    if not _SHA256.fullmatch(result):
        raise ValueError(f"{field} must be a lowercase SHA-256 digest")
    return result


def _host_from_url(value: object, field: str) -> tuple[str, str]:
    url = _clean(value, field, 2_000)
    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError as exc:
        raise ValueError(f"{field} is not a valid URL") from exc
    if parts.scheme.lower() != "https" or not parts.hostname:
        raise ValueError(f"{field} must be an absolute HTTPS URL")
    if parts.username or parts.password or port not in (None, 443):
        raise ValueError(f"{field} must not contain credentials or a non-standard port")
    raw_host = parts.hostname.rstrip(".").lower()
    try:
        ipaddress.ip_address(raw_host)
    except ValueError:
        pass
    else:
        raise ValueError(f"{field} must not use an IP-literal host")
    try:
        host = raw_host.encode("idna").decode("ascii").removeprefix("www.")
    except UnicodeError as exc:
        raise ValueError(f"{field} has an invalid hostname") from exc
    return host, url


def _approved_hosts(values: list[str] | tuple[str, ...]) -> set[str]:
    if not isinstance(values, (list, tuple)) or not 1 <= len(values) <= 50:
        raise ValueError("approved_hosts must contain between 1 and 50 hostnames")
    hosts = set()
    for value in values:
        host = _clean(value, "approved host", 253).lower().rstrip(".")
        if "://" in host or "/" in host or "@" in host or ":" in host:
            raise ValueError("approved_hosts must contain hostnames, not URLs")
        try:
            ipaddress.ip_address(host.strip("[]"))
        except ValueError:
            pass
        else:
            raise ValueError("approved_hosts must not contain IP literals")
        try:
            host = host.encode("idna").decode("ascii").removeprefix("www.")
        except UnicodeError as exc:
            raise ValueError("approved host is not valid IDNA") from exc
        if "." not in host:
            raise ValueError("approved host must be fully qualified")
        hosts.add(host)
    return hosts


class _VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.hidden = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"script", "style"}:
            self.hidden += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style"} and self.hidden:
            self.hidden -= 1

    def handle_data(self, data: str) -> None:
        if not self.hidden:
            self.parts.append(data)


def _plain_feed_text(value: object) -> str:
    if value is None:
        return ""
    raw = _clean(str(value), "feed text", MAX_FEED_TEXT_CHARS * 4, empty=True)
    parser = _VisibleText()
    parser.feed(raw)
    parser.close()
    return " ".join(html.unescape(" ".join(parser.parts)).split())[:MAX_FEED_TEXT_CHARS]


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].split(":")[-1].lower()


def _xml_child(element: ET.Element, *names: str) -> str:
    wanted = {name.lower() for name in names}
    for child in list(element):
        if _local(child.tag) in wanted:
            return "".join(child.itertext()).strip()
    return ""


def _feed_date(value: str) -> tuple[str | None, str | None]:
    if not value:
        return None, None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        try:
            parsed = parsedate_to_datetime(value.strip())
        except (TypeError, ValueError, OverflowError):
            return None, "published_date_unparsed"
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None, "published_date_timezone_missing"
    return parsed.astimezone(timezone.utc).isoformat(), None


def _feed_entries(payload: str, format_hint: str | None) -> tuple[str, str, list[dict]]:
    detected = format_hint.lower() if isinstance(format_hint, str) else None
    if detected not in (None, "rss", "atom", "jsonfeed"):
        raise ValueError("format_hint must be rss, atom or jsonfeed")
    if detected == "jsonfeed" or (detected is None and payload.lstrip().startswith("{")):
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise ValueError("JSON Feed is malformed") from exc
        if not isinstance(data, dict) or data.get("version") != "https://jsonfeed.org/version/1.1":
            raise ValueError("only JSON Feed 1.1 is supported")
        items = data.get("items")
        if not isinstance(items, list) or len(items) > MAX_FEED_ENTRIES:
            raise ValueError("JSON Feed items must be a list of at most 250 entries")
        rows = []
        for item in items:
            if not isinstance(item, dict):
                raise ValueError("every JSON Feed item must be an object")
            rows.append({
                "id": item.get("id"),
                "url": item.get("url") or item.get("external_url"),
                "title": item.get("title", ""),
                "body": item.get("content_text") or item.get("content_html") or item.get("summary", ""),
                "date": item.get("date_published") or item.get("date_modified", ""),
            })
        return "jsonfeed", _plain_feed_text(data.get("title", "")), rows

    if "<!DOCTYPE" in payload.upper() or "<!ENTITY" in payload.upper():
        raise ValueError("XML DTD and entity declarations are not accepted")
    try:
        root = ET.fromstring(payload)
    except ET.ParseError as exc:
        raise ValueError("RSS/Atom XML is malformed") from exc
    root_name = _local(root.tag)
    if root_name == "rss":
        channel = next((item for item in list(root) if _local(item.tag) == "channel"), None)
        if channel is None:
            raise ValueError("RSS channel is missing")
        items = [item for item in list(channel) if _local(item.tag) == "item"]
        rows = [{
            "id": _xml_child(item, "guid"),
            "url": _xml_child(item, "link"),
            "title": _xml_child(item, "title"),
            "body": _xml_child(item, "encoded", "description", "content"),
            "date": _xml_child(item, "pubdate", "published"),
        } for item in items]
        return "rss", _xml_child(channel, "title"), rows
    if root_name == "feed":
        entries = [item for item in list(root) if _local(item.tag) == "entry"]
        rows = []
        for item in entries:
            link = ""
            for child in list(item):
                if _local(child.tag) == "link":
                    rel = child.attrib.get("rel", "alternate").lower()
                    if rel == "alternate":
                        link = child.attrib.get("href", "")
                        if link:
                            break
            rows.append({
                "id": _xml_child(item, "id"),
                "url": link,
                "title": _xml_child(item, "title"),
                "body": _xml_child(item, "content", "summary"),
                "date": _xml_child(item, "published", "updated"),
            })
        return "atom", _xml_child(root, "title"), rows
    raise ValueError("XML feed root must be RSS or Atom")


def parse_public_feed(
    payload: str | bytes,
    *,
    captured_at: str,
    approved_hosts: list[str] | tuple[str, ...],
    format_hint: str | None = None,
) -> dict:
    """Parse caller-supplied RSS, Atom or JSON Feed into normalized public records."""
    if isinstance(payload, bytes):
        if len(payload) > MAX_FEED_BYTES:
            raise ValueError("feed exceeds the 2 MiB byte limit")
        try:
            text = payload.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ValueError("feed must be UTF-8") from exc
    elif isinstance(payload, str):
        text = payload
        if len(text.encode("utf-8")) > MAX_FEED_BYTES:
            raise ValueError("feed exceeds the 2 MiB byte limit")
    else:
        raise ValueError("payload must be UTF-8 text or bytes")
    if not text.strip():
        raise ValueError("feed payload must not be empty")
    captured = _clean(captured_at, "captured_at", 64)
    hosts = _approved_hosts(approved_hosts)
    feed_format, feed_title, rows = _feed_entries(text, format_hint)
    if len(rows) > MAX_FEED_ENTRIES:
        raise ValueError("feed exceeds the 250-entry limit")
    accepted, rejected, seen_ids = [], [], set()
    for index, row in enumerate(rows):
        raw_id = row.get("id")
        raw_url = row.get("url")
        title = _plain_feed_text(row.get("title", ""))
        body = _plain_feed_text(row.get("body", ""))
        identity_basis = str(raw_id or raw_url or f"{index}:{title}")
        entry_id = str(raw_id).strip() if raw_id not in (None, "") else hashlib.sha256(
            identity_basis.encode("utf-8")
        ).hexdigest()[:24]
        if not entry_id or len(entry_id) > 240 or entry_id in seen_ids:
            raise ValueError("feed entry identifiers must be unique and at most 240 characters")
        seen_ids.add(entry_id)
        if not raw_url:
            rejected.append({"entry_id": entry_id, "reason": "item_link_missing"})
            continue
        try:
            host, link = _host_from_url(raw_url, "feed item URL")
        except ValueError:
            rejected.append({"entry_id": entry_id, "reason": "item_link_not_safe_https"})
            continue
        if host not in hosts:
            rejected.append({"entry_id": entry_id, "reason": "item_host_not_allowlisted"})
            continue
        if not title and not body:
            rejected.append({"entry_id": entry_id, "reason": "item_text_missing"})
            continue
        published_at, date_warning = _feed_date(str(row.get("date") or ""))
        metadata = {
            "thread_id": entry_id,
            "title": title or body[:240],
            "text": body or title,
            "forum_name": feed_title or "public-feed",
            "public_permalink": link,
        }
        if published_at:
            metadata["published_at"] = published_at
        record = normalize_public_record({
            "platform": "web_forum",
            "visibility": "public",
            "access_mode": "authorized_public_feed",
            "source_url": link,
            "captured_at": captured,
            "provider_item_id": entry_id,
            "content_type": "forum_post",
            "metadata": metadata,
        })
        accepted.append({
            "record": record,
            "date_warning": date_warning,
            "feed_format": feed_format,
        })
    return {
        "schema_version": SCHEMA_VERSION,
        "feed_format": feed_format,
        "feed_title": feed_title,
        "entry_count": len(rows),
        "accepted_count": len(accepted),
        "rejected_count": len(rejected),
        "records": [item["record"] for item in accepted],
        "entry_warnings": [
            {"source_id": item["record"]["source_id"], "warning": item["date_warning"]}
            for item in accepted if item["date_warning"]
        ],
        "rejected_entries": rejected,
        "network_requests_made": False,
        "media_downloaded": False,
        "private_content_accessed": False,
        "scientific_evidence_established": False,
    }


def audit_adapter_contract(
    platform: str,
    *,
    access_mode: str,
    declared_fields: list[str],
    required_fields: list[str] | tuple[str, ...] = (),
) -> dict:
    """Expose and audit a provider adapter against existing allowlists."""
    name = _clean(platform, "platform", 40).lower()
    mode = _clean(access_mode, "access_mode", 80).lower()
    if name not in CHANNEL_ACCESS:
        raise ValueError("unsupported platform")
    if not isinstance(declared_fields, list) or len(declared_fields) > 100:
        raise ValueError("declared_fields must be a list of at most 100 names")
    if not isinstance(required_fields, (list, tuple)) or len(required_fields) > 100:
        raise ValueError("required_fields must contain at most 100 names")
    fields = [_clean(item, "declared field", 80) for item in declared_fields]
    required = [_clean(item, "required field", 80) for item in required_fields]
    if len(fields) != len(set(fields)) or len(required) != len(set(required)):
        raise ValueError("field declarations must not contain duplicates")
    allowed = CHANNEL_FIELDS[name]
    unsupported_required = sorted(set(required) - allowed)
    unexpected = sorted(set(fields) - allowed)
    missing = sorted(set(required) - set(fields))
    sensitive_names = {
        "email", "phone", "private_message", "direct_message", "access_token",
        "refresh_token", "authorization", "cookie", "password", "latitude",
        "longitude", "ip_address", "home_address", "follower_list", "friend_list",
    }
    sensitive = sorted(field for field in fields if field.casefold() in sensitive_names)
    access_valid = mode in CHANNEL_ACCESS[name]
    report = {
        "schema_version": SCHEMA_VERSION,
        "platform": name,
        "access_mode": mode,
        "access_mode_approved": access_valid,
        "allowed_fields": sorted(allowed),
        "declared_fields": sorted(fields),
        "required_fields": sorted(required),
        "missing_required_fields": missing,
        "unexpected_fields": unexpected,
        "unsupported_required_fields": unsupported_required,
        "sensitive_field_names": sensitive,
        "compatible": access_valid and not missing and not unexpected and not unsupported_required and not sensitive,
        "unknown_values_copied": False,
        "network_requests_made": False,
    }
    report["contract_sha256"] = _digest(report)
    return report


def build_pagination_checkpoint_chain(pages: list[dict]) -> dict:
    """Hash opaque page cursors without persisting cursor or credential values."""
    if not isinstance(pages, list) or len(pages) > MAX_PAGINATION_PAGES:
        raise ValueError("pages must be a list of at most 500 entries")
    output, seen_cursors, seen_page_ids = [], set(), set()
    previous_chain = "0" * 64
    previous_next_hash = None
    previous_next_ref = None
    provider = None
    for index, page in enumerate(pages):
        if not isinstance(page, dict):
            raise ValueError("each page must be an object")
        sequence = page.get("sequence")
        if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence != index:
            raise ValueError("page sequence must be contiguous and start at zero")
        current_provider = _clean(page.get("provider"), "provider", 80)
        if provider is None:
            provider = current_provider
        elif provider != current_provider:
            raise ValueError("one checkpoint chain may contain only one provider")
        cursor = page.get("cursor")
        next_cursor = page.get("next_cursor")
        for token, field in ((cursor, "cursor"), (next_cursor, "next_cursor")):
            if token is not None and (not isinstance(token, str) or not token or len(token) > MAX_CURSOR_CHARS):
                raise ValueError(f"{field} must be null or non-empty bounded text")
        cursor_hash = hashlib.sha256(cursor.encode("utf-8")).hexdigest() if cursor is not None else None
        next_hash = hashlib.sha256(next_cursor.encode("utf-8")).hexdigest() if next_cursor is not None else None
        cursor_ref = page.get("cursor_reference_id")
        next_ref = page.get("next_cursor_reference_id")
        if cursor is not None:
            cursor_ref = _clean(cursor_ref, "cursor_reference_id", 200)
        elif cursor_ref not in (None, ""):
            raise ValueError("first-page cursor reference must be empty")
        if next_cursor is not None:
            next_ref = _clean(next_ref, "next_cursor_reference_id", 200)
        elif next_ref not in (None, ""):
            raise ValueError("terminal page must not declare a next cursor reference")
        if index == 0 and cursor is not None:
            raise ValueError("first page must use a null cursor")
        if index and (cursor_hash != previous_next_hash or cursor_ref != previous_next_ref):
            raise ValueError("page cursor does not match the previous checkpoint's next cursor")
        if cursor_hash is not None:
            if cursor_hash in seen_cursors:
                raise ValueError("pagination cursor loop detected")
            seen_cursors.add(cursor_hash)
        if next_hash is not None and next_hash in seen_cursors:
            raise ValueError("pagination cursor loop detected: next cursor repeats an earlier cursor")
        item_ids = page.get("item_ids")
        if not isinstance(item_ids, list) or len(item_ids) > MAX_PAGE_ITEMS:
            raise ValueError("item_ids must be a list of at most 1000 IDs")
        ids = [_clean(item, "item_id", 300) for item in item_ids]
        if len(ids) != len(set(ids)):
            raise ValueError("item_ids must be unique within a page")
        page_id = _clean(page.get("page_id"), "page_id", 200)
        if page_id in seen_page_ids:
            raise ValueError("page_id values must be unique")
        seen_page_ids.add(page_id)
        captured_at = _clean(page.get("captured_at"), "captured_at", 64)
        event = {
            "sequence": sequence,
            "page_id": page_id,
            "provider": current_provider,
            "cursor_sha256": cursor_hash,
            "cursor_reference_id": cursor_ref,
            "next_cursor_sha256": next_hash,
            "next_cursor_reference_id": next_ref,
            "item_ids": ids,
            "captured_at": captured_at,
        }
        page_hash = _digest(event)
        chain_hash = _digest({"previous_chain_sha256": previous_chain, "page_sha256": page_hash})
        output.append({**event, "page_sha256": page_hash, "chain_sha256": chain_hash})
        previous_chain = chain_hash
        previous_next_hash, previous_next_ref = next_hash, next_ref
    return {
        "schema_version": SCHEMA_VERSION,
        "provider": provider,
        "page_count": len(output),
        "pages": output,
        "head_sha256": previous_chain,
        "raw_cursor_tokens_persisted": False,
        "credentials_persisted": False,
        "external_secure_cursor_store_required_for_resume": True,
    }


def verify_pagination_checkpoint_chain(chain: dict) -> dict:
    """Verify checkpoint order, cursor continuity and tamper-evident hashes."""
    if not isinstance(chain, dict) or chain.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported pagination checkpoint schema")
    if chain.get("raw_cursor_tokens_persisted") is not False or chain.get("credentials_persisted") is not False:
        raise ValueError("checkpoint chain must not contain raw cursor or credential storage")
    pages = chain.get("pages")
    if not isinstance(pages, list) or len(pages) > MAX_PAGINATION_PAGES:
        raise ValueError("checkpoint pages must be a bounded list")
    previous_chain = "0" * 64
    previous_next_hash = previous_next_ref = None
    seen = set()
    valid = True
    for index, page in enumerate(pages):
        if not isinstance(page, dict) or page.get("sequence") != index:
            valid = False
            break
        if index == 0:
            if page.get("cursor_sha256") is not None:
                valid = False
                break
        elif page.get("cursor_sha256") != previous_next_hash or page.get("cursor_reference_id") != previous_next_ref:
            valid = False
            break
        current = page.get("cursor_sha256")
        next_hash = page.get("next_cursor_sha256")
        if current is not None:
            if not isinstance(current, str) or not _SHA256.fullmatch(current) or current in seen:
                valid = False
                break
            seen.add(current)
        if next_hash is not None and (
            not isinstance(next_hash, str) or not _SHA256.fullmatch(next_hash) or next_hash in seen
        ):
            valid = False
            break
        event = {key: page.get(key) for key in (
            "sequence", "page_id", "provider", "cursor_sha256", "cursor_reference_id",
            "next_cursor_sha256", "next_cursor_reference_id", "item_ids", "captured_at",
        )}
        page_hash = _digest(event)
        chain_hash = _digest({"previous_chain_sha256": previous_chain, "page_sha256": page_hash})
        if page.get("page_sha256") != page_hash or page.get("chain_sha256") != chain_hash:
            valid = False
            break
        previous_chain = chain_hash
        previous_next_hash = next_hash
        previous_next_ref = page.get("next_cursor_reference_id")
    if chain.get("page_count") != len(pages) or chain.get("head_sha256") != previous_chain:
        valid = False
    return {
        "valid": valid,
        "verified_page_count": len(pages) if valid else index,
        "head_sha256": previous_chain,
        "raw_cursor_tokens_persisted": False,
        "tampering_detected": not valid,
    }


def assess_language_script_consistency(text: str, declared_language: str | None) -> dict:
    """Check script compatibility without pretending to identify the language."""
    value = _clean(text, "text", 20_000)
    if declared_language is not None:
        language = _clean(declared_language, "declared_language", 20).lower()
        if not _LANGUAGE_TAG.fullmatch(language):
            raise ValueError("declared_language must be a BCP-47-like tag")
        code = language.split("-", 1)[0]
    else:
        language, code = None, None
    profile = script_profile(value)
    counts = profile["script_counts"]
    letters = profile["letter_count"]
    kana_count = sum(
        1 for char in value
        if 0x3040 <= ord(char) <= 0x30FF or 0x31F0 <= ord(char) <= 0x31FF
    )
    expected = _SCRIPT_BY_LANGUAGE.get(code) if code else None
    flags = []
    status = "declared_language_not_checked"
    if not letters:
        status = "insufficient_script_evidence"
        flags.append("no_letters_detected")
    elif code is None:
        status = "language_not_declared"
    elif code in {"ja", "zh"}:
        cjk = counts.get("cjk", 0)
        if not cjk:
            status = "script_mismatch"
            flags.append("expected_cjk_script_not_detected")
        elif code == "ja" and kana_count == 0:
            status = "ambiguous_han_only_text"
            flags.append("japanese_and_chinese_cannot_be_distinguished_from_han_only_text")
        elif code == "zh" and kana_count:
            status = "script_mismatch"
            flags.append("japanese_kana_detected_in_chinese_declared_text")
        else:
            status = "script_compatible"
    elif expected is None:
        status = "language_script_rule_unavailable"
        flags.append("no_script_rule_for_declared_language")
    else:
        ratio = counts.get(expected, 0) / letters
        if ratio >= 0.5:
            status = "script_compatible"
        elif max(counts.values(), default=0) / letters >= 0.7:
            status = "script_mismatch"
            flags.append("dominant_script_conflicts_with_declared_language")
        else:
            status = "mixed_script_review"
            flags.append("mixed_script_composition")
    return {
        "declared_language": language,
        "script_counts": counts,
        "letter_count": letters,
        "expected_script": expected or ("cjk_with_kana_for_ja" if code == "ja" else "cjk_han_for_zh" if code == "zh" else None),
        "kana_count": kana_count,
        "status": status,
        "flags": flags,
        "language_identification_performed": False,
        "translation_performed": False,
        "scientific_evidence_established": False,
    }


def audit_headline_context(title: str, body: str, *, language: str | None = None) -> dict:
    """Surface multilingual headline/body tension as a human-review prompt."""
    headline = _clean(title, "title", 5_000)
    context = _clean(body, "body", 20_000, empty=True)
    title_triage = triage_title(headline, language)
    body_triage = triage_title(context, language) if context else {
        "matched_cues": [], "triage_level": "not_assessed",
    }
    title_cues = title_triage["matched_cues"]
    body_cues = body_triage["matched_cues"]
    title_tokens = set(tokenize(headline))
    body_tokens = set(tokenize(context)) if context else set()
    overlap = len(title_tokens & body_tokens) / len(title_tokens) if title_tokens else 0.0
    letters = [char for char in headline if char.isalpha()]
    uppercase_ratio = (
        sum(1 for char in letters if char.isupper()) / len(letters) if len(letters) >= 8 else 0.0
    )
    certainty = [cue for cue in _CERTAINTY_CUES if cue.casefold() in headline.casefold()]
    qualifiers = [cue for cue in _QUALIFIER_CUES if cue.casefold() in context.casefold()]
    reasons = []
    if title_cues and not body_cues:
        reasons.append("headline_sensationalism_cue_not_repeated_in_body")
    if len(title_cues) > len(body_cues) and body_cues:
        reasons.append("headline_has_more_sensationalism_cues_than_body")
    if uppercase_ratio >= 0.65:
        reasons.append("high_uppercase_ratio")
    if re.search(r"[!?！？]{2,}", headline):
        reasons.append("repeated_emphatic_punctuation")
    if certainty and qualifiers:
        reasons.append("headline_certainty_conflicts_with_body_qualification")
    if context and overlap < 0.15 and len(title_tokens) >= 4:
        reasons.append("low_lexical_overlap_requires_context_review")
    score = len(reasons)
    priority = "high_review_priority" if score >= 3 else "review_priority" if score else "no_extra_review_signal"
    return {
        "title_triage": title_triage,
        "body_triage": body_triage,
        "title_body_token_overlap": round(overlap, 4),
        "uppercase_ratio": round(uppercase_ratio, 4),
        "certainty_cues": certainty,
        "body_qualifier_cues": qualifiers,
        "reason_codes": reasons,
        "review_priority": priority,
        "clickbait_determined": False,
        "publisher_intent_determined": False,
        "truth_or_misleadingness_determined": False,
    }


def _timestamp_ms(value: str) -> int:
    match = re.fullmatch(r"(?:(\d{2,}):)?(\d{2}):(\d{2})[.,](\d{3})", value)
    if not match:
        raise ValueError("caption timestamp is malformed")
    hours = int(match.group(1) or 0)
    minutes, seconds, millis = int(match.group(2)), int(match.group(3)), int(match.group(4))
    if seconds > 59 or (match.group(1) is not None and minutes > 59):
        raise ValueError("caption timestamp has an out-of-range minute or second")
    return ((hours * 60 + minutes) * 60 + seconds) * 1000 + millis


def parse_caption_transcript(
    payload: str | bytes,
    *,
    format_hint: str | None = None,
    language: str | None = None,
) -> dict:
    """Parse supplied WebVTT or SRT cues with bounded time and source offsets."""
    if isinstance(payload, bytes):
        if len(payload) > MAX_TRANSCRIPT_BYTES:
            raise ValueError("transcript exceeds the 2 MiB byte limit")
        try:
            original = payload.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ValueError("transcript must be UTF-8") from exc
    elif isinstance(payload, str):
        original = payload
        if len(original.encode("utf-8")) > MAX_TRANSCRIPT_BYTES:
            raise ValueError("transcript exceeds the 2 MiB byte limit")
    else:
        raise ValueError("transcript must be UTF-8 text or bytes")
    if language is not None:
        language = _clean(language, "language", 20).lower()
        if not _LANGUAGE_TAG.fullmatch(language):
            raise ValueError("language must be a BCP-47-like tag")
    if format_hint is None:
        kind = "vtt" if original.lstrip().startswith("WEBVTT") else "srt"
    else:
        kind = _clean(format_hint, "format_hint", 8).lower()
    if kind not in {"vtt", "srt"}:
        raise ValueError("format_hint must be vtt or srt")
    blocks = re.split(r"\r?\n[ \t]*\r?\n", original.strip())
    cues, cue_ids = [], set()
    previous_start = -1
    previous_end = -1
    total_chars = 0
    search_offset = 0
    for block in blocks:
        block_start = original.find(block, search_offset)
        if block_start < 0:
            block_start = search_offset
        search_offset = block_start + len(block)
        lines = block.splitlines(keepends=True)
        if not lines:
            continue
        header_prefix = 0
        if lines[0].lstrip("\ufeff").startswith("WEBVTT"):
            header_prefix = len(lines[0])
            lines = lines[1:]
            if not lines:
                continue
        first = "".join(lines).lstrip()
        if first.startswith(("NOTE", "STYLE", "REGION")):
            continue
        time_index = next((i for i, line in enumerate(lines[:3]) if _TIMESTAMP.match(line.strip())), None)
        if time_index is None:
            if not first.strip():
                continue
            raise ValueError("caption block has no valid timing line")
        timing = _TIMESTAMP.match(lines[time_index].strip())
        assert timing is not None
        start_ms = _timestamp_ms(timing.group("start"))
        end_ms = _timestamp_ms(timing.group("end"))
        if end_ms <= start_ms:
            raise ValueError("caption cue end must be after its start")
        if start_ms < previous_start:
            raise ValueError("caption cues must be ordered by start time")
        cue_id = (
            lines[time_index - 1].strip()
            if time_index > 0 else f"cue-{len(cues) + 1:05d}"
        )
        cue_id = _clean(cue_id, "cue_id", 200)
        if cue_id in cue_ids:
            raise ValueError("caption cue IDs must be unique")
        cue_ids.add(cue_id)
        body_lines = lines[time_index + 1:]
        raw_body = "".join(body_lines)
        left_trim = len(raw_body) - len(raw_body.lstrip())
        right_trim = len(raw_body.rstrip())
        if right_trim <= left_trim:
            raise ValueError("caption cue text must not be empty")
        cue_text = raw_body[left_trim:right_trim]
        if len(cue_text) > 20_000:
            raise ValueError("caption cue exceeds 20000 characters")
        body_start = block_start + header_prefix + sum(len(line) for line in lines[:time_index + 1])
        cue_start, cue_end = body_start + left_trim, body_start + right_trim
        total_chars += len(cue_text)
        if total_chars > MAX_TRANSCRIPT_TEXT_CHARS:
            raise ValueError("transcript cue text exceeds the 1 MiB character budget")
        overlap = start_ms < previous_end
        cues.append({
            "cue_id": cue_id,
            "start_ms": start_ms,
            "end_ms": end_ms,
            "text": cue_text,
            "start_char": cue_start,
            "end_char": cue_end,
            "text_sha256": hashlib.sha256(cue_text.encode("utf-8")).hexdigest(),
            "overlaps_previous_cue": overlap,
        })
        previous_start, previous_end = start_ms, max(previous_end, end_ms)
        if len(cues) > MAX_TRANSCRIPT_CUES:
            raise ValueError("transcript exceeds the 5000-cue limit")
    return {
        "schema_version": SCHEMA_VERSION,
        "format": kind,
        "language": language,
        "cue_count": len(cues),
        "cues": cues,
        "overlap_count": sum(1 for cue in cues if cue["overlaps_previous_cue"]),
        "cue_offsets_use_unicode_code_points": True,
        "transcript_fetched": False,
        "media_downloaded": False,
        "transcript_completeness_verified": False,
        "transcript_accuracy_verified": False,
    }


def bind_claim_candidates_to_source(
    source_record: dict,
    source_text: str,
    *,
    candidates: dict | list[dict] | None = None,
    transcript_cues: list[dict] | None = None,
    language: str | None = None,
    translation_reference: dict | None = None,
) -> dict:
    """Bind sentence spans to an immutable source snapshot and optional cue IDs."""
    if not isinstance(source_record, dict):
        raise ValueError("source_record must be an object")
    source_id = _clean(source_record.get("source_id"), "source_id", 300)
    snapshot_hash = _sha(source_record.get("snapshot_sha256"), "snapshot_sha256")
    original = _clean(source_text, "source_text", 20_000)
    if language is not None:
        language = _clean(language, "language", 20).lower()
        if not _LANGUAGE_TAG.fullmatch(language):
            raise ValueError("language must be a BCP-47-like tag")
    if candidates is None:
        candidate_rows = extract_claim_candidates(original)["candidates"]
    elif isinstance(candidates, dict):
        candidate_rows = candidates.get("candidates")
    else:
        candidate_rows = candidates
    if not isinstance(candidate_rows, list) or len(candidate_rows) > 200:
        raise ValueError("candidates must be a list of at most 200 spans")
    cues = transcript_cues or []
    if not isinstance(cues, list) or len(cues) > MAX_TRANSCRIPT_CUES:
        raise ValueError("transcript_cues must be a bounded list")
    cue_rows = []
    for cue in cues:
        if not isinstance(cue, dict):
            raise ValueError("each transcript cue must be an object")
        cue_id = _clean(cue.get("cue_id"), "cue_id", 200)
        start, end = cue.get("start_char"), cue.get("end_char")
        if (
            isinstance(start, bool) or not isinstance(start, int)
            or isinstance(end, bool) or not isinstance(end, int)
            or not 0 <= start < end <= len(original)
            or original[start:end] != cue.get("text")
        ):
            raise ValueError("transcript cue offsets must resolve to exact source text")
        cue_rows.append((cue_id, start, end))
    if len({item[0] for item in cue_rows}) != len(cue_rows):
        raise ValueError("transcript cue IDs must be unique")
    translation = None
    if translation_reference is not None:
        if not isinstance(translation_reference, dict):
            raise ValueError("translation_reference must be an object")
        translation = {
            "original_sha256": _sha(translation_reference.get("original_sha256"), "translation original hash"),
            "translated_sha256": _sha(translation_reference.get("translated_sha256"), "translation translated hash"),
            "source_language": _clean(translation_reference.get("source_language"), "source language", 20),
            "target_language": _clean(translation_reference.get("target_language"), "target language", 20),
            "translation_replaces_original": False,
        }
    claims, seen_ids = [], set()
    for candidate in candidate_rows:
        if not isinstance(candidate, dict):
            raise ValueError("each claim candidate must be an object")
        start, end = candidate.get("start_char"), candidate.get("end_char")
        text = candidate.get("text")
        if (
            isinstance(start, bool) or not isinstance(start, int)
            or isinstance(end, bool) or not isinstance(end, int)
            or not 0 <= start < end <= len(original)
            or not isinstance(text, str) or original[start:end] != text
        ):
            raise ValueError("claim candidate offsets must resolve to exact source text")
        claim_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        claim_id = _digest({
            "source_id": source_id, "snapshot_sha256": snapshot_hash,
            "start_char": start, "end_char": end, "claim_text_sha256": claim_hash,
        })[:24]
        if claim_id in seen_ids:
            raise ValueError("claim candidate spans must be unique")
        seen_ids.add(claim_id)
        linked_cues = sorted(
            cue_id for cue_id, cue_start, cue_end in cue_rows
            if start < cue_end and end > cue_start
        )
        claims.append({
            "claim_id": claim_id,
            "source_id": source_id,
            "source_snapshot_sha256": snapshot_hash,
            "start_char": start,
            "end_char": end,
            "claim_text": text,
            "claim_text_sha256": claim_hash,
            "transcript_cue_ids": linked_cues,
            "language": language,
            "translation_reference": translation,
            "verification_state": "unverified_candidate",
            "scientific_evidence_established": False,
        })
    return {
        "schema_version": SCHEMA_VERSION,
        "source_id": source_id,
        "source_snapshot_sha256": snapshot_hash,
        "claim_count": len(claims),
        "claims": claims,
        "offsets_use_unicode_code_points": True,
        "automatic_claim_verification": False,
        "translation_replaces_original": False,
    }


def build_publisher_status_ledger(events: list[dict]) -> dict:
    """Append explicit publisher-declared correction/retraction events to a hash chain."""
    allowed = {"corrected", "retracted", "updated", "removed", "restored"}
    if not isinstance(events, list) or len(events) > MAX_LEDGER_EVENTS:
        raise ValueError("events must be a list of at most 500 entries")
    output, seen, latest, previous_hash = [], set(), {}, "0" * 64
    last_time: dict[str, datetime] = {}
    for index, item in enumerate(events):
        if not isinstance(item, dict):
            raise ValueError("each publisher event must be an object")
        event_id = _clean(item.get("event_id"), "event_id", 200)
        source_id = _clean(item.get("source_id"), "source_id", 300)
        event_type = _clean(item.get("event_type"), "event_type", 40).lower()
        if event_type not in allowed:
            raise ValueError("unsupported publisher event_type")
        if event_id in seen:
            raise ValueError("publisher event IDs must be unique")
        seen.add(event_id)
        if item.get("publisher_declared") is not True:
            raise ValueError("status events must be explicitly publisher-declared")
        prior_hash = _sha(item.get("prior_snapshot_sha256"), "prior_snapshot_sha256")
        new_hash = item.get("new_snapshot_sha256")
        if new_hash is not None:
            new_hash = _sha(new_hash, "new_snapshot_sha256")
        if event_type in {"corrected", "updated", "restored"} and new_hash is None:
            raise ValueError("corrected, updated and restored events require a new snapshot hash")
        if event_type in {"retracted", "removed"} and new_hash is not None:
            raise ValueError("retracted and removed events must not invent a replacement snapshot")
        if source_id in latest and latest[source_id] != prior_hash:
            raise ValueError("publisher event prior snapshot does not match the preceding event")
        occurred = _clean(item.get("occurred_at"), "occurred_at", 64)
        try:
            parsed = datetime.fromisoformat(occurred.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("occurred_at must be timezone-aware ISO 8601") from exc
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("occurred_at must include a timezone")
        parsed = parsed.astimezone(timezone.utc)
        if source_id in last_time and parsed < last_time[source_id]:
            raise ValueError("publisher events must be chronological per source")
        last_time[source_id] = parsed
        ref_host, reference = _host_from_url(item.get("publisher_reference_url"), "publisher_reference_url")
        statement = _clean(item.get("publisher_statement"), "publisher_statement", 2_000)
        event = {
            "sequence": index,
            "event_id": event_id,
            "source_id": source_id,
            "event_type": event_type,
            "occurred_at": parsed.isoformat(),
            "prior_snapshot_sha256": prior_hash,
            "new_snapshot_sha256": new_hash,
            "publisher_reference_url": reference,
            "publisher_reference_host": ref_host,
            "publisher_statement": statement,
            "publisher_declared": True,
            "prior_source_version_preserved": True,
        }
        event_hash = _digest(event)
        chain_hash = _digest({"previous_event_sha256": previous_hash, "event_sha256": event_hash})
        output.append({**event, "event_sha256": event_hash, "chain_sha256": chain_hash})
        previous_hash = chain_hash
        latest[source_id] = new_hash if new_hash is not None else prior_hash
    return {
        "schema_version": SCHEMA_VERSION,
        "event_count": len(output),
        "events": output,
        "head_sha256": previous_hash,
        "source_records_deleted": False,
        "scientific_truth_adjudicated": False,
    }


def verify_publisher_status_ledger(ledger: dict) -> dict:
    if not isinstance(ledger, dict) or ledger.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported publisher status ledger")
    events = ledger.get("events")
    if not isinstance(events, list) or len(events) > MAX_LEDGER_EVENTS:
        raise ValueError("ledger events must be a bounded list")
    previous_hash = "0" * 64
    valid = True
    for index, item in enumerate(events):
        if not isinstance(item, dict) or item.get("sequence") != index:
            valid = False
            break
        event = {key: item.get(key) for key in (
            "sequence", "event_id", "source_id", "event_type", "occurred_at",
            "prior_snapshot_sha256", "new_snapshot_sha256", "publisher_reference_url",
            "publisher_reference_host", "publisher_statement", "publisher_declared",
            "prior_source_version_preserved",
        )}
        event_hash = _digest(event)
        chain_hash = _digest({"previous_event_sha256": previous_hash, "event_sha256": event_hash})
        if item.get("event_sha256") != event_hash or item.get("chain_sha256") != chain_hash:
            valid = False
            break
        previous_hash = chain_hash
    valid = valid and ledger.get("event_count") == len(events) and ledger.get("head_sha256") == previous_hash
    return {
        "valid": valid,
        "verified_event_count": len(events) if valid else index,
        "head_sha256": previous_hash,
        "source_records_deleted": False,
        "tampering_detected": not valid,
    }


_PRIVACY_PATTERNS = (
    ("email", re.compile(r"(?<![\w.+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?![\w.-])", re.I)),
    ("credential", re.compile(r"(?i)\b(?:bearer\s+[A-Za-z0-9._~+/=-]{12,}|(?:ghp|github_pat|sk|xox[baprs])_[A-Za-z0-9_-]{12,})\b")),
    ("ipv4", re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")),
    ("coordinates", re.compile(r"(?<![\d.])[-+]?\d{1,2}\.\d{4,}\s*[,;/]\s*[-+]?\d{1,3}\.\d{4,}(?![\d.])")),
    ("phone_like", re.compile(r"(?<!\w)\+?\d[\d\s().-]{7,}\d(?!\w)")),
)


def scan_public_text_privacy(text: str, *, include_redacted_preview: bool = True) -> dict:
    """Find common identifiers without returning matched values or mutating input."""
    original = _clean(text, "text", MAX_PRIVACY_TEXT_CHARS, empty=True)
    matches = []
    for category, pattern in _PRIVACY_PATTERNS:
        for found in pattern.finditer(original):
            value = found.group(0)
            if category == "ipv4":
                try:
                    ipaddress.ip_address(value)
                except ValueError:
                    continue
            if category == "phone_like" and sum(char.isdigit() for char in value) < 9:
                continue
            matches.append({
                "category": category,
                "start_char": found.start(),
                "end_char": found.end(),
                "matched_value_sha256": hashlib.sha256(value.encode("utf-8")).hexdigest(),
            })
    matches.sort(key=lambda item: (item["start_char"], item["end_char"], item["category"]))
    preview = None
    if include_redacted_preview:
        pieces, cursor = [], 0
        for item in matches:
            if item["start_char"] < cursor:
                continue
            pieces.append(original[cursor:item["start_char"]])
            pieces.append(f"[REDACTED:{item['category']}]")
            cursor = item["end_char"]
        pieces.append(original[cursor:])
        preview = "".join(pieces)
    return {
        "character_count": len(original),
        "finding_count": len(matches),
        "findings": matches,
        "redacted_preview": preview,
        "matched_values_echoed": False,
        "input_mutated": False,
        "automatic_storage_or_deletion": False,
        "limitations": [
            "Pattern screening is incomplete and can produce false positives.",
            "A clean scan is not proof that text contains no personal or confidential information.",
        ],
    }


def _packet_text(value: object, field: str, maximum: int = 20_000) -> tuple[str, dict]:
    text = _clean(value, field, maximum, empty=True)
    privacy = scan_public_text_privacy(text)
    if privacy["finding_count"]:
        return privacy["redacted_preview"], privacy
    return text, privacy


def build_human_review_packet(
    records: list[dict],
    *,
    claim_bindings: list[dict] | None = None,
    transcript_cues: list[dict] | None = None,
    translation_reviews: list[dict] | None = None,
    language_audits: list[dict] | None = None,
    publisher_status_ledger: dict | None = None,
    review_queue: dict | None = None,
    max_bytes: int = MAX_REVIEW_PACKET_BYTES,
) -> dict:
    """Build a deterministic, privacy-screened, bounded human-review export."""
    if not isinstance(records, list) or len(records) > 500:
        raise ValueError("records must be a list of at most 500 normalized records")
    if isinstance(max_bytes, bool) or not isinstance(max_bytes, int) or not 1_000 <= max_bytes <= MAX_REVIEW_PACKET_BYTES:
        raise ValueError("max_bytes must be between 1000 and 5 MiB")
    claim_bindings = [] if claim_bindings is None else claim_bindings
    transcript_cues = [] if transcript_cues is None else transcript_cues
    translation_reviews = [] if translation_reviews is None else translation_reviews
    language_audits = [] if language_audits is None else language_audits
    for name, rows, maximum in (
        ("claim_bindings", claim_bindings, 1_000),
        ("transcript_cues", transcript_cues, MAX_TRANSCRIPT_CUES),
        ("translation_reviews", translation_reviews, 500),
        ("language_audits", language_audits, 500),
    ):
        if not isinstance(rows, list) or len(rows) > maximum:
            raise ValueError(f"{name} must be a bounded list")

    source_map = {}
    safe_records = []
    privacy_counts = {"records_scanned": 0, "findings": 0, "fields_redacted": 0}
    top_level_allowlist = {
        "schema_version", "source_id", "platform", "content_type", "visibility",
        "access_mode", "source_url", "published_at", "captured_at",
        "discarded_field_names", "sensitive_field_names_flagged",
        "private_content_accessed", "media_downloaded", "terms_of_service_bypass",
        "scientific_evidence_established", "discovery_only", "snapshot_sha256",
        "content_sha256",
    }
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("every record must be an object")
        source_id = _clean(record.get("source_id"), "source_id", 300)
        snapshot = _sha(record.get("snapshot_sha256"), "snapshot_sha256")
        platform = _clean(record.get("platform"), "platform", 40).lower()
        if platform not in CHANNEL_FIELDS:
            raise ValueError("review packet contains an unsupported platform")
        if source_id in source_map:
            raise ValueError("source IDs must be unique in a review packet")
        source_map[source_id] = snapshot
        safe = {key: value for key, value in record.items() if key in top_level_allowlist}
        source_url = safe.get("source_url")
        if isinstance(source_url, str):
            _, _ = _host_from_url(source_url, "source_url")
            parts = urlsplit(source_url)
            safe["source_url"] = urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
            safe["source_url_query_removed"] = bool(parts.query or parts.fragment)

        metadata = record.get("metadata", {})
        if not isinstance(metadata, dict):
            raise ValueError("record metadata must be an object")
        safe_metadata = {}
        redacted_fields = []
        for key, value in sorted(metadata.items()):
            if key not in CHANNEL_FIELDS[platform] or key == "author_display_name":
                continue
            if key == "public_permalink" and isinstance(value, str):
                _, _ = _host_from_url(value, "metadata.public_permalink")
                parts = urlsplit(value)
                value = urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
                if parts.query or parts.fragment:
                    redacted_fields.append(key + ":tracking_query_removed")
            if isinstance(value, str):
                preview, report = _packet_text(value, f"metadata.{key}", 5_000)
                privacy_counts["records_scanned"] += 1
                privacy_counts["findings"] += report["finding_count"]
                privacy_counts["fields_redacted"] += int(bool(report["finding_count"]))
                if report["finding_count"]:
                    redacted_fields.append(key)
                safe_metadata[key] = preview
            elif isinstance(value, list):
                safe_values = []
                for entry in value[:50]:
                    if isinstance(entry, str):
                        preview, report = _packet_text(entry, f"metadata.{key}", 200)
                        privacy_counts["records_scanned"] += 1
                        privacy_counts["findings"] += report["finding_count"]
                        privacy_counts["fields_redacted"] += int(bool(report["finding_count"]))
                        if report["finding_count"]:
                            redacted_fields.append(key)
                        safe_values.append(preview)
                safe_metadata[key] = safe_values
            elif isinstance(value, (int, float, bool)) or value is None:
                safe_metadata[key] = value
        safe["metadata"] = safe_metadata
        safe["packet_redacted_fields"] = sorted(set(redacted_fields))
        safe_records.append(safe)

    safe_claims = []
    for item in claim_bindings:
        if not isinstance(item, dict):
            raise ValueError("claim bindings must be objects")
        source_id = _clean(item.get("source_id"), "claim source_id", 300)
        if source_id not in source_map or item.get("source_snapshot_sha256") != source_map[source_id]:
            raise ValueError("claim binding does not resolve to the current source snapshot")
        raw_text = _clean(item.get("claim_text", ""), "claim_text", 20_000, empty=True)
        claim_hash = _sha(item.get("claim_text_sha256"), "claim_text_sha256")
        if hashlib.sha256(raw_text.encode("utf-8")).hexdigest() != claim_hash:
            raise ValueError("claim text does not match its retained source hash")
        claim_text, report = _packet_text(raw_text, "claim_text")
        privacy_counts["findings"] += report["finding_count"]
        privacy_counts["fields_redacted"] += int(bool(report["finding_count"]))
        start, end = item.get("start_char"), item.get("end_char")
        if (
            isinstance(start, bool) or not isinstance(start, int)
            or isinstance(end, bool) or not isinstance(end, int)
            or not 0 <= start < end
        ):
            raise ValueError("claim offsets must be positive integer spans")
        cue_ids = item.get("transcript_cue_ids", [])
        if not isinstance(cue_ids, list) or any(not isinstance(value, str) for value in cue_ids):
            raise ValueError("transcript_cue_ids must be a list of strings")
        safe_claims.append({
            "claim_id": _clean(item.get("claim_id"), "claim_id", 100),
            "source_id": source_id,
            "source_snapshot_sha256": source_map[source_id],
            "start_char": start,
            "end_char": end,
            "claim_text": claim_text,
            "claim_text_sha256": claim_hash,
            "claim_text_redacted_for_packet": bool(report["finding_count"]),
            "transcript_cue_ids": sorted(set(cue_ids)),
            "language": item.get("language"),
            "verification_state": "unverified_candidate",
        })

    safe_cues = []
    for item in transcript_cues:
        if not isinstance(item, dict):
            raise ValueError("transcript cues must be objects")
        source_id = _clean(item.get("source_id"), "cue source_id", 300)
        if source_id not in source_map:
            raise ValueError("transcript cue source does not exist in this packet")
        raw_text = _clean(item.get("text", ""), "cue text", 20_000)
        cue_hash = _sha(item.get("text_sha256"), "cue text_sha256")
        if hashlib.sha256(raw_text.encode("utf-8")).hexdigest() != cue_hash:
            raise ValueError("transcript cue text does not match its retained hash")
        cue_text, report = _packet_text(raw_text, "cue text")
        privacy_counts["findings"] += report["finding_count"]
        privacy_counts["fields_redacted"] += int(bool(report["finding_count"]))
        start_ms, end_ms = item.get("start_ms"), item.get("end_ms")
        if (
            isinstance(start_ms, bool) or not isinstance(start_ms, int)
            or isinstance(end_ms, bool) or not isinstance(end_ms, int)
            or start_ms < 0 or end_ms <= start_ms
        ):
            raise ValueError("transcript cue times must be valid non-negative millisecond spans")
        safe_cues.append({
            "source_id": source_id,
            "cue_id": _clean(item.get("cue_id"), "cue_id", 200),
            "start_ms": start_ms,
            "end_ms": end_ms,
            "text": cue_text,
            "text_sha256": cue_hash,
            "text_redacted_for_packet": bool(report["finding_count"]),
            "start_char": item.get("start_char"),
            "end_char": item.get("end_char"),
        })

    safe_translations = []
    for item in translation_reviews:
        if not isinstance(item, dict):
            raise ValueError("translation reviews must be objects")
        record_id = _clean(item.get("record_id"), "translation record_id", 300)
        if record_id not in source_map:
            raise ValueError("translation review source does not exist in this packet")
        raw_original = _clean(item.get("original_text", ""), "original translation text", 20_000)
        raw_translated = _clean(item.get("translated_text", ""), "translated text", 20_000)
        original_hash = _sha(item.get("original_sha256"), "original_sha256")
        translated_hash = _sha(item.get("translated_sha256"), "translated_sha256")
        if hashlib.sha256(raw_original.encode("utf-8")).hexdigest() != original_hash:
            raise ValueError("original translation text does not match its retained hash")
        if hashlib.sha256(raw_translated.encode("utf-8")).hexdigest() != translated_hash:
            raise ValueError("translated text does not match its retained hash")
        original, original_report = _packet_text(raw_original, "original translation text")
        translated, translated_report = _packet_text(raw_translated, "translated text")
        privacy_counts["findings"] += original_report["finding_count"] + translated_report["finding_count"]
        privacy_counts["fields_redacted"] += int(bool(original_report["finding_count"])) + int(bool(translated_report["finding_count"]))
        safe_translations.append({
            "record_id": record_id,
            "source_language": item.get("source_language"),
            "target_language": item.get("target_language"),
            "original_text": original,
            "translated_text": translated,
            "original_sha256": original_hash,
            "translated_sha256": translated_hash,
            "text_redacted_for_packet": bool(original_report["finding_count"] or translated_report["finding_count"]),
            "review_state": item.get("review_state"),
            "reviewer_attested": bool(item.get("reviewer_attested")),
            "translation_accuracy_established": False,
        })

    safe_languages = []
    for item in language_audits:
        if not isinstance(item, dict):
            raise ValueError("language audits must be objects")
        source_id = _clean(item.get("source_id"), "language audit source_id", 300)
        if source_id not in source_map:
            raise ValueError("language audit source does not exist in this packet")
        script_counts = item.get("script_counts", {})
        flags = item.get("flags", [])
        if (
            not isinstance(script_counts, dict)
            or any(not isinstance(key, str) or isinstance(value, bool) or not isinstance(value, int) or value < 0 for key, value in script_counts.items())
            or not isinstance(flags, list) or any(not isinstance(flag, str) for flag in flags)
        ):
            raise ValueError("language audit script counts or flags are invalid")
        declared_language = item.get("declared_language")
        if declared_language is not None:
            declared_language = _clean(declared_language, "declared language", 20).lower()
            if not _LANGUAGE_TAG.fullmatch(declared_language):
                raise ValueError("declared language must be a BCP-47-like tag")
        status = _clean(item.get("status"), "language audit status", 60)
        if status not in {
            "declared_language_not_checked", "insufficient_script_evidence",
            "language_not_declared", "script_compatible", "ambiguous_han_only_text",
            "script_mismatch", "language_script_rule_unavailable", "mixed_script_review",
        }:
            raise ValueError("language audit status is unsupported")
        if any(not re.fullmatch(r"[a-z0-9_]{1,80}", flag) for flag in flags):
            raise ValueError("language audit flags must be reason-code tokens")
        if any(not re.fullmatch(r"[a-z_]{1,40}", key) for key in script_counts):
            raise ValueError("script count keys must be identifiers")
        safe_languages.append({
            "source_id": source_id,
            "declared_language": declared_language,
            "status": status,
            "script_counts": dict(sorted(script_counts.items())),
            "flags": sorted(set(flags)),
            "language_identification_performed": False,
        })

    ledger = publisher_status_ledger or {
        "schema_version": SCHEMA_VERSION, "event_count": 0, "events": [], "head_sha256": "0" * 64,
    }
    if not isinstance(ledger, dict) or not verify_publisher_status_ledger(ledger)["valid"]:
        raise ValueError("publisher_status_ledger must be a valid hash chain")
    ledger_sources = {item.get("source_id") for item in ledger["events"]}
    if not ledger_sources.issubset(source_map):
        raise ValueError("publisher status ledger contains unknown source IDs")
    safe_events, packet_previous = [], "0" * 64
    for item in ledger["events"]:
        statement, report = _packet_text(item["publisher_statement"], "publisher statement", 2_000)
        privacy_counts["findings"] += report["finding_count"]
        privacy_counts["fields_redacted"] += int(bool(report["finding_count"]))
        safe_event = {
            key: value for key, value in item.items()
            if key not in {"event_sha256", "chain_sha256", "publisher_statement"}
        }
        safe_event["publisher_statement"] = statement
        safe_event["publisher_statement_redacted_for_packet"] = bool(report["finding_count"])
        if isinstance(safe_event.get("publisher_reference_url"), str):
            _, _ = _host_from_url(safe_event["publisher_reference_url"], "publisher reference URL")
            parts = urlsplit(safe_event["publisher_reference_url"])
            safe_event["publisher_reference_url"] = urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
        safe_event["source_event_sha256"] = item["event_sha256"]
        safe_event["source_chain_sha256"] = item["chain_sha256"]
        packet_event_hash = _digest(safe_event)
        packet_chain_hash = _digest({
            "previous_event_sha256": packet_previous,
            "event_sha256": packet_event_hash,
        })
        safe_event["packet_event_sha256"] = packet_event_hash
        safe_event["packet_chain_sha256"] = packet_chain_hash
        safe_events.append(safe_event)
        packet_previous = packet_chain_hash

    safe_queue = None
    if review_queue is not None:
        if not isinstance(review_queue, dict) or not isinstance(review_queue.get("items", []), list):
            raise ValueError("review_queue must contain an items list")
        queue_items = review_queue.get("items", [])
        if len(queue_items) > 500:
            raise ValueError("review_queue exceeds 500 items")
        safe_queue_items = []
        seen_queue_ids = set()
        for item in queue_items:
            if not isinstance(item, dict):
                raise ValueError("review queue entries must be objects")
            record_id = _clean(item.get("record_id"), "review queue record_id", 300)
            if record_id not in source_map:
                raise ValueError("review queue contains an unknown source ID")
            if record_id in seen_queue_ids:
                raise ValueError("review queue source IDs must be unique")
            seen_queue_ids.add(record_id)
            reasons = item.get("reason_codes", [])
            if not isinstance(reasons, list) or any(
                not isinstance(reason, str) or not re.fullmatch(r"[a-z0-9_]{1,80}", reason)
                for reason in reasons
            ):
                raise ValueError("review queue reason_codes must be reason-code tokens")
            priority = _clean(item.get("priority", "unranked"), "review priority", 40)
            if priority not in {"critical", "high", "medium", "low", "unranked"}:
                raise ValueError("review priority is unsupported")
            candidate_count = item.get("claim_candidate_count", 0)
            if (
                isinstance(candidate_count, bool) or not isinstance(candidate_count, int)
                or not 0 <= candidate_count <= 200
            ):
                raise ValueError("claim_candidate_count must be between 0 and 200")
            safe_queue_items.append({
                "record_id": record_id,
                "priority": priority,
                "reason_codes": sorted(set(reasons)),
                "claim_candidate_count": candidate_count,
            })
        safe_queue = {
            "items": sorted(safe_queue_items, key=lambda item: (item["priority"], item["record_id"])),
            "item_count": len(safe_queue_items),
            "automatic_adjudication": False,
        }

    payload = {
        "schema_version": SCHEMA_VERSION,
        "packet_type": "public_media_human_review",
        "records": sorted(safe_records, key=lambda item: item["source_id"]),
        "claim_bindings": sorted(safe_claims, key=lambda item: (item["source_id"], item["claim_id"])),
        "transcript_cues": sorted(safe_cues, key=lambda item: (item["source_id"], item["start_ms"], item["cue_id"])),
        "translation_reviews": sorted(safe_translations, key=lambda item: item["record_id"]),
        "language_audits": sorted(safe_languages, key=lambda item: item["source_id"]),
        "publisher_status_events": safe_events,
        "source_ledger_head_sha256": ledger["head_sha256"],
        "source_ledger_verified": True,
        "packet_event_chain_head_sha256": packet_previous,
        "review_queue": safe_queue,
        "privacy_screening": privacy_counts,
        "omissions": {
            "media_bytes": "not collected",
            "private_content": "not accessed",
            "raw_cursor_tokens": "not retained",
            "unapproved_fields": "not copied",
            "author_display_names": "omitted from export",
        },
        "scientific_evidence_established": False,
        "automatic_adjudication": False,
        "byte_budget": max_bytes,
        "raw_media_included": False,
        "private_content_accessed": False,
        "deterministic_for_identical_inputs": True,
        "canonical_bytes": 0,
    }
    payload["manifest_sha256"] = _digest({
        key: value for key, value in payload.items()
        if key not in {"manifest_sha256", "canonical_bytes"}
    })
    for _ in range(4):
        measured = len(_canonical(payload))
        if measured == payload["canonical_bytes"]:
            break
        payload["canonical_bytes"] = measured
    if payload["canonical_bytes"] > max_bytes:
        raise ValueError("review packet exceeds its configured serialized-byte budget")
    return payload


__all__ = [
    "SCHEMA_VERSION", "parse_public_feed", "audit_adapter_contract",
    "build_pagination_checkpoint_chain", "verify_pagination_checkpoint_chain",
    "assess_language_script_consistency", "audit_headline_context",
    "parse_caption_transcript", "bind_claim_candidates_to_source",
    "build_publisher_status_ledger", "verify_publisher_status_ledger",
    "scan_public_text_privacy", "build_human_review_packet",
]

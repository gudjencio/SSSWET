"""Bounded, provenance-preserving workbench for permitted public science-media discovery.

This module composes existing SSSWET normalization and multilingual triage.
It does not fetch pages, download media, authenticate, or adjudicate truth.
"""
from __future__ import annotations

import hashlib
import ipaddress
import json
import re
import unicodedata
from collections import defaultdict
from datetime import datetime
from urllib.parse import urlsplit

from ssswet_core.multilingual_research_triage import tokenize, triage_title
from ssswet_core.public_media_ingestion import normalize_public_record

SCHEMA_VERSION = 1
POLICY_VERSION = "public-media-review-1"
MAX_INPUT_RECORDS = 1_000
MAX_RECORDS = 500
MAX_TEXT_CHARS = 20_000
MAX_CLAIM_CANDIDATES = 200
MAX_QUEUE_ITEMS = 500
MAX_AUDIT_EVENTS = 1_000
MAX_TOTAL_TEXT_CHARS = 2_000_000
MAX_SERIALIZED_BYTES = 5_000_000
_ZERO_HASH = "0" * 64

_PLATFORM_HOSTS = {
    "youtube": {"youtube.com", "youtu.be", "youtube-nocookie.com"},
    "x": {"x.com", "twitter.com", "t.co"},
    "instagram": {"instagram.com"},
    "facebook": {"facebook.com", "fb.watch"},
    "threads": {"threads.net"},
    "bluesky": {"bsky.app"},
    "reddit": {"reddit.com", "redd.it"},
    "snapchat": {"snapchat.com"},
    "mewe": {"mewe.com"},
    "weibo": {"weibo.com", "weibo.cn"},
    "bilibili": {"bilibili.com", "b23.tv"},
    "niconico": {"nicovideo.jp", "niconico.jp"},
    "qiita": {"qiita.com"},
    "web_forum": set(),
}
_TEXT_FIELDS = ("text", "caption", "title", "description")
_LANGUAGE_TAG = re.compile(r"^[a-z]{2,3}(?:-[a-z0-9]{2,8})*$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_CAUSAL_CUES = (
    "because", "causes", "caused", "leads to", "results in", "therefore",
    "demonstrates", "proves", "due to", "causal", "significant increase",
    "significant decrease", "prouve", "provoque", "entraîne", "en raison de",
    "原因", "によって", "証明", "引き起こす", "結果として",
)
_COMPARISON_CUES = (
    "compared with", "compared to", "higher than", "lower than",
    "more effective", "less effective", "versus", "vs.", "compared",
    "比較して", "より高い", "より低い", "対して",
)


def _canonical_bytes(value: object) -> bytes:
    try:
        return json.dumps(
            value, ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("value must be bounded, finite and JSON serializable") from exc


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _text(value: object, field: str, maximum: int, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or len(value) > maximum:
        raise ValueError(f"{field} must be text of at most {maximum} characters")
    cleaned = value.strip()
    if not cleaned and not allow_empty:
        raise ValueError(f"{field} must not be empty")
    return cleaned


def _identifier(value: object, field: str, maximum: int = 200) -> str:
    result = _text(value, field, maximum)
    if any(ord(char) < 32 for char in result):
        raise ValueError(f"{field} contains control characters")
    return result


def _normalize_host(value: object, field: str) -> str:
    host = _text(value, field, 253).lower().rstrip(".")
    if "://" in host or "/" in host or "@" in host or ":" in host:
        raise ValueError(f"{field} must be a hostname, not a URL")
    try:
        ipaddress.ip_address(host.strip("[]"))
    except ValueError:
        pass
    else:
        raise ValueError(f"{field} must not be an IP literal")
    try:
        normalized = host.encode("idna").decode("ascii")
    except UnicodeError as exc:
        raise ValueError(f"{field} is not a valid IDNA hostname") from exc
    if not normalized or "." not in normalized:
        raise ValueError(f"{field} must be a fully qualified hostname")
    return normalized.removeprefix("www.")


def _https_host(value: object, field: str) -> str:
    url = _text(value, field, 2_000)
    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError as exc:
        raise ValueError(f"{field} is not a valid URL") from exc
    if parts.scheme.lower() != "https" or not parts.hostname:
        raise ValueError(f"{field} must be an absolute HTTPS URL")
    if parts.username or parts.password:
        raise ValueError(f"{field} must not contain embedded credentials")
    if port not in (None, 443):
        raise ValueError(f"{field} must not use a non-standard port")
    raw_host = parts.hostname.rstrip(".").lower()
    try:
        ipaddress.ip_address(raw_host)
    except ValueError:
        pass
    else:
        raise ValueError(f"{field} must not use an IP-literal host")
    try:
        host = raw_host.encode("idna").decode("ascii")
    except UnicodeError as exc:
        raise ValueError(f"{field} hostname is invalid") from exc
    return host.removeprefix("www.")


def validate_platform_origin(
    record: dict,
    *,
    approved_forum_hosts: tuple[str, ...] | list[str] = (),
) -> dict:
    """Bind a public item to an exact platform hostname; never follows redirects."""
    if not isinstance(record, dict):
        raise ValueError("record must be an object")
    platform = _identifier(record.get("platform"), "platform", 40).lower()
    if platform not in _PLATFORM_HOSTS:
        raise ValueError("unsupported platform")
    source_host = _https_host(record.get("source_url"), "source_url")
    if platform == "web_forum":
        if not isinstance(approved_forum_hosts, (list, tuple)) or len(approved_forum_hosts) > 50:
            raise ValueError("approved_forum_hosts must contain at most 50 hostnames")
        allowed = {_normalize_host(host, "approved forum host") for host in approved_forum_hosts}
        if not allowed:
            raise ValueError("web_forum requires an explicit exact-host allowlist")
    else:
        allowed = _PLATFORM_HOSTS[platform]
    if source_host not in allowed:
        raise ValueError("source_url host does not match the approved platform origin")
    metadata = record.get("metadata", {})
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be an object")
    checked = [source_host]
    permalink = metadata.get("public_permalink")
    if permalink not in (None, ""):
        permalink_host = _https_host(permalink, "metadata.public_permalink")
        if permalink_host not in allowed:
            raise ValueError("public_permalink host does not match the approved platform origin")
        checked.append(permalink_host)
    return {
        "schema_version": SCHEMA_VERSION,
        "platform": platform,
        "source_url_host": source_host,
        "checked_hosts": sorted(set(checked)),
        "origin_binding_valid": True,
        "redirects_followed": False,
        "private_content_accessed": False,
    }


def _primary_text(record: dict) -> tuple[str | None, str]:
    metadata = record.get("metadata", {})
    if not isinstance(metadata, dict):
        return None, ""
    for field in _TEXT_FIELDS:
        value = metadata.get(field)
        if isinstance(value, str) and value.strip():
            return field, value.strip()
    return None, ""


def content_fingerprint(record: dict) -> dict:
    """Fingerprint the first available public text field after Unicode normalization."""
    if not isinstance(record, dict):
        raise ValueError("record must be an object")
    field, original = _primary_text(record)
    if not original:
        return {
            "content_sha256": None, "content_field": None, "normalized_char_count": 0,
            "exact_text_available": False,
        }
    if len(original) > MAX_TEXT_CHARS:
        raise ValueError(f"content text exceeds {MAX_TEXT_CHARS} characters")
    normalized = " ".join(unicodedata.normalize("NFKC", original).casefold().split())
    if not normalized:
        return {
            "content_sha256": None, "content_field": field, "normalized_char_count": 0,
            "exact_text_available": False,
        }
    return {
        "content_sha256": hashlib.sha256(normalized.encode("utf-8")).hexdigest(),
        "content_field": field,
        "normalized_char_count": len(normalized),
        "exact_text_available": True,
        "normalization": "NFKC_casefold_whitespace_v1",
    }


def cluster_exact_content(records: list[dict]) -> dict:
    """Cluster exact normalized text only; preserve all records and mark candidates unconfirmed."""
    if not isinstance(records, list) or len(records) > MAX_RECORDS:
        raise ValueError(f"records must be a list of at most {MAX_RECORDS}")
    identifiers = []
    groups: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("every record must be an object")
        source_id = _identifier(record.get("source_id"), "source_id")
        if source_id in identifiers:
            raise ValueError("source_id values must be unique")
        identifiers.append(source_id)
        fingerprint = content_fingerprint(record)
        if fingerprint["content_sha256"]:
            groups[fingerprint["content_sha256"]].append({
                "source_id": source_id,
                "platform": record.get("platform", "unknown"),
                "content_field": fingerprint["content_field"],
            })
    clusters = []
    for digest, members in sorted(groups.items()):
        if len(members) > 1:
            clusters.append({
                "content_sha256": digest,
                "members": sorted(members, key=lambda item: (item["platform"], item["source_id"])),
                "candidate_count": len(members),
                "duplicate_confirmed": False,
                "scientific_independence_established": False,
                "records_deleted_or_merged": False,
            })
    clustered = {member["source_id"] for cluster in clusters for member in cluster["members"]}
    return {
        "clusters": clusters,
        "cluster_count": len(clusters),
        "unclustered_source_ids": sorted(set(identifiers) - clustered),
        "source_count": len(records),
        "exact_text_only": True,
        "records_preserved": True,
    }


def score_topic_relevance(record: dict, query: str) -> dict:
    """Return explainable lexical overlap; the score is not evidence quality or truth."""
    if not isinstance(record, dict):
        raise ValueError("record must be an object")
    query = _text(query, "query", 2_000)
    _, text = _primary_text(record)
    if len(text) > MAX_TEXT_CHARS:
        raise ValueError(f"record text exceeds {MAX_TEXT_CHARS} characters")
    query_tokens = sorted(set(tokenize(query)))
    content_tokens = set(tokenize(text))
    matched = [token for token in query_tokens if token in content_tokens]
    missing = [token for token in query_tokens if token not in content_tokens]
    score = (len(matched) / len(query_tokens)) if query_tokens else 0.0
    return {
        "query_token_count": len(query_tokens),
        "matched_tokens": matched,
        "missing_tokens": missing,
        "matched_token_count": len(matched),
        "lexical_overlap_score": round(score, 6),
        "method": "unique_token_recall_v1",
        "semantic_relevance_established": False,
        "scientific_quality_established": False,
        "truth_or_misleadingness_determined": False,
    }


def assess_caption_readiness(
    record: dict,
    *,
    transcript_text: str | None = None,
    expected_language: str | None = None,
) -> dict:
    """Assess supplied caption metadata and optional text; never fetches transcripts."""
    if not isinstance(record, dict):
        raise ValueError("record must be an object")
    metadata = record.get("metadata", {})
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be an object")
    captions = metadata.get("captions_available")
    if captions is not None and not isinstance(captions, bool):
        raise ValueError("captions_available must be boolean or absent")
    actual_language = metadata.get("language")
    if actual_language is not None:
        actual_language = _text(actual_language, "metadata.language", 20).lower()
        if not _LANGUAGE_TAG.fullmatch(actual_language):
            raise ValueError("metadata.language must be a language tag")
    if expected_language is not None:
        expected_language = _text(expected_language, "expected_language", 20).lower()
        if not _LANGUAGE_TAG.fullmatch(expected_language):
            raise ValueError("expected_language must be a language tag")
    if transcript_text is not None:
        transcript_text = _text(transcript_text, "transcript_text", MAX_TEXT_CHARS)
        token_count = len(tokenize(transcript_text))
        character_count = len(transcript_text)
        supplied = True
    else:
        token_count = 0
        character_count = 0
        supplied = False
    flags = []
    if captions is None:
        flags.append("caption_availability_not_reported")
    elif captions is False and supplied:
        flags.append("transcript_supplied_but_captions_reported_unavailable")
    elif captions is True and not supplied:
        flags.append("captions_reported_available_but_transcript_not_supplied")
    if supplied and token_count < 10:
        flags.append("very_short_transcript_for_manual_review")
    if expected_language and actual_language and expected_language.split("-")[0] != actual_language.split("-")[0]:
        flags.append("language_mismatch")
    status = (
        "transcript_supplied_for_review" if supplied
        else "captions_reported_available_transcript_not_supplied" if captions is True
        else "captions_reported_unavailable" if captions is False
        else "caption_status_unknown"
    )
    return {
        "status": status,
        "captions_available_reported": captions,
        "transcript_supplied": supplied,
        "transcript_character_count": character_count,
        "transcript_token_count": token_count,
        "reported_language": actual_language,
        "expected_language": expected_language,
        "flags": flags,
        "transcript_completeness_verified": False,
        "transcript_accuracy_verified": False,
        "media_downloaded": False,
    }


def build_translation_review(
    *,
    record_id: str,
    original_text: str,
    translated_text: str,
    source_language: str,
    target_language: str,
    reviewer_id: str | None = None,
    decision: str = "pending",
    protected_terms: list[str] | tuple[str, ...] = (),
) -> dict:
    """Create a traceable human translation-review record without translating text."""
    record_id = _identifier(record_id, "record_id")
    original = _text(original_text, "original_text", MAX_TEXT_CHARS)
    translated = _text(translated_text, "translated_text", MAX_TEXT_CHARS)
    source_language = _text(source_language, "source_language", 20).lower()
    target_language = _text(target_language, "target_language", 20).lower()
    if not _LANGUAGE_TAG.fullmatch(source_language) or not _LANGUAGE_TAG.fullmatch(target_language):
        raise ValueError("source_language and target_language must be language tags")
    if source_language.split("-")[0] == target_language.split("-")[0]:
        raise ValueError("source and target languages must differ")
    if decision not in {"pending", "accepted", "needs_revision"}:
        raise ValueError("decision must be pending, accepted or needs_revision")
    if decision != "pending" and reviewer_id is None:
        raise ValueError("a reviewer_id is required for a recorded decision")
    reviewer = _identifier(reviewer_id, "reviewer_id") if reviewer_id is not None else None
    if not isinstance(protected_terms, (list, tuple)) or len(protected_terms) > 100:
        raise ValueError("protected_terms must contain at most 100 strings")
    terms = [_text(term, "protected term", 200) for term in protected_terms]
    normalized_translation = unicodedata.normalize("NFKC", translated).casefold()
    missing_terms = [
        term for term in terms
        if unicodedata.normalize("NFKC", term).casefold() not in normalized_translation
    ]
    if missing_terms:
        state = "blocked_protected_terms_missing"
    elif decision == "accepted":
        state = "reviewer_accepted"
    elif decision == "needs_revision":
        state = "revision_requested"
    else:
        state = "unreviewed"
    return {
        "schema_version": SCHEMA_VERSION,
        "record_id": record_id,
        "source_language": source_language,
        "target_language": target_language,
        "original_text": original,
        "translated_text": translated,
        "original_sha256": hashlib.sha256(original.encode("utf-8")).hexdigest(),
        "translated_sha256": hashlib.sha256(translated.encode("utf-8")).hexdigest(),
        "protected_terms": terms,
        "missing_protected_terms": missing_terms,
        "reviewer_id": reviewer,
        "reviewer_decision": decision,
        "review_state": state,
        "reviewer_attested": reviewer is not None and decision != "pending",
        "translation_accuracy_established": False,
        "machine_translation_performed": False,
    }


def extract_claim_candidates(text: str, *, max_candidates: int = MAX_CLAIM_CANDIDATES) -> dict:
    """Return sentence spans with offsets; every candidate remains unverified."""
    original = _text(text, "text", MAX_TEXT_CHARS)
    if isinstance(max_candidates, bool) or not isinstance(max_candidates, int) or not 1 <= max_candidates <= MAX_CLAIM_CANDIDATES:
        raise ValueError(f"max_candidates must be between 1 and {MAX_CLAIM_CANDIDATES}")
    spans = []
    start = 0
    for index, char in enumerate(original):
        boundary = char in "!?。！？；;"
        if char == ".":
            previous = original[index - 1] if index else ""
            following = original[index + 1] if index + 1 < len(original) else ""
            boundary = not (previous.isdigit() and following.isdigit())
        if boundary:
            end = index + 1
            left = start
            while left < end and original[left].isspace():
                left += 1
            right = end
            while right > left and original[right - 1].isspace():
                right -= 1
            if right > left:
                spans.append((left, right))
            start = end
    left = start
    while left < len(original) and original[left].isspace():
        left += 1
    right = len(original.rstrip())
    if right > left:
        spans.append((left, right))
    candidates = []
    for offset_start, offset_end in spans[:max_candidates]:
        sentence = original[offset_start:offset_end]
        normalized = unicodedata.normalize("NFKC", sentence).casefold()
        signals = []
        if re.search(r"\d", sentence):
            signals.append("numeric_or_quantitative_expression")
        if any(cue in normalized for cue in _CAUSAL_CUES):
            signals.append("possible_causal_or_evidential_wording")
        if any(cue in normalized for cue in _COMPARISON_CUES):
            signals.append("possible_comparison")
        if sentence.endswith(("!", "！")):
            signals.append("emphatic_punctuation")
        candidates.append({
            "candidate_id": hashlib.sha256(
                f"{offset_start}:{offset_end}:{sentence}".encode("utf-8")
            ).hexdigest()[:20],
            "text": sentence,
            "start_char": offset_start,
            "end_char": offset_end,
            "heuristic_signals": signals,
            "review_status": "unverified_candidate",
            "scientific_claim_confirmed": False,
            "evidence_linked": False,
        })
    return {
        "candidate_count": len(candidates),
        "candidates": candidates,
        "truncated": len(spans) > max_candidates,
        "original_text_sha256": hashlib.sha256(original.encode("utf-8")).hexdigest(),
        "offset_unit": "unicode_code_points",
        "automatic_claim_verification": False,
    }


def prioritize_review_queue(items: list[dict]) -> dict:
    """Build a deterministic, reason-coded human review queue."""
    if not isinstance(items, list) or len(items) > MAX_QUEUE_ITEMS:
        raise ValueError(f"items must be a list of at most {MAX_QUEUE_ITEMS}")
    seen = set()
    queued = []
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("every queue item must be an object")
        record_id = _identifier(item.get("record_id"), "record_id")
        if record_id in seen:
            raise ValueError("record_id values must be unique")
        seen.add(record_id)
        reasons = []
        score = 0
        if item.get("origin_binding_valid") is False:
            reasons.append("platform_origin_unverified")
            score += 100
        if item.get("sensitive_field_names_flagged"):
            reasons.append("sensitive_metadata_flagged")
            score += 90
        if item.get("translation_review_state") in {
            "unreviewed", "blocked_protected_terms_missing", "revision_requested",
        }:
            reasons.append("translation_requires_human_review")
            score += 70
        if item.get("triage_level") == "multiple_signals":
            reasons.append("multiple_sensationalism_cues")
            score += 50
        elif item.get("triage_level") == "single_signal":
            reasons.append("single_sensationalism_cue")
            score += 25
        if item.get("caption_status") in {
            "captions_reported_available_transcript_not_supplied", "caption_status_unknown",
        }:
            reasons.append("transcript_not_available_for_review")
            score += 30
        claim_count = item.get("claim_candidate_count", 0)
        if isinstance(claim_count, bool) or not isinstance(claim_count, int) or not 0 <= claim_count <= MAX_CLAIM_CANDIDATES:
            raise ValueError("claim_candidate_count must be a bounded non-negative integer")
        if claim_count:
            reasons.append("unverified_claim_candidates")
            score += 20
        priority = "critical" if score >= 90 else "high" if score >= 70 else "medium" if score >= 40 else "normal"
        queued.append({
            "record_id": record_id,
            "priority": priority,
            "priority_score": score,
            "reason_codes": reasons or ["no_configured_review_flag"],
            "human_review_required": bool(reasons),
            "automatic_adjudication": False,
        })
    queued.sort(key=lambda row: (-row["priority_score"], row["record_id"]))
    return {
        "items": queued,
        "item_count": len(queued),
        "priority_counts": {
            level: sum(row["priority"] == level for row in queued)
            for level in ("critical", "high", "medium", "normal")
        },
        "queue_order_deterministic": True,
        "scientific_truth_determined": False,
    }


def compare_record_snapshots(previous: list[dict], current: list[dict]) -> dict:
    """Compare two bounded normalized snapshots without interpreting absence as retraction."""
    for name, records in (("previous", previous), ("current", current)):
        if not isinstance(records, list) or len(records) > MAX_RECORDS:
            raise ValueError(f"{name} must be a list of at most {MAX_RECORDS} records")

    def indexed(records, label):
        result = {}
        for record in records:
            if not isinstance(record, dict):
                raise ValueError(f"{label} records must be objects")
            source_id = _identifier(record.get("source_id"), f"{label}.source_id")
            if source_id in result:
                raise ValueError(f"{label} source_id values must be unique")
            _canonical_bytes(record)
            result[source_id] = record
        return result

    before, after = indexed(previous, "previous"), indexed(current, "current")
    added = sorted(set(after) - set(before))
    absent = sorted(set(before) - set(after))
    changed = []
    for source_id in sorted(set(before) & set(after)):
        old, new = before[source_id], after[source_id]
        fields = sorted(
            key for key in set(old) | set(new)
            if _canonical_bytes(old.get(key)) != _canonical_bytes(new.get(key))
        )
        if fields:
            changed.append({
                "source_id": source_id,
                "changed_fields": fields,
                "previous_snapshot_sha256": _digest(old),
                "current_snapshot_sha256": _digest(new),
            })
    return {
        "added_source_ids": added,
        "absent_from_current_source_ids": absent,
        "changed_records": changed,
        "absence_is_not_retraction": True,
        "metadata_change_is_not_a_correction": True,
        "records_deleted_or_merged": False,
    }


def plan_intake_budget(
    records: list[dict],
    *,
    max_records: int = MAX_RECORDS,
    max_text_chars: int = MAX_TOTAL_TEXT_CHARS,
    max_serialized_bytes: int = MAX_SERIALIZED_BYTES,
) -> dict:
    """Select whole records in deterministic round-robin platform order."""
    if not isinstance(records, list) or len(records) > MAX_INPUT_RECORDS:
        raise ValueError(f"records must be a list of at most {MAX_INPUT_RECORDS}")
    limits = (
        ("max_records", max_records, 1, MAX_RECORDS),
        ("max_text_chars", max_text_chars, 1, MAX_TOTAL_TEXT_CHARS),
        ("max_serialized_bytes", max_serialized_bytes, 1, MAX_SERIALIZED_BYTES),
    )
    for name, value, minimum, maximum in limits:
        if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
            raise ValueError(f"{name} must be between {minimum} and {maximum}")
    grouped: dict[str, list[tuple[int, dict, str, int, int]]] = defaultdict(list)
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError("every record must be an object")
        platform = str(record.get("platform", "unknown")).lower()
        source_id = str(record.get("source_id") or (
            f"{platform}:{record.get('provider_item_id')}" if record.get("provider_item_id")
            else f"record-{index:04d}"
        ))
        try:
            encoded_size = len(_canonical_bytes(record))
        except ValueError:
            grouped[platform].append((index, record, source_id, -1, -1))
            continue
        metadata = record.get("metadata", {})
        if not isinstance(metadata, dict):
            raise ValueError("record metadata must be an object")
        text_size = sum(
            len(value) for value in metadata.values()
            if isinstance(value, str) and value
        )
        grouped[platform].append((index, record, source_id, text_size, encoded_size))
    platform_names = sorted(grouped)
    positions = {name: 0 for name in platform_names}
    selected, excluded = [], []
    used_text, used_bytes = 0, 0
    while True:
        progressed = False
        for platform in platform_names:
            position = positions[platform]
            if position >= len(grouped[platform]):
                continue
            progressed = True
            index, record, source_id, text_size, encoded_size = grouped[platform][position]
            positions[platform] += 1
            if len(selected) >= max_records:
                excluded.append({"index": index, "record_id": source_id, "reason": "record_limit"})
                continue
            if encoded_size < 0:
                excluded.append({"index": index, "record_id": source_id, "reason": "not_json_serializable"})
                continue
            if text_size > max_text_chars - used_text:
                excluded.append({"index": index, "record_id": source_id, "reason": "text_budget"})
                continue
            if encoded_size > max_serialized_bytes - used_bytes:
                excluded.append({"index": index, "record_id": source_id, "reason": "serialized_byte_budget"})
                continue
            selected.append(index)
            used_text += text_size
            used_bytes += encoded_size
        if not progressed:
            break
    return {
        "selected_indices": selected,
        "selected_record_count": len(selected),
        "excluded": excluded,
        "excluded_count": len(excluded),
        "platform_round_robin_order": platform_names,
        "used_text_chars": used_text,
        "used_serialized_bytes": used_bytes,
        "budgets": {
            "max_records": max_records,
            "max_text_chars": max_text_chars,
            "max_serialized_bytes": max_serialized_bytes,
        },
        "whole_records_only": True,
        "silent_truncation": False,
    }


def build_audit_chain(events: list[dict]) -> dict:
    """Build a bounded SHA-256 chain; raw source text must not be placed in events."""
    if not isinstance(events, list) or len(events) > MAX_AUDIT_EVENTS:
        raise ValueError(f"events must be a list of at most {MAX_AUDIT_EVENTS}")
    chain = []
    previous_hash = _ZERO_HASH
    seen = set()
    for sequence, event in enumerate(events):
        if not isinstance(event, dict):
            raise ValueError("every audit event must be an object")
        event_id = _identifier(event.get("event_id"), "event_id")
        if event_id in seen:
            raise ValueError("event_id values must be unique")
        seen.add(event_id)
        event_type = _identifier(event.get("event_type"), "event_type", 80)
        record_id = _identifier(event.get("record_id"), "record_id")
        occurred_at = _text(event.get("occurred_at"), "occurred_at", 64)
        try:
            parsed = datetime.fromisoformat(occurred_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("occurred_at must be a timezone-aware ISO timestamp") from exc
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("occurred_at must include a timezone")
        payload_sha256 = event.get("payload_sha256")
        if not isinstance(payload_sha256, str) or not _SHA256.fullmatch(payload_sha256):
            raise ValueError("payload_sha256 must be a lowercase SHA-256 digest")
        safe_event = {
            "event_id": event_id,
            "event_type": event_type,
            "record_id": record_id,
            "occurred_at": parsed.isoformat(),
            "payload_sha256": payload_sha256,
        }
        entry = {"sequence": sequence, "previous_hash": previous_hash, "event": safe_event}
        entry["event_hash"] = _digest(entry)
        previous_hash = entry["event_hash"]
        chain.append(entry)
    return {
        "schema_version": SCHEMA_VERSION,
        "event_count": len(chain),
        "events": chain,
        "head_hash": previous_hash,
        "capacity": MAX_AUDIT_EVENTS,
        "automatic_pruning": False,
        "raw_source_text_stored": False,
    }


def verify_audit_chain(chain: dict) -> dict:
    """Verify sequence, predecessor links and event digests without repairing the chain."""
    if not isinstance(chain, dict) or not isinstance(chain.get("events"), list):
        raise ValueError("chain must contain an events list")
    events = chain["events"]
    if len(events) > MAX_AUDIT_EVENTS:
        raise ValueError(f"chain exceeds {MAX_AUDIT_EVENTS} events")
    previous_hash = _ZERO_HASH
    errors = []
    for expected_sequence, entry in enumerate(events):
        if not isinstance(entry, dict):
            errors.append(f"entry_{expected_sequence}_not_object")
            continue
        if entry.get("sequence") != expected_sequence:
            errors.append(f"entry_{expected_sequence}_sequence_mismatch")
        if entry.get("previous_hash") != previous_hash:
            errors.append(f"entry_{expected_sequence}_previous_hash_mismatch")
        supplied_hash = entry.get("event_hash")
        payload = {key: value for key, value in entry.items() if key != "event_hash"}
        try:
            calculated = _digest(payload)
        except ValueError:
            errors.append(f"entry_{expected_sequence}_not_canonical")
            continue
        if supplied_hash != calculated:
            errors.append(f"entry_{expected_sequence}_hash_mismatch")
        if isinstance(supplied_hash, str) and _SHA256.fullmatch(supplied_hash):
            previous_hash = supplied_hash
        else:
            previous_hash = _ZERO_HASH
    if chain.get("event_count") != len(events):
        errors.append("event_count_mismatch")
    if chain.get("head_hash") != previous_hash:
        errors.append("head_hash_mismatch")
    return {
        "valid": not errors,
        "errors": errors,
        "verified_event_count": len(events) if not errors else 0,
        "head_hash": previous_hash,
        "chain_repaired": False,
    }


def prepare_public_media_batch(
    records: list[dict],
    query: str,
    *,
    approved_forum_hosts: tuple[str, ...] | list[str] = (),
    transcripts: dict[str, str] | None = None,
    translations: dict[str, dict] | None = None,
) -> dict:
    """Run the opt-in discovery/review workflow over already-authorized metadata."""
    query = _text(query, "query", 2_000)
    budget = plan_intake_budget(records)
    transcripts = transcripts or {}
    translations = translations or {}
    if not isinstance(transcripts, dict) or not isinstance(translations, dict):
        raise ValueError("transcripts and translations must be objects")
    normalized, findings, rejected, queue_inputs = [], [], [], []
    for index in budget["selected_indices"]:
        raw = records[index]
        platform = str(raw.get("platform") or "unknown").lower()
        source_id = str(raw.get("source_id") or (
            f"{platform}:{raw.get('provider_item_id')}" if raw.get("provider_item_id")
            else f"record-{index:04d}"
        ))
        try:
            origin = validate_platform_origin(raw, approved_forum_hosts=approved_forum_hosts)
        except (ValueError, TypeError) as exc:
            rejected.append({"record_id": source_id, "reason": str(exc)})
            queue_inputs.append({
                "record_id": source_id, "origin_binding_valid": False,
                "sensitive_field_names_flagged": [],
                "triage_level": "no_lexical_signal",
                "caption_status": "caption_status_unknown",
                "claim_candidate_count": 0,
            })
            continue
        try:
            safe = normalize_public_record(raw)
        except (ValueError, TypeError) as exc:
            rejected.append({"record_id": source_id, "reason": str(exc)})
            queue_inputs.append({
                "record_id": source_id, "origin_binding_valid": True,
                "sensitive_field_names_flagged": [],
                "triage_level": "no_lexical_signal",
                "caption_status": "caption_status_unknown",
                "claim_candidate_count": 0,
            })
            continue
        normalized.append(safe)
        _, title_text = _primary_text(safe)
        language = safe["metadata"].get("language")
        supported = {
            "ar", "bn", "de", "en", "es", "fr", "he", "hi", "id", "it", "ja",
            "ko", "nl", "pl", "pt", "ru", "th", "tr", "uk", "vi", "zh",
        }
        triage = triage_title(
            title_text,
            language if language and language.split("-")[0] in supported else None,
        ) if title_text else {
            "triage_level": "no_lexical_signal", "matched_cues": [],
            "matched_cue_count": 0, "languages_checked": [],
            "truth_or_misleadingness_determined": False,
        }
        relevance = score_topic_relevance(safe, query)
        caption = assess_caption_readiness(
            safe, transcript_text=transcripts.get(safe["source_id"])
        )
        claims = extract_claim_candidates(title_text) if title_text else {
            "candidate_count": 0, "candidates": [], "truncated": False,
            "automatic_claim_verification": False,
        }
        translation = None
        if safe["source_id"] in translations:
            details = translations[safe["source_id"]]
            if not isinstance(details, dict):
                raise ValueError("each translation entry must be an object")
            translation = build_translation_review(
                record_id=safe["source_id"],
                original_text=details.get("original_text", title_text),
                translated_text=details.get("translated_text", ""),
                source_language=details.get("source_language", language or "und"),
                target_language=details.get("target_language", "en"),
                reviewer_id=details.get("reviewer_id"),
                decision=details.get("decision", "pending"),
                protected_terms=details.get("protected_terms", ()),
            )
        finding = {
            "record_id": safe["source_id"], "origin": origin, "triage": triage,
            "relevance": relevance, "caption_readiness": caption,
            "claim_candidates": claims, "translation_review": translation,
        }
        findings.append(finding)
        queue_inputs.append({
            "record_id": safe["source_id"],
            "origin_binding_valid": origin["origin_binding_valid"],
            "sensitive_field_names_flagged": safe["sensitive_field_names_flagged"],
            "translation_review_state": translation["review_state"] if translation else None,
            "triage_level": triage["triage_level"],
            "caption_status": caption["status"],
            "claim_candidate_count": claims["candidate_count"],
        })
    clusters = cluster_exact_content(normalized)
    review_queue = prioritize_review_queue(queue_inputs)
    manifest_payload = {
        "schema_version": SCHEMA_VERSION,
        "policy_version": POLICY_VERSION,
        "query": query,
        "selected_source_ids": [item["source_id"] for item in normalized],
        "rejected": rejected,
        "budget": budget,
        "content_clusters": clusters,
        "findings": findings,
        "review_queue": review_queue,
        "scientific_evidence_established": False,
        "automatic_adjudication": False,
    }
    return {
        **manifest_payload,
        "records": normalized,
        "manifest_sha256": _digest(manifest_payload),
        "media_downloaded": False,
        "private_content_accessed": False,
        "terms_of_service_bypass": False,
        "translation_performed": False,
        "scientific_evidence_established": False,
        "automatic_adjudication": False,
    }


__all__ = [
    "SCHEMA_VERSION", "POLICY_VERSION", "validate_platform_origin",
    "content_fingerprint", "cluster_exact_content", "score_topic_relevance",
    "assess_caption_readiness", "build_translation_review",
    "extract_claim_candidates", "prioritize_review_queue",
    "compare_record_snapshots", "plan_intake_budget", "build_audit_chain",
    "verify_audit_chain", "prepare_public_media_batch",
]

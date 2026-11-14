import copy
import hashlib
import json

import pytest

from ssswet_core.public_media_evidence_pipeline import (
    assess_language_script_consistency,
    audit_adapter_contract,
    audit_headline_context,
    bind_claim_candidates_to_source,
    build_human_review_packet,
    build_pagination_checkpoint_chain,
    build_publisher_status_ledger,
    parse_caption_transcript,
    parse_public_feed,
    scan_public_text_privacy,
    verify_pagination_checkpoint_chain,
    verify_publisher_status_ledger,
)
from ssswet_core.public_media_ingestion import normalize_public_record
from ssswet_core.public_media_research_workbench import build_translation_review


CAPTURED = "2026-11-14T08:00:00+00:00"
HOSTS = ["forum.example"]


def rss_feed(link="https://forum.example/post/1"):
    return f"""<?xml version="1.0"?>
<rss version="2.0"><channel><title>Materials forum</title>
<item><guid>entry-1</guid><link>{link}</link><title>Battery test</title>
<description>A controlled materials test.</description>
<pubDate>Sat, 14 Nov 2026 08:00:00 +0000</pubDate></item>
</channel></rss>"""


def normalized_record(text="A result was 12%.", title="Battery test"):
    return normalize_public_record({
        "platform": "web_forum",
        "visibility": "public",
        "access_mode": "authorized_public_feed",
        "source_url": "https://forum.example/post/1?session=private",
        "captured_at": CAPTURED,
        "provider_item_id": "entry-1",
        "content_type": "forum_post",
        "metadata": {
            "thread_id": "entry-1",
            "title": title,
            "text": text,
            "forum_name": "Materials forum",
            "public_permalink": "https://forum.example/post/1?session=private",
        },
    })


def test_rss_feed_is_normalized_and_origin_bound():
    result = parse_public_feed(rss_feed(), captured_at=CAPTURED, approved_hosts=HOSTS)
    assert result["feed_format"] == "rss"
    assert result["accepted_count"] == 1
    record = result["records"][0]
    assert record["platform"] == "web_forum"
    assert record["source_id"] == "web_forum:entry-1"
    assert record["metadata"]["title"] == "Battery test"
    assert record["scientific_evidence_established"] is False
    assert result["network_requests_made"] is False


def test_atom_feed_is_supported_with_namespaced_elements():
    payload = """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
<title>Research notes</title><entry><id>atom-1</id>
<link rel="alternate" href="https://forum.example/atom/1"/>
<title>Thermal test</title><summary>Preliminary observation</summary>
<updated>2026-11-14T08:00:00Z</updated></entry></feed>"""
    result = parse_public_feed(payload, captured_at=CAPTURED, approved_hosts=HOSTS)
    assert result["feed_format"] == "atom"
    assert result["records"][0]["metadata"]["thread_id"] == "atom-1"


def test_json_feed_11_is_supported():
    payload = json.dumps({
        "version": "https://jsonfeed.org/version/1.1",
        "title": "Open science",
        "items": [{
            "id": "json-1", "url": "https://forum.example/json/1",
            "title": "Battery research", "content_text": "A measured result.",
            "date_published": "2026-11-14T08:00:00Z",
        }],
    })
    result = parse_public_feed(payload, captured_at=CAPTURED, approved_hosts=HOSTS)
    assert result["feed_format"] == "jsonfeed"
    assert result["accepted_count"] == 1
    assert result["records"][0]["metadata"]["text"] == "A measured result."


def test_feed_rejects_dtd_entities_and_oversized_input():
    with pytest.raises(ValueError, match="DTD"):
        parse_public_feed('<!DOCTYPE rss [<!ENTITY x "x">]><rss/>',
                          captured_at=CAPTURED, approved_hosts=HOSTS)
    with pytest.raises(ValueError, match="2 MiB"):
        parse_public_feed("x" * (2 * 1024 * 1024 + 1),
                          captured_at=CAPTURED, approved_hosts=HOSTS)


@pytest.mark.parametrize("link", [
    "http://forum.example/post/1",
    "https://evil.example/post/1",
    "https://user:pass@forum.example/post/1",
    "https://forum.example:8443/post/1",
])
def test_feed_rejects_unapproved_or_unsafe_item_links(link):
    result = parse_public_feed(rss_feed(link), captured_at=CAPTURED, approved_hosts=HOSTS)
    assert result["accepted_count"] == 0
    assert result["rejected_count"] == 1


def test_feed_missing_link_is_reported_without_silent_loss():
    result = parse_public_feed(rss_feed(""), captured_at=CAPTURED, approved_hosts=HOSTS)
    assert result["rejected_entries"][0]["reason"] == "item_link_missing"


def test_feed_rejects_duplicate_entry_identifiers():
    payload = rss_feed().replace("</item>", "</item><item><guid>entry-1</guid><link>https://forum.example/2</link><title>Other</title></item>")
    with pytest.raises(ValueError, match="unique"):
        parse_public_feed(payload, captured_at=CAPTURED, approved_hosts=HOSTS)


def test_adapter_contract_exposes_approved_fields_and_required_gaps():
    result = audit_adapter_contract(
        "youtube", access_mode="official_api",
        declared_fields=["video_id", "title"], required_fields=["video_id", "title", "published_at"],
    )
    assert result["access_mode_approved"] is True
    assert result["missing_required_fields"] == ["published_at"]
    assert result["compatible"] is False


def test_adapter_contract_fails_closed_for_unapproved_access_and_sensitive_fields():
    result = audit_adapter_contract(
        "x", access_mode="browser_scrape",
        declared_fields=["post_id", "text", "email"],
    )
    assert result["access_mode_approved"] is False
    assert result["sensitive_field_names"] == ["email"]
    assert result["compatible"] is False
    assert "email" not in result["allowed_fields"]


def test_adapter_contract_rejects_unknown_platform_and_duplicate_fields():
    with pytest.raises(ValueError):
        audit_adapter_contract("unknown", access_mode="official_api", declared_fields=[])
    with pytest.raises(ValueError, match="duplicates"):
        audit_adapter_contract("youtube", access_mode="official_api", declared_fields=["title", "title"])


def page(sequence, cursor, next_cursor, page_id):
    return {
        "sequence": sequence, "provider": "youtube",
        "cursor": cursor, "next_cursor": next_cursor,
        "cursor_reference_id": f"vault:{sequence - 1}" if cursor else None,
        "next_cursor_reference_id": f"vault:{sequence}" if next_cursor else None,
        "page_id": page_id, "item_ids": [f"item-{sequence}"],
        "captured_at": CAPTURED,
    }


def test_pagination_checkpoint_chain_verifies_without_persisting_tokens():
    chain = build_pagination_checkpoint_chain([
        page(0, None, "opaque-secret-cursor", "page-0"),
        page(1, "opaque-secret-cursor", None, "page-1"),
    ])
    assert verify_pagination_checkpoint_chain(chain)["valid"] is True
    encoded = json.dumps(chain)
    assert "opaque-secret-cursor" not in encoded
    assert chain["raw_cursor_tokens_persisted"] is False
    assert chain["page_count"] == 2


def test_pagination_checkpoint_detects_tampering_and_cursor_cycles():
    chain = build_pagination_checkpoint_chain([page(0, None, "cursor-1", "page-0")])
    changed = copy.deepcopy(chain)
    changed["pages"][0]["item_ids"] = ["forged"]
    assert verify_pagination_checkpoint_chain(changed)["valid"] is False
    with pytest.raises(ValueError, match="loop"):
        build_pagination_checkpoint_chain([
            page(0, None, "cursor-1", "page-0"),
            page(1, "cursor-1", "cursor-1", "page-1"),
        ])


def test_pagination_checkpoint_rejects_gaps_and_duplicate_pages():
    with pytest.raises(ValueError, match="contiguous"):
        build_pagination_checkpoint_chain([page(1, None, None, "page-1")])
    with pytest.raises(ValueError, match="unique"):
        build_pagination_checkpoint_chain([page(0, None, None, "same"), page(1, None, None, "same")])


def test_language_script_check_handles_japanese_and_chinese_without_overclaim():
    japanese = assess_language_script_consistency("これは科学の研究です", "ja")
    chinese = assess_language_script_consistency("这是科学研究", "zh")
    ambiguous = assess_language_script_consistency("研究成果", "ja")
    assert japanese["status"] == "script_compatible"
    assert chinese["status"] == "script_compatible"
    assert ambiguous["status"] == "ambiguous_han_only_text"
    assert japanese["language_identification_performed"] is False


def test_language_script_check_detects_mismatch_and_mixed_text():
    mismatch = assess_language_script_consistency("Привет исследование", "en")
    mixed = assess_language_script_consistency("Hello Привет", "en")
    assert mismatch["status"] == "script_mismatch"
    assert mixed["status"] in {"mixed_script_review", "script_compatible"}


def test_headline_context_audit_surfaces_multilingual_review_signals():
    result = audit_headline_context(
        "You won't believe this SHOCKING discovery!!!",
        "Preliminary pilot findings may be limited to a small sample.",
        language="en",
    )
    assert result["reason_codes"]
    assert result["review_priority"] in {"review_priority", "high_review_priority"}
    assert result["clickbait_determined"] is False


def test_headline_context_neutral_control_does_not_escalate():
    result = audit_headline_context(
        "Preliminary battery test results",
        "The preliminary battery test measured capacity over three cycles.",
        language="en",
    )
    assert result["review_priority"] == "no_extra_review_signal"


def test_japanese_headline_cue_is_preserved_as_review_signal():
    result = audit_headline_context("信じられない新発見", "予備的な研究結果です", language="ja")
    assert result["title_triage"]["matched_cues"]
    assert result["clickbait_determined"] is False


def test_vtt_parser_preserves_cue_text_and_codepoint_offsets():
    payload = "WEBVTT\n\ncue-a\n00:00:01.000 --> 00:00:03.000\nA result was 12%.\n"
    result = parse_caption_transcript(payload, language="en")
    cue = result["cues"][0]
    assert result["format"] == "vtt"
    assert cue["start_ms"] == 1000
    assert payload[cue["start_char"]:cue["end_char"]] == cue["text"]
    assert cue["cue_id"] == "cue-a"


def test_srt_parser_handles_comma_milliseconds():
    payload = "1\n00:00:01,250 --> 00:00:02,500\nMeasured result.\n"
    result = parse_caption_transcript(payload, format_hint="srt")
    assert result["cues"][0]["start_ms"] == 1250
    assert result["cues"][0]["end_ms"] == 2500


def test_transcript_parser_flags_overlap_and_rejects_reversed_or_unsorted_cues():
    overlap = "1\n00:00:00,000 --> 00:00:03,000\nFirst.\n\n2\n00:00:02,000 --> 00:00:04,000\nSecond.\n"
    assert parse_caption_transcript(overlap)["overlap_count"] == 1
    reversed_time = "1\n00:00:03,000 --> 00:00:02,000\nBad.\n"
    with pytest.raises(ValueError, match="after"):
        parse_caption_transcript(reversed_time)
    unsorted = "1\n00:00:03,000 --> 00:00:04,000\nFirst.\n\n2\n00:00:01,000 --> 00:00:02,000\nSecond.\n"
    with pytest.raises(ValueError, match="ordered"):
        parse_caption_transcript(unsorted)


def test_transcript_parser_rejects_malformed_and_oversized_cues():
    with pytest.raises(ValueError, match="timing"):
        parse_caption_transcript("1\nnot-a-time\nNo timing.\n")
    with pytest.raises(ValueError, match="2 MiB"):
        parse_caption_transcript("x" * (2 * 1024 * 1024 + 1))


def test_claim_binding_preserves_snapshot_hash_offsets_and_translation_reference():
    record = normalized_record()
    text = "A result was 12%. Another result was 14%."
    candidates = {
        "candidates": [
            {"start_char": 0, "end_char": 17, "text": "A result was 12%."},
        ]
    }
    translation = {
        "original_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "translated_sha256": hashlib.sha256("Un résultat.".encode()).hexdigest(),
        "source_language": "en", "target_language": "fr",
    }
    result = bind_claim_candidates_to_source(
        record, text, candidates=candidates, language="en",
        translation_reference=translation,
    )
    claim = result["claims"][0]
    assert claim["source_snapshot_sha256"] == record["snapshot_sha256"]
    assert text[claim["start_char"]:claim["end_char"]] == claim["claim_text"]
    assert claim["translation_reference"]["translation_replaces_original"] is False
    assert claim["verification_state"] == "unverified_candidate"


def test_claim_binding_rejects_wrong_offsets_or_snapshot_hash():
    record = normalized_record()
    with pytest.raises(ValueError, match="exact source text"):
        bind_claim_candidates_to_source(
            record, "A result was 12%.",
            candidates=[{"start_char": 0, "end_char": 5, "text": "wrong"}],
        )
    broken = dict(record, snapshot_sha256="invalid")
    with pytest.raises(ValueError, match="SHA-256"):
        bind_claim_candidates_to_source(broken, "A result was 12%.")


def status_event(event_id, event_type, prior, new, when):
    return {
        "event_id": event_id, "source_id": "web_forum:entry-1",
        "event_type": event_type, "occurred_at": when,
        "prior_snapshot_sha256": prior, "new_snapshot_sha256": new,
        "publisher_reference_url": "https://forum.example/corrections/1",
        "publisher_statement": f"Publisher declared {event_type}.",
        "publisher_declared": True,
    }


def test_publisher_status_ledger_retains_versions_and_verifies():
    first = "a" * 64
    second = "b" * 64
    ledger = build_publisher_status_ledger([
        status_event("event-1", "corrected", first, second, "2026-11-14T08:00:00Z"),
        status_event("event-2", "retracted", second, None, "2026-11-14T09:00:00Z"),
    ])
    assert verify_publisher_status_ledger(ledger)["valid"] is True
    assert ledger["events"][0]["new_snapshot_sha256"] == second
    assert ledger["source_records_deleted"] is False


def test_publisher_status_ledger_detects_tampering_and_requires_publisher_declaration():
    ledger = build_publisher_status_ledger([
        status_event("event-1", "updated", "a" * 64, "b" * 64, "2026-11-14T08:00:00Z")
    ])
    tampered = copy.deepcopy(ledger)
    tampered["events"][0]["publisher_statement"] = "Changed"
    assert verify_publisher_status_ledger(tampered)["valid"] is False
    event = status_event("event-2", "retracted", "b" * 64, None, "2026-11-14T09:00:00Z")
    event["publisher_declared"] = False
    with pytest.raises(ValueError, match="publisher-declared"):
        build_publisher_status_ledger([event])


def test_publisher_status_ledger_rejects_time_reversal_and_bad_event_types():
    events = [
        status_event("event-1", "updated", "a" * 64, "b" * 64, "2026-11-14T09:00:00Z"),
        status_event("event-2", "retracted", "b" * 64, None, "2026-11-14T08:00:00Z"),
    ]
    with pytest.raises(ValueError, match="chronological"):
        build_publisher_status_ledger(events)
    events[0]["event_type"] = "deleted_by_ai"
    with pytest.raises(ValueError, match="event_type"):
        build_publisher_status_ledger(events[:1])


def test_privacy_scan_redacts_without_echoing_matched_values():
    secret = "ghp_" + "a" * 24
    text = f"Email jane@example.org phone +33 6 12 34 56 78 IP 192.168.1.4 GPS 48.8566, 2.3522 {secret}"
    result = scan_public_text_privacy(text)
    categories = {item["category"] for item in result["findings"]}
    assert {"email", "phone_like", "ipv4", "coordinates", "credential"}.issubset(categories)
    assert "jane@example.org" not in json.dumps(result["findings"])
    assert secret not in json.dumps(result)
    assert "[REDACTED:email]" in result["redacted_preview"]
    assert result["input_mutated"] is False


def test_privacy_scan_has_no_findings_for_plain_text():
    result = scan_public_text_privacy("A controlled experiment reported a measured result.")
    assert result["finding_count"] == 0
    assert result["redacted_preview"] == "A controlled experiment reported a measured result."


def test_review_packet_is_deterministic_bounded_and_strips_tracking_query():
    record = normalized_record()
    text = record["metadata"]["text"]
    bound = bind_claim_candidates_to_source(record, text)
    packet1 = build_human_review_packet(record_list := [record], claim_bindings=bound["claims"])
    packet2 = build_human_review_packet(record_list, claim_bindings=bound["claims"])
    assert packet1["manifest_sha256"] == packet2["manifest_sha256"]
    assert packet1["canonical_bytes"] == packet2["canonical_bytes"]
    assert packet1["records"][0]["source_url_query_removed"] is True
    assert "session=private" not in json.dumps(packet1)
    assert packet1["raw_media_included"] is False


def test_review_packet_redacts_public_text_and_preserves_original_hash():
    record = normalized_record("Contact jane@example.org for details.")
    original_hash = record["snapshot_sha256"]
    packet = build_human_review_packet([record])
    encoded = json.dumps(packet)
    assert "jane@example.org" not in encoded
    assert "[REDACTED:email]" in encoded
    assert packet["records"][0]["snapshot_sha256"] == original_hash
    assert packet["privacy_screening"]["findings"] >= 1


def test_review_packet_rejects_dangling_claims_and_oversized_records():
    record = normalized_record()
    claim = {
        "claim_id": "claim-1", "source_id": "missing",
        "source_snapshot_sha256": "a" * 64, "start_char": 0, "end_char": 1,
        "claim_text": "x", "claim_text_sha256": hashlib.sha256(b"x").hexdigest(),
    }
    with pytest.raises(ValueError, match="does not resolve"):
        build_human_review_packet([record], claim_bindings=[claim])
    with pytest.raises(ValueError, match="500"):
        build_human_review_packet([record] * 501)


def test_review_packet_accepts_empty_status_ledger_and_translation_review():
    record = normalized_record()
    translation = build_translation_review(
        record_id=record["source_id"], original_text="Battery test",
        translated_text="Essai de batterie", source_language="en",
        target_language="fr",
    )
    packet = build_human_review_packet([record], translation_reviews=[translation])
    assert packet["translation_reviews"][0]["review_state"] == "unreviewed"
    assert packet["publisher_status_events"] == []


def test_review_packet_rejects_unknown_translation_source():
    translation = build_translation_review(
        record_id="missing", original_text="Battery test",
        translated_text="Essai de batterie", source_language="en",
        target_language="fr",
    )
    with pytest.raises(ValueError, match="does not exist"):
        build_human_review_packet([normalized_record()], translation_reviews=[translation])

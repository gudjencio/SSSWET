from __future__ import annotations

import copy
import hashlib

import pytest

from ssswet_core.public_media_research_workbench import (
    assess_caption_readiness, build_audit_chain, build_translation_review,
    cluster_exact_content, compare_record_snapshots, content_fingerprint,
    extract_claim_candidates, plan_intake_budget, prepare_public_media_batch,
    prioritize_review_queue, score_topic_relevance, validate_platform_origin,
    verify_audit_chain,
)


def record(source_id="yt-1", platform="youtube", url="https://www.youtube.com/watch?v=abc",
           title="New material science study", language="en", **metadata):
    text_field = "text" if platform in {
        "x", "instagram", "facebook", "threads", "bluesky", "reddit",
        "snapchat", "mewe", "weibo",
    } else "title"
    values = {text_field: title, "language": language}
    values.update(metadata)
    access = {
        "youtube": "official_api", "x": "official_api",
        "instagram": "approved_meta_graph_api", "facebook": "approved_meta_graph_api",
        "threads": "approved_threads_api", "bluesky": "public_atproto_appview",
        "reddit": "official_api", "snapchat": "approved_public_discovery",
        "mewe": "authorized_public_feed", "weibo": "official_api",
        "bilibili": "official_api", "niconico": "official_api",
        "qiita": "official_api", "web_forum": "permitted_public_page",
    }[platform]
    return {
        "platform": platform, "visibility": "public", "access_mode": access,
        "source_url": url, "captured_at": "2026-11-14T08:00:00+01:00",
        "provider_item_id": source_id,
        "content_type": "video" if platform in {"youtube", "bilibili", "niconico"} else "post",
        "metadata": values,
    }


def test_platform_origin_accepts_exact_official_host_and_public_permalink():
    item = record()
    item["metadata"]["public_permalink"] = "https://youtu.be/abc"
    result = validate_platform_origin(item)
    assert result["origin_binding_valid"] is True
    assert result["checked_hosts"] == ["youtu.be", "youtube.com"]
    assert result["redirects_followed"] is False


@pytest.mark.parametrize("url", [
    "http://youtube.com/watch?v=x",
    "https://youtube.com.evil.example/watch?v=x",
    "https://evil-youtube.com/watch?v=x",
    "https://user:pass@youtube.com/watch?v=x",
    "https://127.0.0.1/watch?v=x",
    "https://youtube.com:8443/watch?v=x",
])
def test_platform_origin_rejects_insecure_spoofed_or_nonstandard_urls(url):
    with pytest.raises(ValueError):
        validate_platform_origin(record(url=url))


def test_platform_origin_requires_exact_forum_allowlist():
    forum = record(platform="web_forum", url="https://forum.example.org/topic/1")
    with pytest.raises(ValueError, match="explicit exact-host"):
        validate_platform_origin(forum)
    assert validate_platform_origin(
        forum, approved_forum_hosts=["forum.example.org"]
    )["origin_binding_valid"]
    with pytest.raises(ValueError):
        validate_platform_origin(forum, approved_forum_hosts=["example.org"])


def test_platform_origin_rejects_mismatched_permalink_and_ip_allowlist():
    item = record()
    item["metadata"]["public_permalink"] = "https://evil.example/post"
    with pytest.raises(ValueError, match="public_permalink"):
        validate_platform_origin(item)
    forum = record(platform="web_forum", url="https://127.0.0.1/topic")
    with pytest.raises(ValueError):
        validate_platform_origin(forum, approved_forum_hosts=["127.0.0.1"])


def test_content_fingerprint_normalizes_unicode_case_and_whitespace():
    first = record(title="  ＭＡＴＥＲＩＡＬ   Science ")
    second = record("x-1", "x", "https://x.com/post/1", title="material science")
    assert content_fingerprint(first)["content_sha256"] == content_fingerprint(second)["content_sha256"]


def test_content_fingerprint_does_not_invent_content():
    item = record(title="")
    assert content_fingerprint(item)["exact_text_available"] is False


def test_exact_content_clusters_cross_platform_but_preserves_records():
    from ssswet_core.public_media_ingestion import normalize_public_record
    a = normalize_public_record(record(title="A new battery material"))
    b = normalize_public_record(record("x-1", "x", "https://x.com/post/1", title="A NEW battery material"))
    c = normalize_public_record(record("x-2", "x", "https://x.com/post/2", title="A new battery material!"))
    result = cluster_exact_content([a, b, c])
    assert result["cluster_count"] == 1
    assert {m["source_id"] for m in result["clusters"][0]["members"]} == {"youtube:yt-1", "x:x-1"}
    assert result["clusters"][0]["duplicate_confirmed"] is False
    assert result["records_preserved"] is True


def test_exact_content_rejects_duplicate_ids_and_near_duplicates_remain_separate():
    from ssswet_core.public_media_ingestion import normalize_public_record
    a = normalize_public_record(record())
    b = normalize_public_record(record("yt-2", title="New material science study!"))
    assert cluster_exact_content([a, b])["cluster_count"] == 0
    with pytest.raises(ValueError):
        cluster_exact_content([a, a])


def test_topic_relevance_exposes_matched_and_missing_terms():
    item = {"metadata": {"title": "Japanese battery material research"}}
    first = score_topic_relevance(item, "battery material quantum")
    second = score_topic_relevance(item, "battery material quantum")
    assert first == second
    assert first["matched_tokens"] == ["battery", "material"]
    assert first["missing_tokens"] == ["quantum"]
    assert first["lexical_overlap_score"] == pytest.approx(2 / 3)
    assert first["scientific_quality_established"] is False


def test_topic_relevance_supports_japanese_character_bigrams():
    item = {"metadata": {"title": "新しい材料科学の研究"}}
    result = score_topic_relevance(item, "材料科学")
    assert result["matched_token_count"] > 0


def test_caption_readiness_distinguishes_reported_available_from_supplied():
    item = {"metadata": {"captions_available": True, "language": "ja"}}
    missing = assess_caption_readiness(item, expected_language="ja")
    supplied = assess_caption_readiness(item, transcript_text="材料科学の研究結果を確認します。")
    assert missing["status"] == "captions_reported_available_transcript_not_supplied"
    assert supplied["transcript_supplied"] is True
    assert supplied["transcript_accuracy_verified"] is False


def test_caption_readiness_reports_unknown_and_language_mismatch():
    item = {"metadata": {"language": "ja"}}
    result = assess_caption_readiness(item, transcript_text="Some transcript text", expected_language="en")
    assert "caption_availability_not_reported" in result["flags"]
    assert "language_mismatch" in result["flags"]


def test_caption_readiness_rejects_oversized_or_invalid_transcripts():
    with pytest.raises(ValueError):
        assess_caption_readiness({"metadata": {}}, transcript_text="x" * 20_001)
    with pytest.raises(ValueError):
        assess_caption_readiness({"metadata": {"captions_available": 1}})


def test_translation_review_preserves_both_texts_and_hashes():
    result = build_translation_review(
        record_id="post-1", original_text="耐熱材料の試験", translated_text="Heat-resistant material test",
        source_language="ja", target_language="en", reviewer_id="reviewer-a",
        decision="accepted", protected_terms=["Heat-resistant"],
    )
    assert result["review_state"] == "reviewer_accepted"
    assert result["original_sha256"] == hashlib.sha256("耐熱材料の試験".encode()).hexdigest()
    assert result["machine_translation_performed"] is False
    assert result["translation_accuracy_established"] is False


def test_translation_review_blocks_missing_protected_terms_even_when_reviewer_accepts():
    result = build_translation_review(
        record_id="post-2", original_text="東京での試験", translated_text="A test",
        source_language="ja", target_language="en", reviewer_id="reviewer-a",
        decision="accepted", protected_terms=["Tokyo"],
    )
    assert result["review_state"] == "blocked_protected_terms_missing"
    assert result["reviewer_attested"] is True


def test_translation_review_requires_reviewer_for_decision_and_distinct_languages():
    with pytest.raises(ValueError):
        build_translation_review(
            record_id="a", original_text="A", translated_text="B",
            source_language="en", target_language="fr", decision="accepted",
        )
    with pytest.raises(ValueError):
        build_translation_review(
            record_id="a", original_text="A", translated_text="B",
            source_language="en", target_language="en",
        )


def test_claim_candidates_preserve_unicode_offsets_and_japanese_sentences():
    text = "The sample increased by 12%. 新素材は熱に強い。次の試験が必要です！"
    result = extract_claim_candidates(text)
    assert result["candidate_count"] == 3
    for item in result["candidates"]:
        assert text[item["start_char"]:item["end_char"]] == item["text"]
        assert item["review_status"] == "unverified_candidate"
        assert item["scientific_claim_confirmed"] is False


def test_claim_candidates_keep_decimal_points_inside_numbers():
    result = extract_claim_candidates("The value was 2.75 units. Another measurement followed.")
    assert result["candidate_count"] == 2
    assert "2.75" in result["candidates"][0]["text"]


def test_claim_candidates_are_bounded_and_flag_truncation():
    text = " ".join(f"Sentence {i} has a result." for i in range(250))
    result = extract_claim_candidates(text, max_candidates=50)
    assert result["candidate_count"] == 50
    assert result["truncated"] is True
    with pytest.raises(ValueError):
        extract_claim_candidates("text", max_candidates=201)


def test_review_queue_is_reason_coded_and_deterministic():
    items = [
        {"record_id": "b", "origin_binding_valid": True, "triage_level": "single_signal"},
        {"record_id": "a", "origin_binding_valid": False, "sensitive_field_names_flagged": ["email"]},
        {"record_id": "c", "translation_review_state": "unreviewed"},
    ]
    first = prioritize_review_queue(items)
    second = prioritize_review_queue(items)
    assert first == second
    assert [item["record_id"] for item in first["items"]] == ["a", "c", "b"]
    assert first["items"][0]["priority"] == "critical"
    assert first["scientific_truth_determined"] is False


def test_review_queue_rejects_duplicate_ids_and_invalid_candidate_count():
    with pytest.raises(ValueError):
        prioritize_review_queue([{"record_id": "a"}, {"record_id": "a"}])
    with pytest.raises(ValueError):
        prioritize_review_queue([{"record_id": "a", "claim_candidate_count": -1}])


def test_snapshot_diff_reports_added_absent_and_changed_without_retraction():
    before = [
        {"source_id": "a", "title": "Old"},
        {"source_id": "b", "title": "Still here"},
    ]
    after = [
        {"source_id": "a", "title": "Revised"},
        {"source_id": "c", "title": "New"},
    ]
    result = compare_record_snapshots(before, after)
    assert result["added_source_ids"] == ["c"]
    assert result["absent_from_current_source_ids"] == ["b"]
    assert result["changed_records"][0]["changed_fields"] == ["title"]
    assert result["absence_is_not_retraction"] is True


def test_snapshot_diff_rejects_duplicate_ids_and_oversized_batches():
    with pytest.raises(ValueError):
        compare_record_snapshots([{"source_id": "a"}, {"source_id": "a"}], [])
    with pytest.raises(ValueError):
        compare_record_snapshots([{}] * 501, [])


def test_intake_budget_round_robins_platforms_and_never_truncates():
    records = [
        {"source_id": "yt-1", "platform": "youtube", "metadata": {"text": "x" * 20}},
        {"source_id": "yt-2", "platform": "youtube", "metadata": {"text": "y" * 20}},
        {"source_id": "x-1", "platform": "x", "metadata": {"text": "z" * 20}},
    ]
    result = plan_intake_budget(records, max_records=2, max_text_chars=100, max_serialized_bytes=10_000)
    assert result["selected_indices"] == [2, 0]
    assert result["whole_records_only"] is True
    assert result["excluded_count"] == 1
    assert result["excluded"][0]["reason"] == "record_limit"


def test_intake_budget_reports_text_and_byte_exclusions():
    records = [
        {"source_id": "a", "platform": "youtube", "metadata": {"text": "x" * 30}},
        {"source_id": "b", "platform": "x", "metadata": {"text": "y" * 30}},
    ]
    result = plan_intake_budget(records, max_text_chars=40, max_serialized_bytes=10_000)
    assert result["selected_record_count"] == 1
    assert result["excluded"][0]["reason"] == "text_budget"
    bytes_result = plan_intake_budget(records[:1], max_text_chars=100, max_serialized_bytes=10)
    assert bytes_result["excluded"][0]["reason"] == "serialized_byte_budget"


def test_intake_budget_rejects_invalid_limits_and_non_object_records():
    with pytest.raises(ValueError):
        plan_intake_budget([], max_records=0)
    with pytest.raises(ValueError):
        plan_intake_budget([None])
    with pytest.raises(ValueError):
        plan_intake_budget([{"metadata": []}])


def audit_event(event_id, record_id="r1", event_type="captured"):
    return {
        "event_id": event_id, "event_type": event_type, "record_id": record_id,
        "occurred_at": "2026-11-14T08:00:00+01:00",
        "payload_sha256": "a" * 64,
    }


def test_audit_chain_is_deterministic_and_verifiable():
    events = [audit_event("e1"), audit_event("e2", event_type="reviewed")]
    first = build_audit_chain(events)
    second = build_audit_chain(events)
    assert first == second
    assert verify_audit_chain(first)["valid"] is True
    assert first["raw_source_text_stored"] is False


def test_audit_chain_detects_tampering_and_reordering():
    chain = build_audit_chain([audit_event("e1"), audit_event("e2")])
    tampered = copy.deepcopy(chain)
    tampered["events"][0]["event"]["event_type"] = "deleted"
    assert verify_audit_chain(tampered)["valid"] is False
    reordered = copy.deepcopy(chain)
    reordered["events"].reverse()
    assert verify_audit_chain(reordered)["valid"] is False


def test_audit_chain_rejects_duplicate_ids_bad_timestamps_and_capacity():
    with pytest.raises(ValueError):
        build_audit_chain([audit_event("e1"), audit_event("e1")])
    bad = audit_event("bad")
    bad["occurred_at"] = "2026-11-14T08:00:00"
    with pytest.raises(ValueError):
        build_audit_chain([bad])
    with pytest.raises(ValueError):
        build_audit_chain([audit_event(str(i)) for i in range(1001)])


def test_end_to_end_batch_pipeline_keeps_unverified_status_and_manifest():
    youtube = record(title="Battery material increased by 12%.", captions_available=True)
    x_post = record("x-1", "x", "https://x.com/post/1", title="Battery material increased by 12%.")
    result = prepare_public_media_batch(
        [youtube, x_post], "battery material",
        transcripts={"youtube:yt-1": "Battery material increased by 12 percent in a controlled test."},
    )
    assert result["manifest_sha256"]
    assert result["content_clusters"]["cluster_count"] == 1
    assert result["review_queue"]["item_count"] == 2
    assert result["scientific_evidence_established"] is False
    assert result["automatic_adjudication"] is False
    assert result["media_downloaded"] is False


def test_end_to_end_batch_rejects_origin_mismatch_and_queues_it_for_review():
    bad = record(url="https://unrelated.example/post")
    result = prepare_public_media_batch([bad], "materials")
    assert result["records"] == []
    assert result["rejected"][0]["record_id"] == "youtube:yt-1"
    assert "does not match" in result["rejected"][0]["reason"]
    assert "platform_origin_unverified" in result["review_queue"]["items"][0]["reason_codes"]


def test_end_to_end_batch_is_deterministic_for_same_input():
    items = [record(), record("yt-2", title="A different research post")]
    first = prepare_public_media_batch(items, "material science")
    second = prepare_public_media_batch(items, "material science")
    assert first["manifest_sha256"] == second["manifest_sha256"]
    assert first["findings"] == second["findings"]

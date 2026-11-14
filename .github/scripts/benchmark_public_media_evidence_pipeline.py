#!/usr/bin/env python3
"""Synthetic latency, provenance and bounded-export benchmark for media extensions."""
from __future__ import annotations

import hashlib
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "core"))

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
from ssswet_core.public_media_ingestion import CHANNEL_FIELDS, normalize_public_record

REPEATS = 3
BUDGET_SECONDS = 5.0
CAPTURED = "2026-11-14T08:00:00+00:00"


def make_record(index: int):
    text = (
        f"Measured alloy fatigue test {index} reported a 12 percent change. "
        + ("Contact reviewer@example.org for the public correction note. " if index % 10 == 0 else "")
    )
    return normalize_public_record({
        "platform": "web_forum",
        "visibility": "public",
        "access_mode": "authorized_public_feed",
        "source_url": f"https://forum.example/research/{index}",
        "captured_at": CAPTURED,
        "provider_item_id": f"entry-{index:04d}",
        "content_type": "forum_post",
        "metadata": {
            "thread_id": f"entry-{index:04d}",
            "title": f"Alloy fatigue research {index}",
            "text": text,
            "forum_name": "Public materials forum",
            "public_permalink": f"https://forum.example/research/{index}",
        },
    })


def feed_fixture(count=250):
    items = "".join(
        f"<item><guid>feed-{i}</guid><link>https://forum.example/feed/{i}</link>"
        f"<title>Alloy fatigue {i}</title><description>Measured materials result {i}.</description>"
        f"<pubDate>Sat, 14 Nov 2026 08:00:00 +0000</pubDate></item>"
        for i in range(count)
    )
    return f"<rss version='2.0'><channel><title>Materials feed</title>{items}</channel></rss>"


def transcript_fixture(count=250):
    blocks = []
    for index in range(count):
        start = index * 2_000
        end = start + 1_500
        def stamp(ms):
            hours, remainder = divmod(ms, 3_600_000)
            minutes, remainder = divmod(remainder, 60_000)
            seconds, millis = divmod(remainder, 1_000)
            return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"
        blocks.append(
            f"{index + 1}\n{stamp(start)} --> {stamp(end)}\n"
            f"Measured alloy fatigue result {index}.\n"
        )
    return "\n".join(blocks)


def make_pages(count=250):
    pages = []
    for index in range(count):
        pages.append({
            "sequence": index,
            "provider": "youtube",
            "cursor": f"opaque-cursor-{index - 1}" if index else None,
            "next_cursor": f"opaque-cursor-{index}" if index < count - 1 else None,
            "cursor_reference_id": f"secure-vault:{index - 1}" if index else None,
            "next_cursor_reference_id": f"secure-vault:{index}" if index < count - 1 else None,
            "page_id": f"page-{index:04d}",
            "item_ids": [f"provider-item-{index:04d}"],
            "captured_at": CAPTURED,
        })
    return pages


def make_ledger(records):
    events = []
    for index, record in enumerate(records):
        events.append({
            "event_id": f"publisher-event-{index:04d}",
            "source_id": record["source_id"],
            "event_type": "updated",
            "occurred_at": f"2026-11-14T08:{index // 60:02d}:{index % 60:02d}+00:00",
            "prior_snapshot_sha256": record["snapshot_sha256"],
            "new_snapshot_sha256": hashlib.sha256(f"revised-{index}".encode()).hexdigest(),
            "publisher_reference_url": f"https://forum.example/corrections/{index}",
            "publisher_statement": "Publisher declared a metadata update.",
            "publisher_declared": True,
        })
    return build_publisher_status_ledger(events)


def fixtures():
    records = [make_record(index) for index in range(250)]
    claim_rows = []
    for record in records:
        text_value = record["metadata"]["text"]
        bound = bind_claim_candidates_to_source(record, text_value, language="en")
        claim_rows.extend(bound["claims"])
    language_rows = [
        {
            "source_id": record["source_id"],
            **assess_language_script_consistency(record["metadata"]["text"], "en"),
        }
        for record in records
    ]
    transcript = transcript_fixture()
    parsed_transcript = parse_caption_transcript(transcript, format_hint="srt", language="en")
    cues = [
        {"source_id": records[0]["source_id"], **cue}
        for cue in parsed_transcript["cues"]
    ]
    ledger = make_ledger(records)
    queue = {
        "items": [{
            "record_id": record["source_id"],
            "priority": "medium",
            "reason_codes": ["claim_review_pending"],
            "claim_candidate_count": 1,
        } for record in records],
    }
    return records, claim_rows, language_rows, cues, ledger, queue, transcript


def main():
    records, claims, languages, cues, ledger, queue, transcript = fixtures()
    feed = feed_fixture()
    pages = make_pages()
    headlines = [
        ("Battery material test results", "The battery material test measured a result.", "en")
        for _ in range(250)
    ]
    privacy_texts = [
        f"Public research note {index} reviewer@example.org"
        for index in range(250)
    ]

    workloads = [
        ("rss_import_250", lambda: parse_public_feed(
            feed, captured_at=CAPTURED, approved_hosts=["forum.example"]
        )),
        ("adapter_contracts_14", lambda: [
            audit_adapter_contract(
                platform, access_mode=next(iter(sorted({
                    "youtube": {"official_api"}, "x": {"official_api"},
                    "instagram": {"approved_meta_graph_api"}, "facebook": {"approved_meta_graph_api"},
                    "threads": {"approved_threads_api"}, "bluesky": {"public_atproto_appview"},
                    "reddit": {"official_api"}, "snapchat": {"approved_public_discovery"},
                    "mewe": {"authorized_public_feed"}, "weibo": {"official_api"},
                    "bilibili": {"official_api"}, "niconico": {"official_api"},
                    "qiita": {"official_api"}, "web_forum": {"authorized_public_feed"},
                }[platform]))),
                declared_fields=sorted(CHANNEL_FIELDS[platform]),
            )
            for platform in sorted(CHANNEL_FIELDS)
        ]),
        ("pagination_chain_250", lambda: verify_pagination_checkpoint_chain(
            build_pagination_checkpoint_chain(pages)
        )),
        ("language_audit_250", lambda: [
            assess_language_script_consistency(record["metadata"]["text"], "en")
            for record in records
        ]),
        ("headline_context_250", lambda: [
            audit_headline_context(title, body, language=language)
            for title, body, language in headlines
        ]),
        ("transcript_parse_250", lambda: parse_caption_transcript(
            transcript, format_hint="srt", language="en"
        )),
        ("claim_binding_250", lambda: [
            bind_claim_candidates_to_source(record, record["metadata"]["text"], language="en")
            for record in records
        ]),
        ("publisher_ledger_250", lambda: verify_publisher_status_ledger(ledger)),
        ("privacy_scan_250", lambda: [
            scan_public_text_privacy(value) for value in privacy_texts
        ]),
        ("review_packet_250", lambda: build_human_review_packet(
            records,
            claim_bindings=claims,
            transcript_cues=cues,
            language_audits=languages,
            publisher_status_ledger=ledger,
            review_queue=queue,
        )),
    ]

    results = []
    final_outputs = {}
    for name, workload in workloads:
        durations, output = [], None
        for _ in range(REPEATS):
            started = time.perf_counter()
            output = workload()
            durations.append(time.perf_counter() - started)
        final_outputs[name] = output
        maximum = max(durations)
        results.append({
            "workload": name,
            "repeats": REPEATS,
            "median_ms": round(statistics.median(durations) * 1000, 3),
            "maximum_ms": round(maximum * 1000, 3),
            "budget_ms": int(BUDGET_SECONDS * 1000),
            "within_budget": maximum <= BUDGET_SECONDS,
        })

    packet_250 = final_outputs["review_packet_250"]
    ledger_125 = make_ledger(records[:125])
    packet_125 = build_human_review_packet(
        records[:125],
        claim_bindings=claims[:len(claims) // 2],
        language_audits=languages[:125],
        publisher_status_ledger=ledger_125,
        review_queue={"items": queue["items"][:125]},
    )
    feed_result = final_outputs["rss_import_250"]
    checkpoint_result = final_outputs["pagination_chain_250"]
    ledger_result = final_outputs["publisher_ledger_250"]
    claim_source_ids = {item["source_id"] for item in claims}
    provenance_rate = len(claim_source_ids) / len(records) if records else 1.0
    privacy_findings = sum(
        scan_public_text_privacy(value)["finding_count"] for value in privacy_texts
    )
    quality = {
        "feed_import": {
            "entries": feed_result["entry_count"],
            "accepted": feed_result["accepted_count"],
            "retention_rate": round(
                feed_result["accepted_count"] / feed_result["entry_count"], 4
            ) if feed_result["entry_count"] else 1.0,
        },
        "pagination": {
            "pages": len(pages),
            "chain_valid": checkpoint_result["valid"],
            "raw_cursor_tokens_persisted": False,
        },
        "claim_provenance": {
            "source_records": len(records),
            "sources_with_claim_bindings": len(claim_source_ids),
            "source_coverage_rate": round(provenance_rate, 4),
            "claim_count": len(claims),
        },
        "publisher_status": {
            "events": ledger["event_count"],
            "chain_valid": ledger_result["valid"],
            "source_records_deleted": False,
        },
        "privacy": {
            "synthetic_texts_scanned": len(privacy_texts),
            "findings": privacy_findings,
            "matched_values_echoed": False,
        },
        "review_packet_storage": {
            "records_125_bytes": packet_125["canonical_bytes"],
            "records_250_bytes": packet_250["canonical_bytes"],
            "growth_ratio_125_to_250": round(
                packet_250["canonical_bytes"] / packet_125["canonical_bytes"], 4
            ) if packet_125["canonical_bytes"] else None,
            "packet_source_count": len(packet_250["records"]),
            "packet_claim_count": len(packet_250["claim_bindings"]),
            "packet_media_bytes_included": packet_250["raw_media_included"],
        },
        "contradiction_adjudication": False,
        "scientific_validity_established": False,
        "intelligence_gain_claimed": False,
    }
    print(json.dumps({
        "benchmark": "SSSWET public-media evidence pipeline expansion",
        "results": results,
        "quality_and_retention": quality,
        "measurement": "synthetic fixtures; no network, media downloads or external services",
    }, indent=2))

    if feed_result["accepted_count"] != 250:
        raise SystemExit("Feed retention acceptance failed")
    if not checkpoint_result["valid"]:
        raise SystemExit("Pagination checkpoint integrity acceptance failed")
    if provenance_rate != 1.0 or len(claims) < len(records):
        raise SystemExit("Claim/source provenance retention acceptance failed")
    if not ledger_result["valid"]:
        raise SystemExit("Publisher status ledger integrity acceptance failed")
    if len(packet_250["records"]) != 250 or len(packet_250["claim_bindings"]) != len(claims):
        raise SystemExit("Review packet retention acceptance failed")
    failed = [item["workload"] for item in results if not item["within_budget"]]
    if failed:
        raise SystemExit("Latency budget exceeded: " + ", ".join(failed))


if __name__ == "__main__":
    main()

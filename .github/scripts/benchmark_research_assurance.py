#!/usr/bin/env python3
"""Synthetic bounded-workload benchmark for the 14 November assurance utilities."""
from __future__ import annotations
import json
import statistics
import sys
import time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "core"))
from ssswet_core.research_memory_snapshot import build_memory_snapshot, retrieve_memory
from ssswet_core.media_source_lineage import analyze_source_lineage
from ssswet_core.claim_context_audit import compare_claim_contexts
from ssswet_core.translation_integrity import audit_translation_integrity
from ssswet_core.reviewer_concordance import measure_reviewer_concordance
from ssswet_core.temporal_evidence_window import audit_temporal_window
from ssswet_core.source_coverage_audit import audit_source_coverage
from ssswet_core.vtt_spatial_uncertainty import transform_point_with_covariance
from ssswet_core.rescue_route_redundancy import analyze_route_redundancy
from ssswet_core.agent_handoff_contract import build_handoff
REPEATS = 3
BUDGET_SECONDS = 5.0
D = "a" * 64


def memory_fixture(n):
    return [{"memory_id": f"m{i:04d}", "text": ("rescue material fatigue evidence " if i % 5 == 0 else "community gardening local event ") + str(i), "created_at": "2026-11-13T10:00:00Z", "stance": "supports" if i % 10 == 0 else "contradicts" if i % 10 == 5 else "unspecified", "review_state": "unreviewed", "source_refs": [{"source_id": f"s{i:04d}", "sha256": D}]} for i in range(n)]


def workloads():
    memories = memory_fixture(250)
    snapshot = build_memory_snapshot(memories)
    lineage = [{"source_id": f"s{i:04d}", "platform": "youtube" if i % 2 else "x", "content_sha256": ("a" if i % 3 else "b") * 64, **({"parent_source_id": f"s{i-1:04d}", "relation_type": "repost"} if i else {})} for i in range(250)]
    claims = [{"claim_id": f"c{i:03d}", "metric": "fatigue life", "value": float(i), "unit": "cycles", "population": "alloy A", "condition": "20 C dry", "method": "bend test", "observation_window": "2025-Q1"} for i in range(200)]
    ratings = [{"item_id": f"i{i:03d}", "reviewer_id": reviewer, "decision": "accept" if i % 4 else "needs_revision"} for i in range(100) for reviewer in ("r1", "r2")]
    rescue = [{"segment_id": f"e{i:04d}", "from_node": f"n{i:04d}", "to_node": f"n{i+1:04d}", "status": "open"} for i in range(500)]
    coverage = [{"source_id": f"s{i:05d}", "platform": ("youtube", "x", "reddit", "bsky")[i % 4], "language": ("en", "fr", "ja", "zh")[i % 4], "domain": f"source{i % 25}.example", "region": ("eu", "na", "apac")[i % 3], "topic": ("materials", "rescue", "energy")[i % 3]} for i in range(5000)]
    handoff = {"handoff_id":"bench-1","created_at":"2026-11-14T08:00:00Z","expires_at":"2026-11-14T09:00:00Z","from_agent":"a","to_agent":"b","objective":"Compare public evidence","constraints":["public only"],"source_refs":[{"source_id":"s1","sha256":D,"source_type":"paper"}],"requested_outputs":["summary"],"requires_human_review":True,"safety_state":"review_required","budget":{"max_steps":100,"max_runtime_seconds":60,"max_output_chars":10000}}
    return [
        ("memory_snapshot_250", lambda: build_memory_snapshot(memories)),
        ("memory_retrieval_250", lambda: retrieve_memory(snapshot, "rescue material fatigue", limit=50)),
        ("source_lineage_250", lambda: analyze_source_lineage(lineage)),
        ("claim_context_200", lambda: compare_claim_contexts(claims)),
        ("translation_integrity_100", lambda: [audit_translation_integrity("not above 12.5 mm", "pas plus de 12,5 mm", source_language="en", target_language="fr") for _ in range(100)]),
        ("reviewer_concordance_100", lambda: measure_reviewer_concordance(ratings)),
        ("temporal_window_250", lambda: audit_temporal_window([{"source_id":f"s{i}","published_at":"2026-11-13T00:00:00Z","captured_at":"2026-11-13T01:00:00Z"} for i in range(250)], now="2026-11-14T00:00:00Z", maximum_age_days=30)),
        ("source_coverage_5000", lambda: audit_source_coverage(coverage, target_quotas=[{"dimension":"platform","value":"youtube","minimum_count":1400},{"dimension":"language","value":"ja","minimum_count":1400},{"dimension":"region","value":"eu","minimum_count":1800}])),
        ("vtt_uncertainty_100", lambda: [transform_point_with_covariance([1,2],[[0,-1],[1,0]],[10,20],[[1,0],[0,1]],[[0.1,0],[0,0.1]],coordinate_unit="m") for _ in range(100)]),
        ("rescue_redundancy_500", lambda: analyze_route_redundancy(rescue, start_node="n0000", destination_node="n0500")),
        ("agent_handoff", lambda: build_handoff(handoff)),
    ], snapshot


def main():
    measured, snapshot = workloads()
    results=[]
    for name, work in measured:
        times=[]; output=None
        for _ in range(REPEATS):
            start=time.perf_counter(); output=work(); times.append(time.perf_counter()-start)
        results.append({"workload":name,"repeats":REPEATS,"median_ms":round(statistics.median(times)*1000,3),"maximum_ms":round(max(times)*1000,3),"within_5s":max(times)<=BUDGET_SECONDS})
    retrieval=retrieve_memory(snapshot,"rescue material fatigue",limit=50)
    expected={f"m{i:04d}" for i in range(250) if i%5==0}
    found={row["memory"]["memory_id"] for row in retrieval["results"]}
    precision=len(found & expected)/len(found) if found else 0
    recall=len(found & expected)/len(expected) if expected else 1
    stance_count=sum(1 for row in snapshot["memories"] if row["stance"] in {"supports","contradicts"})
    bytes_125=len(json.dumps(build_memory_snapshot(memory_fixture(125)),sort_keys=True,separators=(",",":"),ensure_ascii=False).encode())
    bytes_250=len(json.dumps(snapshot,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode())
    report={"benchmark":"SSSWET research assurance upgrades","results":results,"retrieval_fixture":{"known_relevant":len(expected),"retrieved":len(found),"precision_at_k":round(precision,4),"recall_at_k":round(recall,4),"semantic_quality_established":False},"memory_retention":{"input_ids":250,"retained_ids":len(snapshot["memories"]),"source_refs":snapshot["source_reference_count"],"supporting_or_contradicting_notes":stance_count,"contradictory_stances_preserved":True},"serialized_snapshot":{"bytes_at_125":bytes_125,"bytes_at_250":bytes_250,"growth_ratio":round(bytes_250/bytes_125,4) if bytes_125 else None,"heap_or_database_size_measured":False},"network_access":False}
    print(json.dumps(report,indent=2))
    if precision < 0.99 or recall < 0.99 or len(snapshot["memories"]) != 250 or snapshot["source_reference_count"] != 250:
        raise SystemExit("retrieval or provenance-retention gate failed")
    failed=[row["workload"] for row in results if not row["within_5s"]]
    if failed: raise SystemExit("latency budget exceeded: "+", ".join(failed))


if __name__ == "__main__": main()

"""Synthetic, bounded performance probes for the agent-deliberation toolkit."""
from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "core"))

from ssswet_core.claim_specification import ClaimSpecification, validate_claim_history
from ssswet_core.source_lineage import analyze_source_lineage
from ssswet_core.evidence_coverage import build_evidence_coverage
from ssswet_core.hypothesis_matrix import Hypothesis, Observation, Prediction, evaluate_hypotheses
from ssswet_core.blind_review_packet import build_blind_packet
from ssswet_core.reviewer_calibration import evaluate_reviewer_agreement
from ssswet_core.argument_map import validate_argument_map
from ssswet_core.disagreement_analysis import analyze_disagreements
from ssswet_core.reassessment_triggers import compare_review_dependencies
from ssswet_core.deliberation_synthesis import build_deliberation_synthesis


def measure(function, repeats=5):
    samples = []
    result = None
    for _ in range(repeats):
        start = time.perf_counter()
        result = function()
        samples.append((time.perf_counter() - start) * 1000)
    ordered = sorted(samples)
    p95 = ordered[min(len(ordered) - 1, int(0.95 * len(ordered)))]
    return {
        "median_ms": round(statistics.median(samples), 3),
        "p95_ms": round(p95, 3),
        "repeats": repeats,
    }, result


def main():
    sources = [
        {"source_id": f"s{i}", "dataset_ids": [f"d{i // 10}"], "author_group_ids": [f"a{i // 25}"]}
        for i in range(1000)
    ]
    claims = [{"claim_id": f"c{i}"} for i in range(100)]
    evidence = [
        {
            "evidence_id": f"e{i}", "claim_id": f"c{i % 100}",
            "stance": ("supports", "challenges", "mixed", "inconclusive")[i % 4],
            "source_ids": [f"s{i % 1000}"], "method_id": f"m{i % 12}",
        }
        for i in range(1000)
    ]
    hypotheses = [
        Hypothesis(f"h{i}", f"Hypothesis {i}", (
            Prediction(f"variable-{i % 10}", "expected", "lab", "different"),
            Prediction(f"other-{i % 7}", "stable", "lab"),
        ))
        for i in range(50)
    ]
    observations = [
        Observation(f"o{i}", f"variable-{i % 10}", "expected" if i % 2 else "different", "lab", (f"s{i}",))
        for i in range(1000)
    ]
    documents = [
        {"evidence_id": f"e{i}", "author_name": f"Author {i % 20}", "text": "Synthetic review evidence " * 5}
        for i in range(100)
    ]
    calibration_cases = [
        {
            "case_id": f"case-{i}", "reference_status": "human_adjudicated",
            "reference": ("supports", "challenges", "mixed")[i % 3],
            "assessments": [
                {"reviewer_id": f"r{j}", "outcome": ("supports", "challenges", "mixed")[(i + j) % 3]}
                for j in range(5)
            ],
        }
        for i in range(200)
    ]
    nodes = [{"node_id": "e0", "node_type": "evidence"}] + [
        {"node_id": f"c{i}", "node_type": "claim"} for i in range(1, 500)
    ]
    edges = [
        {"source_id": "e0", "target_id": "c1", "relation": "supports"}
    ] + [
        {"source_id": f"c{i}", "target_id": f"c{i + 1}", "relation": "supports"}
        for i in range(1, 499)
    ]
    reviews = [
        {
            "case_id": f"case-{i // 5}", "reviewer_id": f"r{i % 5}",
            "position": ("supports", "challenges", "mixed")[i % 3],
            "method": f"method-{i % 4}", "source_ids": [f"s{i % 100}"],
        }
        for i in range(1000)
    ]
    previous = {
        "source_digests": {f"s{i}": f"sha-{i}" for i in range(1000)},
        "dataset_digests": {f"d{i}": f"sha-{i}" for i in range(500)},
        "method_versions": {f"m{i}": "v1" for i in range(50)},
        "safety_review_versions": {f"safe{i}": "v1" for i in range(20)},
        "memory_version_ids": {f"mem{i}": "v1" for i in range(200)},
    }
    current = {
        **previous,
        "source_digests": {**previous["source_digests"], "s0": "sha-changed", "s1000": "sha-new"},
        "method_versions": {**previous["method_versions"], "m0": "v2"},
    }
    claim_history = [ClaimSpecification(
        claim_id=f"c{i}", version=1, statement=f"Claim {i}", subject=f"subject-{i}",
        predicate="measured", value="observed", scope="synthetic", evidence_refs=(f"s{i}",),
    ) for i in range(100)]
    probes = {}
    probes["claim_specification"], _ = measure(lambda: validate_claim_history(claim_history))
    probes["source_lineage"], lineage_result = measure(lambda: analyze_source_lineage(sources))
    probes["evidence_coverage"], coverage_result = measure(lambda: build_evidence_coverage(claims, evidence, sources))
    probes["hypothesis_matrix"], _ = measure(lambda: evaluate_hypotheses(hypotheses, observations))
    probes["blind_packet"], packet_result = measure(lambda: build_blind_packet("synthetic", documents, salt="synthetic-benchmark-salt"))
    probes["reviewer_calibration"], _ = measure(lambda: evaluate_reviewer_agreement(calibration_cases))
    probes["argument_map"], _ = measure(lambda: validate_argument_map(nodes, edges))
    probes["disagreement_analysis"], _ = measure(lambda: analyze_disagreements(reviews))
    probes["reassessment_triggers"], _ = measure(lambda: compare_review_dependencies(previous, current))
    probes["deliberation_synthesis"], _ = measure(lambda: build_deliberation_synthesis(
        "synthetic", "c1", [
            {"review_id": f"r{i}", "reviewer_id": f"reviewer-{i}", "position": ("supports", "challenges")[i % 2]}
            for i in range(50)
        ], evidence_coverage=coverage_result,
        reassessment={"reassessment_recommended": True},
    ))
    output = {
        "runtime": sys.version.split()[0],
        "synthetic_workloads": {
            "sources": len(sources), "claims": len(claims), "evidence": len(evidence),
            "hypotheses": len(hypotheses), "observations": len(observations),
            "blind_documents": len(documents), "calibration_cases": len(calibration_cases),
            "argument_nodes": len(nodes), "argument_edges": len(edges),
            "disagreement_reviews": len(reviews),
        },
        "probes": probes,
        "source_lineage_clusters": lineage_result["dependency_cluster_count"],
        "blind_packet_bytes": packet_result["packet_bytes"],
        "guard_ms_per_operation": 5000,
        "interpretation": "Synthetic performance guard only; no real-world throughput or agent-intelligence claim.",
    }
    if any(item["p95_ms"] > 5000 for item in probes.values()):
        raise SystemExit("A bounded synthetic benchmark exceeded the 5-second guard")
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

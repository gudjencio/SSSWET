"""Claim-by-claim evidence coverage without opaque composite scores."""
from __future__ import annotations

from collections import defaultdict
from .source_lineage import analyze_source_lineage


MAX_CLAIMS = 200
MAX_EVIDENCE = 5000
STANCES = {"supports", "challenges", "mixed", "inconclusive"}


def build_evidence_coverage(
    claims: list[dict], evidence: list[dict], source_metadata: list[dict] | None = None,
) -> dict:
    if not isinstance(claims, list) or not 1 <= len(claims) <= MAX_CLAIMS:
        raise ValueError(f"claims must contain 1 to {MAX_CLAIMS} entries")
    if not isinstance(evidence, list) or len(evidence) > MAX_EVIDENCE:
        raise ValueError(f"evidence is limited to {MAX_EVIDENCE} entries")
    claim_ids = []
    for claim in claims:
        if not isinstance(claim, dict) or not isinstance(claim.get("claim_id"), str) or not claim["claim_id"].strip():
            raise ValueError("every claim requires a claim_id")
        claim_ids.append(claim["claim_id"].strip())
    if len(set(claim_ids)) != len(claim_ids):
        raise ValueError("claim IDs must be unique")

    lineage = analyze_source_lineage(source_metadata or [])
    if not lineage["valid"]:
        raise ValueError("source lineage contains a cycle")
    source_to_cluster = lineage.get("source_to_cluster", {})
    rows = defaultdict(list)
    for item in evidence:
        if not isinstance(item, dict):
            raise ValueError("every evidence item must be a dictionary")
        evidence_id = item.get("evidence_id")
        claim_id = item.get("claim_id")
        stance = item.get("stance")
        if not isinstance(evidence_id, str) or not evidence_id.strip():
            raise ValueError("every evidence item requires an evidence_id")
        if claim_id not in set(claim_ids):
            raise ValueError(f"evidence references unknown claim: {claim_id}")
        if stance not in STANCES:
            raise ValueError(f"unsupported evidence stance: {stance}")
        source_ids = item.get("source_ids", [])
        if not isinstance(source_ids, list) or any(not isinstance(value, str) or not value.strip() for value in source_ids):
            raise ValueError("source_ids must be a list of non-empty identifiers")
        rows[claim_id].append(item)

    reports = []
    for claim_id in claim_ids:
        items = rows[claim_id]
        counts = {stance: sum(item["stance"] == stance for item in items) for stance in sorted(STANCES)}
        groups = {stance: set() for stance in STANCES}
        unresolved = 0
        methods, datasets = set(), set()
        for item in items:
            source_ids = item.get("source_ids", [])
            explicit_group = str(item.get("provenance_group", "")).strip()
            if explicit_group:
                groups[item["stance"]].add("declared:" + explicit_group)
            else:
                resolved = {source_to_cluster[source] for source in source_ids if source in source_to_cluster}
                groups[item["stance"]].update(resolved)
                if not resolved:
                    unresolved += 1
            method = str(item.get("method_id", "")).strip()
            dataset_ids = item.get("dataset_ids", [])
            if method:
                methods.add(method)
            if isinstance(dataset_ids, list):
                datasets.update(str(value).strip() for value in dataset_ids if str(value).strip())
        gaps = []
        if not counts["supports"]:
            gaps.append("no_supporting_evidence_recorded")
        if not counts["challenges"]:
            gaps.append("no_challenging_evidence_recorded")
        if not groups["supports"]:
            gaps.append("no_resolved_supporting_provenance_group")
        if unresolved:
            gaps.append("some_evidence_has_unresolved_provenance")
        reports.append({
            "claim_id": claim_id, "evidence_count": len(items),
            "stance_counts": counts,
            "supporting_lineage_groups": sorted(groups["supports"]),
            "challenging_lineage_groups": sorted(groups["challenges"]),
            "mixed_lineage_groups": sorted(groups["mixed"]),
            "inconclusive_lineage_groups": sorted(groups["inconclusive"]),
            "independent_supporting_group_count": len(groups["supports"]),
            "independent_challenging_group_count": len(groups["challenges"]),
            "distinct_method_count": len(methods),
            "distinct_dataset_count": len(datasets),
            "unresolved_provenance_evidence_count": unresolved,
            "coverage_gaps": gaps,
            "coverage_is_not_a_truth_score": True,
        })
    return {
        "claims": reports, "claim_count": len(reports),
        "evidence_count": len(evidence),
        "source_lineage_cluster_count": lineage["dependency_cluster_count"],
        "publisher_similarity_used": False,
        "automatic_claim_adjudication": False,
        "scientific_validity_established": False,
    }

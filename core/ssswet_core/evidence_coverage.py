"""Claim-level evidence coverage audit with provenance-group deduplication."""
from __future__ import annotations

from typing import Any

MAX_RECORDS = 2_000
_STANCES = {"supports", "contradicts", "neutral", "unclear"}
_EVIDENCE_STATES = {"active", "under_review", "withdrawn", "superseded"}


def _id(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > 200:
        raise ValueError(f"{field} must contain 1 to 200 characters")
    return value.strip()


def audit_claim_coverage(
    claims: list[dict[str, Any]], evidence: list[dict[str, Any]],
    links: list[dict[str, Any]],
) -> dict[str, Any]:
    """Audit explicit links; never infer support from source titles or metadata."""
    for name, records in (("claims", claims), ("evidence", evidence), ("links", links)):
        if not isinstance(records, list) or len(records) > MAX_RECORDS:
            raise ValueError(f"{name} must be a list of at most {MAX_RECORDS} records")
    claim_map, evidence_map = {}, {}
    for item in claims:
        if not isinstance(item, dict):
            raise ValueError("every claim must be an object")
        key = _id(item.get("claim_id"), "claim_id")
        if key in claim_map:
            raise ValueError("claim IDs must be unique")
        claim_map[key] = _id(item.get("text"), "claim text")
    for item in evidence:
        if not isinstance(item, dict):
            raise ValueError("every evidence record must be an object")
        key = _id(item.get("evidence_id"), "evidence_id")
        if key in evidence_map:
            raise ValueError("evidence IDs must be unique")
        state = item.get("state", "active")
        if state not in _EVIDENCE_STATES:
            raise ValueError("unsupported evidence state")
        evidence_map[key] = {
            "source_id": _id(item.get("source_id"), "source_id"),
            "provenance_group": _id(item.get("provenance_group"), "provenance_group"),
            "state": state,
        }

    seen_links = set()
    per_claim = {
        key: {
            "claim_id": key, "text": value, "supporting_groups": set(),
            "contradicting_groups": set(), "neutral_groups": set(),
            "under_review_groups": set(), "withdrawn_evidence_ids": [],
            "unresolved_evidence_ids": [],
        } for key, value in claim_map.items()
    }
    dangling = []
    for link in links:
        if not isinstance(link, dict):
            raise ValueError("every evidence link must be an object")
        claim_id = _id(link.get("claim_id"), "link.claim_id")
        evidence_id = _id(link.get("evidence_id"), "link.evidence_id")
        stance = link.get("stance")
        if stance not in _STANCES:
            raise ValueError("link stance must be supports, contradicts, neutral or unclear")
        pair = (claim_id, evidence_id, stance)
        if pair in seen_links:
            continue
        seen_links.add(pair)
        if claim_id not in claim_map or evidence_id not in evidence_map:
            dangling.append({"claim_id": claim_id, "evidence_id": evidence_id, "stance": stance})
            if claim_id in per_claim:
                per_claim[claim_id]["unresolved_evidence_ids"].append(evidence_id)
            continue
        record = evidence_map[evidence_id]
        target = per_claim[claim_id]
        if record["state"] in {"withdrawn", "superseded"}:
            target["withdrawn_evidence_ids"].append(evidence_id)
            continue
        group = record["provenance_group"]
        if record["state"] == "under_review":
            target["under_review_groups"].add(group)
        if stance == "supports":
            target["supporting_groups"].add(group)
        elif stance == "contradicts":
            target["contradicting_groups"].add(group)
        elif stance == "neutral":
            target["neutral_groups"].add(group)

    results = []
    for claim_id in sorted(per_claim):
        item = per_claim[claim_id]
        support = sorted(item["supporting_groups"])
        contradiction = sorted(item["contradicting_groups"])
        row = {
            "claim_id": claim_id,
            "supporting_independent_group_count": len(support),
            "supporting_provenance_groups": support,
            "contradicting_independent_group_count": len(contradiction),
            "contradicting_provenance_groups": contradiction,
            "neutral_group_count": len(item["neutral_groups"]),
            "under_review_group_count": len(item["under_review_groups"]),
            "withdrawn_evidence_ids": sorted(item["withdrawn_evidence_ids"]),
            "unresolved_evidence_ids": sorted(item["unresolved_evidence_ids"]),
            "unsupported_by_recorded_links": not support,
            "counterevidence_present": bool(contradiction),
            "contested": bool(support and contradiction),
            "single_group_support_concentration": len(support) == 1,
        }
        results.append(row)
    return {
        "claims": results,
        "claim_count": len(results),
        "dangling_links": dangling,
        "duplicate_links_ignored": len(links) - len(seen_links),
        "unsupported_claim_ids": [item["claim_id"] for item in results if item["unsupported_by_recorded_links"]],
        "contested_claim_ids": [item["claim_id"] for item in results if item["contested"]],
        "automatic_adjudication": False,
        "scientific_truth_score": None,
    }

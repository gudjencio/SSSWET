"""Provenance-aware support/contradiction matrix for structured claims."""
from __future__ import annotations

MAX_CLAIMS = 500
MAX_SOURCES = 2_000
MAX_LINKS = 5_000
RELATIONS = {"supports", "contradicts", "neutral"}
STATES = {"active", "withdrawn", "superseded", "under_review"}


def _records(values, field, maximum):
    if not isinstance(values, list) or len(values) > maximum:
        raise ValueError(f"{field} must be a list of at most {maximum} records")
    if any(not isinstance(item, dict) for item in values):
        raise ValueError(f"every {field} item must be an object")
    return values


def _identifier(value, field):
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > 240:
        raise ValueError(f"{field} must contain 1 to 240 characters")
    return value.strip()


def build_claim_evidence_matrix(claims: list[dict], sources: list[dict], links: list[dict]) -> dict:
    claims = _records(claims, "claims", MAX_CLAIMS)
    sources = _records(sources, "sources", MAX_SOURCES)
    links = _records(links, "links", MAX_LINKS)
    claim_map = {}
    for item in claims:
        claim_id = _identifier(item.get("claim_id"), "claim_id")
        if claim_id in claim_map:
            raise ValueError("claim identifiers must be unique")
        claim_map[claim_id] = item
    source_map = {}
    for item in sources:
        source_id = _identifier(item.get("source_id"), "source_id")
        if source_id in source_map:
            raise ValueError("source identifiers must be unique")
        group = item.get("provenance_group", "")
        if group is not None and (not isinstance(group, str) or len(group) > 240):
            raise ValueError("provenance_group must be a string of at most 240 characters")
        source_map[source_id] = item
    seen_links = set()
    report = {
        claim_id: {
            "claim_id": claim_id,
            "support_source_ids": set(),
            "support_provenance_groups": set(),
            "contradiction_source_ids": set(),
            "contradiction_provenance_groups": set(),
            "neutral_source_ids": set(),
            "withdrawn_evidence_refs": set(),
            "under_review_evidence_refs": set(),
            "unresolved_source_refs": set(),
            "unknown_provenance_group_source_ids": set(),
        }
        for claim_id in claim_map
    }
    normalized_links = []
    for link in links:
        claim_id = _identifier(link.get("claim_id"), "link.claim_id")
        source_id = _identifier(link.get("source_id"), "link.source_id")
        relation = link.get("relation")
        state = link.get("state", "active")
        evidence_ref = _identifier(link.get("evidence_ref"), "link.evidence_ref")
        if claim_id not in claim_map:
            raise ValueError(f"link references unknown claim: {claim_id}")
        if relation not in RELATIONS or state not in STATES:
            raise ValueError("unsupported evidence relation or state")
        key = (claim_id, source_id, relation, evidence_ref)
        if key in seen_links:
            raise ValueError("duplicate claim/source/relation/evidence link")
        seen_links.add(key)
        row = report[claim_id]
        if source_id not in source_map:
            row["unresolved_source_refs"].add(source_id)
            normalized_links.append({"claim_id": claim_id, "source_id": source_id, "relation": relation, "state": state, "evidence_ref": evidence_ref, "source_resolved": False})
            continue
        source = source_map[source_id]
        group = str(source.get("provenance_group") or "").strip()
        if state == "withdrawn":
            row["withdrawn_evidence_refs"].add(evidence_ref)
        elif state == "under_review":
            row["under_review_evidence_refs"].add(evidence_ref)
        elif state == "active":
            if not group:
                row["unknown_provenance_group_source_ids"].add(source_id)
                group = "unknown:" + source_id
            if relation == "supports":
                row["support_source_ids"].add(source_id)
                row["support_provenance_groups"].add(group)
            elif relation == "contradicts":
                row["contradiction_source_ids"].add(source_id)
                row["contradiction_provenance_groups"].add(group)
            else:
                row["neutral_source_ids"].add(source_id)
        normalized_links.append({"claim_id": claim_id, "source_id": source_id, "relation": relation, "state": state, "evidence_ref": evidence_ref, "source_resolved": True})
    output = []
    for claim_id in sorted(report):
        row = report[claim_id]
        for key in tuple(row):
            if isinstance(row[key], set):
                row[key] = sorted(row[key])
        row.update({
            "support_independent_group_count": len(row["support_provenance_groups"]),
            "contradiction_independent_group_count": len(row["contradiction_provenance_groups"]),
            "mixed_support_and_contradiction": bool(row["support_source_ids"] and row["contradiction_source_ids"]),
            "provenance_group_completeness": not bool(row["unknown_provenance_group_source_ids"]),
            "scientific_truth_score": None,
            "claim_adjudicated": False,
        })
        output.append(row)
    return {
        "claims": output,
        "claim_count": len(output),
        "source_count": len(source_map),
        "link_count": len(normalized_links),
        "unresolved_link_count": sum(not item["source_resolved"] for item in normalized_links),
        "links": normalized_links,
        "duplicate_publishers_counted_as_one_group": True,
        "support_and_contradiction_retained_separately": True,
        "withdrawn_evidence_reactivated": False,
        "scientific_validity_established": False,
        "automatic_adjudication": False,
    }

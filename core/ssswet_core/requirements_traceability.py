"""Trace requirements to reviewed verification evidence without certifying designs."""
from __future__ import annotations

MAX_REQUIREMENTS = 1_000
MAX_EVIDENCE = 5_000
_METHODS = {"analysis", "test", "inspection", "demonstration"}
_RESULTS = {"pass", "fail", "inconclusive"}


def build_traceability_matrix(requirements: list[dict], evidence: list[dict]) -> dict:
    if not isinstance(requirements, list) or len(requirements) > MAX_REQUIREMENTS:
        raise ValueError(f"requirements must be a list of at most {MAX_REQUIREMENTS} entries")
    if not isinstance(evidence, list) or len(evidence) > MAX_EVIDENCE:
        raise ValueError(f"evidence must be a list of at most {MAX_EVIDENCE} entries")
    req_by_id = {}
    for requirement in requirements:
        if not isinstance(requirement, dict):
            raise ValueError("each requirement must be an object")
        identifier = requirement.get("requirement_id")
        if not isinstance(identifier, str) or not identifier.strip() or len(identifier) > 200 or identifier in req_by_id:
            raise ValueError("requirement_id values must be unique non-empty strings")
        if not isinstance(requirement.get("description"), str) or not requirement["description"].strip() or len(requirement["description"]) > 2_000:
            raise ValueError("each requirement needs a description")
        if requirement.get("verification_method") not in _METHODS:
            raise ValueError("verification_method must be analysis, test, inspection or demonstration")
        refs = requirement.get("evidence_refs", [])
        if not isinstance(refs, list) or len(refs) > 100 or any(not isinstance(ref, str) or not ref.strip() or len(ref) > 300 for ref in refs):
            raise ValueError("evidence_refs must be a bounded list of non-empty identifiers")
        req_by_id[identifier] = {**requirement, "evidence_refs": list(refs)}
    evidence_by_id = {}
    for item in evidence:
        if not isinstance(item, dict):
            raise ValueError("each evidence item must be an object")
        identifier = item.get("evidence_id")
        if not isinstance(identifier, str) or not identifier.strip() or len(identifier) > 200 or identifier in evidence_by_id:
            raise ValueError("evidence_id values must be unique non-empty strings")
        if item.get("result") not in _RESULTS:
            raise ValueError("evidence result must be pass, fail or inconclusive")
        reviewer, provenance = item.get("reviewer"), item.get("provenance_ref")
        if reviewer is not None and (not isinstance(reviewer, str) or len(reviewer) > 200):
            raise ValueError("reviewer must be a string of at most 200 characters")
        if provenance is not None and (not isinstance(provenance, str) or len(provenance) > 300):
            raise ValueError("provenance_ref must be a string of at most 300 characters")
        evidence_by_id[identifier] = item
    rows, referenced = [], set()
    for identifier, requirement in req_by_id.items():
        linked, unresolved = [], []
        for ref in requirement["evidence_refs"]:
            referenced.add(ref)
            item = evidence_by_id.get(ref)
            if item is None:
                unresolved.append(ref)
            else:
                linked.append(item)
        valid_pass = [item for item in linked if item["result"] == "pass" and isinstance(item.get("reviewer"), str) and item["reviewer"].strip() and isinstance(item.get("provenance_ref"), str) and item["provenance_ref"].strip()]
        adverse = [item for item in linked if item["result"] in {"fail", "inconclusive"}]
        if unresolved:
            state = "broken_evidence_reference"
        elif adverse:
            state = "conflicting_or_inconclusive_evidence"
        elif valid_pass:
            state = "reviewed_pass_evidence_present"
        elif linked:
            state = "review_evidence_incomplete"
        else:
            state = "unverified"
        rows.append({
            "requirement_id": identifier,
            "verification_method": requirement["verification_method"],
            "evidence_refs": requirement["evidence_refs"],
            "unresolved_evidence_refs": unresolved,
            "state": state,
            "human_review_required": state != "reviewed_pass_evidence_present",
        })
    return {
        "requirement_count": len(rows),
        "reviewed_pass_count": sum(row["state"] == "reviewed_pass_evidence_present" for row in rows),
        "unverified_requirement_ids": [row["requirement_id"] for row in rows if row["state"] != "reviewed_pass_evidence_present"],
        "orphan_evidence_ids": sorted(set(evidence_by_id) - referenced),
        "broken_evidence_refs": sorted({ref for row in rows for ref in row["unresolved_evidence_refs"]}),
        "matrix": rows,
        "design_certification_or_safety_approval_granted": False,
    }

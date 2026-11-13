"""Identify re-verification and independent-review work after design changes."""
from __future__ import annotations

MAX_RECORDS = 2_000


def _list(value, field):
    if not isinstance(value, list) or len(value) > MAX_RECORDS or any(not isinstance(item, dict) for item in value):
        raise ValueError(f"{field} must be a list of at most {MAX_RECORDS} objects")
    return value


def _ids(values, field):
    if not isinstance(values, list) or len(values) > MAX_RECORDS:
        raise ValueError(f"{field} must be a list of at most {MAX_RECORDS} identifiers")
    if any(not isinstance(item, str) or not item.strip() for item in values):
        raise ValueError(f"{field} must contain non-empty strings")
    cleaned = [item.strip() for item in values]
    if len(cleaned) != len(set(cleaned)):
        raise ValueError(f"{field} must not contain duplicates")
    return set(cleaned)


def analyze_design_change_impact(design: dict, changes: dict) -> dict:
    if not isinstance(design, dict) or not isinstance(changes, dict):
        raise ValueError("design and changes must be objects")
    requirements = _list(design.get("requirements", []), "requirements")
    hazards = _list(design.get("hazards", []), "hazards")
    controls = _list(design.get("controls", []), "controls")
    verifications = _list(design.get("verifications", []), "verifications")
    reviews = _list(design.get("independent_reviews", []), "independent_reviews")

    def index(records, field):
        result = {}
        for item in records:
            identifier = item.get(field)
            if not isinstance(identifier, str) or not identifier.strip():
                raise ValueError(f"{field} is required")
            identifier = identifier.strip()
            if identifier in result:
                raise ValueError(f"{field} values must be unique")
            result[identifier] = item
        return result

    req_map = index(requirements, "requirement_id")
    hazard_map = index(hazards, "hazard_id")
    control_map = index(controls, "control_id")
    verification_map = index(verifications, "verification_id")
    review_map = index(reviews, "review_id")
    changed_requirements = _ids(changes.get("changed_requirement_ids", []), "changed_requirement_ids")
    changed_hazards = _ids(changes.get("changed_hazard_ids", []), "changed_hazard_ids")
    changed_controls = _ids(changes.get("changed_control_ids", []), "changed_control_ids")
    removed_evidence = _ids(changes.get("removed_evidence_refs", []), "removed_evidence_refs")

    missing_changes = {
        "requirement_ids": sorted(changed_requirements - set(req_map)),
        "hazard_ids": sorted(changed_hazards - set(hazard_map)),
        "control_ids": sorted(changed_controls - set(control_map)),
    }
    affected_controls = set(changed_controls)
    for control_id, control in control_map.items():
        if control.get("hazard_id") in changed_hazards:
            affected_controls.add(control_id)
    affected_hazards = set(changed_hazards)
    for control_id in affected_controls:
        hazard_id = control_map.get(control_id, {}).get("hazard_id")
        if isinstance(hazard_id, str) and hazard_id in hazard_map:
            affected_hazards.add(hazard_id)

    stale_verifications = []
    for verification_id, verification in verification_map.items():
        evidence_refs = verification.get("evidence_refs", [])
        control_refs = verification.get("control_ids", [])
        if not isinstance(evidence_refs, list) or not isinstance(control_refs, list):
            raise ValueError("verification evidence_refs and control_ids must be lists")
        stale = (
            verification.get("requirement_id") in changed_requirements
            or verification.get("hazard_id") in affected_hazards
            or bool(set(control_refs) & affected_controls)
            or bool(set(evidence_refs) & removed_evidence)
        )
        if stale:
            stale_verifications.append(verification_id)
    critical_hazards = {
        hazard_id for hazard_id in affected_hazards
        if hazard_id in hazard_map and (
            hazard_map[hazard_id].get("severity", 0) >= 4
            or hazard_map[hazard_id].get("likelihood", 0) >= 4
        )
    }
    stale_reviews = [
        review_id for review_id, review in review_map.items()
        if review.get("hazard_id") in affected_hazards
    ]
    return {
        "changed_requirement_ids": sorted(changed_requirements),
        "changed_hazard_ids": sorted(changed_hazards),
        "changed_control_ids": sorted(changed_controls),
        "affected_control_ids": sorted(affected_controls),
        "affected_hazard_ids": sorted(affected_hazards),
        "stale_verification_ids": sorted(stale_verifications),
        "unaffected_verification_ids": sorted(set(verification_map) - set(stale_verifications)),
        "independent_review_required_for_hazard_ids": sorted(critical_hazards),
        "previous_review_records_to_revisit": sorted(stale_reviews),
        "missing_change_references": missing_changes,
        "reverification_required": bool(stale_verifications),
        "human_safety_review_required": True,
        "design_approved": False,
        "safe_for_use_established": False,
        "deployment_authorized": False,
        "automatic_verification_invalidation": False,
        "automatic_design_approval": False,
    }

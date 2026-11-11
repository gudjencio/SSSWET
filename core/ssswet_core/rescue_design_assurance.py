"""Traceable safety-case preparation for civil protective and rescue technology."""
from __future__ import annotations

ALLOWED_DESIGN_CLASSES = {
    "protective_equipment", "rescue_equipment", "shelter",
    "communications", "accessibility_aid", "environmental_monitoring",
}
MAX_RECORDS = 2000


def _records(values, field):
    if not isinstance(values, list) or len(values) > MAX_RECORDS:
        raise ValueError(f"{field} must be a list of at most {MAX_RECORDS} records")
    if any(not isinstance(item, dict) for item in values):
        raise ValueError(f"every {field} record must be an object")
    return values


def _identifier(value, field):
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > 160:
        raise ValueError(f"{field} must contain 1 to 160 characters")
    return value.strip()


def build_assurance_case(*, design_id: str, design_class: str, design_owner_id: str,
                         requirements: list[dict], hazards: list[dict],
                         controls: list[dict], verifications: list[dict],
                         independent_reviews: list[dict] | None = None) -> dict:
    design_id = _identifier(design_id, "design_id")
    owner = _identifier(design_owner_id, "design_owner_id")
    if design_class not in ALLOWED_DESIGN_CLASSES:
        raise ValueError("design_class is outside the civil protective/rescue allowlist")
    requirements = _records(requirements, "requirements")
    hazards = _records(hazards, "hazards")
    controls = _records(controls, "controls")
    verifications = _records(verifications, "verifications")
    reviews = _records(independent_reviews or [], "independent_reviews")

    def index(records, key, field):
        ids = [_identifier(item.get(key), field) for item in records]
        if len(ids) != len(set(ids)):
            raise ValueError(f"{field} values must be unique")
        return set(ids)

    requirement_ids = index(requirements, "requirement_id", "requirement_id")
    hazard_ids = index(hazards, "hazard_id", "hazard_id")
    control_ids = index(controls, "control_id", "control_id")
    verification_ids = index(verifications, "verification_id", "verification_id")
    index(reviews, "review_id", "review_id")
    if not requirements or not hazards:
        raise ValueError("at least one requirement and one hazard are required")

    requirement_coverage = {key: [] for key in requirement_ids}
    failed_verifications = []
    invalid_verifications = []
    for item in verifications:
        requirement_id = item["requirement_id"]
        if requirement_id not in requirement_ids:
            invalid_verifications.append(item["verification_id"])
            continue
        outcome = item.get("outcome")
        if outcome not in {"pass", "fail", "inconclusive"}:
            raise ValueError("verification outcome must be pass, fail or inconclusive")
        refs = item.get("evidence_refs")
        if not isinstance(refs, list) or not refs or any(not isinstance(ref, str) or not ref.strip() for ref in refs):
            raise ValueError("every verification requires non-empty evidence_refs")
        requirement_coverage[requirement_id].append(item["verification_id"])
        if outcome == "fail":
            failed_verifications.append(item["verification_id"])

    control_by_hazard = {key: [] for key in hazard_ids}
    invalid_controls = []
    for item in controls:
        hazard_id = item.get("hazard_id")
        if hazard_id not in hazard_ids:
            invalid_controls.append(item["control_id"])
            continue
        if not isinstance(item.get("description"), str) or not item["description"].strip():
            raise ValueError("every control requires a description")
        if not isinstance(item.get("owner_id"), str) or not item["owner_id"].strip():
            raise ValueError("every control requires an owner")
        control_by_hazard[hazard_id].append(item["control_id"])

    hazard_gaps = []
    critical_hazards = []
    for item in hazards:
        hazard_id = item["hazard_id"]
        severity, likelihood = item.get("severity"), item.get("likelihood")
        for value, field in ((severity, "severity"), (likelihood, "likelihood")):
            if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 5:
                raise ValueError(f"hazard {field} must be an integer from 1 to 5")
        if not control_by_hazard[hazard_id]:
            hazard_gaps.append(hazard_id)
        if severity >= 4 or likelihood >= 4:
            critical_hazards.append(hazard_id)

    reviewed_hazards = set()
    invalid_reviews = []
    for item in reviews:
        hazard_id = item.get("hazard_id")
        reviewer_id = item.get("reviewer_id")
        refs = item.get("evidence_refs")
        if hazard_id not in hazard_ids or not isinstance(reviewer_id, str) or not reviewer_id.strip() or reviewer_id.strip() == owner or not isinstance(refs, list) or not refs:
            invalid_reviews.append(item["review_id"])
            continue
        reviewed_hazards.add(hazard_id)

    missing_requirement_verification = sorted(key for key, values in requirement_coverage.items() if not values)
    missing_critical_review = sorted(set(critical_hazards) - reviewed_hazards)
    traceability_complete = not (
        missing_requirement_verification or hazard_gaps or invalid_controls
        or invalid_verifications or invalid_reviews
    )
    if failed_verifications:
        status = "verification_failures_recorded"
    elif not traceability_complete:
        status = "blocked_missing_traceability"
    elif missing_critical_review:
        status = "independent_review_required"
    else:
        status = "evidence_ready_for_human_safety_review"
    return {
        "design_id": design_id, "design_class": design_class, "status": status,
        "requirement_count": len(requirements), "hazard_count": len(hazards),
        "control_count": len(controls), "verification_count": len(verifications),
        "independent_review_count": len(reviews),
        "missing_requirement_verification": missing_requirement_verification,
        "hazards_without_controls": sorted(hazard_gaps),
        "critical_hazards_requiring_independent_review": sorted(set(critical_hazards)),
        "critical_hazards_without_independent_review": missing_critical_review,
        "invalid_control_refs": sorted(invalid_controls),
        "invalid_verification_refs": sorted(invalid_verifications),
        "invalid_review_refs": sorted(invalid_reviews),
        "failed_verifications": sorted(failed_verifications),
        "traceability_complete": traceability_complete,
        "human_safety_review_required": True,
        "design_approved": False, "safe_for_use_established": False,
        "legal_compliance_established": False, "deployment_authorized": False,
        "medical_or_evacuation_decisions_automated": False,
    }

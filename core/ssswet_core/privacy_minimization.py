"""Flag potentially identifying field names for data-minimization review; values are not inspected."""
from __future__ import annotations
import re
_PATTERNS = {
    "direct_identifier": re.compile(r"(^|_)(full_?name|first_?name|last_?name|email|phone|telephone|street_?address|postal_?address|passport|ssn|social_?security|national_?id)(_|$)", re.I),
    "location_identifier": re.compile(r"(^|_)(precise_?location|gps|latitude|longitude|geolocation|ip_?address)(_|$)", re.I),
    "date_identifier": re.compile(r"(^|_)(date_?of_?birth|birth_?date|dob)(_|$)", re.I),
}

def audit_fields(field_names: list[str]) -> dict:
    if not isinstance(field_names, list) or len(field_names) > 5000:
        raise ValueError("field_names must be a list of at most 5000 names")
    findings = []
    for name in field_names:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("field names must be non-empty strings")
        normalized = name.strip()
        categories = [category for category, pattern in _PATTERNS.items() if pattern.search(normalized)]
        if categories:
            findings.append({"field": normalized, "categories": categories, "recommendation": "remove, tokenize, or coarsen unless strictly necessary"})
    return {"field_count": len(field_names), "flagged_count": len(findings), "findings": findings, "values_inspected": False, "automatically_deleted": False, "limitations": "Name-based screening only; it can miss identifiers and produce false positives."}

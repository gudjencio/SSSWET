"""Operationalisation audit for research hypotheses; not a scientific-validity test."""
from __future__ import annotations

import json
from typing import Any

MAX_SPEC_CHARS = 50_000
MAX_ITEMS = 20
MAX_TEXT = 2_000


def _text(value: Any, field: str, *, required: bool = True) -> str:
    if not isinstance(value, str):
        if required:
            raise ValueError(f"{field} must be text")
        return ""
    cleaned = value.strip()
    if required and not cleaned:
        raise ValueError(f"{field} is required")
    if len(cleaned) > MAX_TEXT:
        raise ValueError(f"{field} exceeds {MAX_TEXT} characters")
    return cleaned


def _items(value: Any, field: str, *, minimum: int = 1) -> list[str]:
    if not isinstance(value, list) or len(value) > MAX_ITEMS:
        raise ValueError(f"{field} must be a list of at most {MAX_ITEMS} entries")
    result = [_text(item, field) for item in value]
    if len(result) < minimum:
        raise ValueError(f"{field} must contain at least {minimum} entry")
    if len(result) != len(set(result)):
        raise ValueError(f"{field} must not contain duplicates")
    return result


def _variable_records(value: Any, field: str, measurement_field: str) -> list[dict[str, str]]:
    if not isinstance(value, list) or not 1 <= len(value) <= MAX_ITEMS:
        raise ValueError(f"{field} must contain 1 to {MAX_ITEMS} records")
    result = []
    seen = set()
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(f"{field}[{index}] must be an object")
        name = _text(item.get("name"), f"{field}[{index}].name")
        unit = _text(item.get("unit"), f"{field}[{index}].unit")
        method = _text(item.get(measurement_field), f"{field}[{index}].{measurement_field}")
        key = name.casefold()
        if key in seen:
            raise ValueError(f"{field} contains duplicate variable names")
        seen.add(key)
        result.append({"name": name, "unit": unit, measurement_field: method})
    return result


def assess_hypothesis(specification: dict[str, Any]) -> dict[str, Any]:
    """Report operationalisation gaps without judging truth, feasibility or ethics."""
    if not isinstance(specification, dict) or len(specification) > 30:
        raise ValueError("specification must be an object with at most 30 fields")
    try:
        encoded = json.dumps(
            specification, ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("specification must contain finite JSON-compatible values") from exc
    if len(encoded) > MAX_SPEC_CHARS:
        raise ValueError(f"specification exceeds {MAX_SPEC_CHARS} characters")

    required_text = (
        "research_question", "system_scope", "comparator", "time_horizon",
        "measurement_context",
    )
    missing = []
    normalized = {}
    for field in required_text:
        value = specification.get(field)
        if value is None or value == "":
            missing.append(field)
        elif not isinstance(value, str):
            raise ValueError(f"{field} must be text")
        else:
            normalized[field] = _text(value, field)

    variables = []
    outcomes = []
    for field, measure_field, target in (
        ("independent_variables", "operational_definition", variables),
        ("outcomes", "measurement_method", outcomes),
    ):
        raw = specification.get(field)
        if raw is None or raw == []:
            missing.append(field)
        else:
            target.extend(_variable_records(raw, field, measure_field))

    list_fields = (
        "falsification_conditions", "alternative_explanations", "safety_constraints",
    )
    lists = {}
    for field in list_fields:
        raw = specification.get(field)
        if raw is None or raw == []:
            missing.append(field)
            lists[field] = []
        else:
            lists[field] = _items(raw, field)

    missing = sorted(set(missing))
    return {
        "schema_version": 1,
        "complete_for_protocol_review": not missing,
        "status": "ready_for_protocol_review" if not missing else "incomplete_operationalisation",
        "missing_or_invalid_fields": missing,
        "independent_variable_count": len(variables),
        "outcome_count": len(outcomes),
        "falsification_condition_count": len(lists["falsification_conditions"]),
        "alternative_explanation_count": len(lists["alternative_explanations"]),
        "safety_constraint_count": len(lists["safety_constraints"]),
        "normalized_fields": {
            **normalized,
            "independent_variables": variables,
            "outcomes": outcomes,
            **lists,
        },
        "scientific_validity_established": False,
        "hypothesis_tested": False,
        "ethics_or_safety_approval_granted": False,
    }

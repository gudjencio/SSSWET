"""Compare declared claim contexts before human interpretation of differing values."""
from __future__ import annotations
import math
from .assurance_common import finite_number, identifier, text

MAX_CLAIMS = 200
SCHEMA_VERSION = 1
CONTEXT_FIELDS = ("unit", "population", "condition", "method", "observation_window")


def compare_claim_contexts(claims: list[dict]) -> dict:
    if not isinstance(claims, list) or len(claims) > MAX_CLAIMS:
        raise ValueError(f"claims must contain at most {MAX_CLAIMS} items")
    normalized, seen = [], set()
    for item in claims:
        if not isinstance(item, dict):
            raise ValueError("each claim must be an object")
        claim_id = identifier(item.get("claim_id"), "claim_id")
        if claim_id in seen:
            raise ValueError("claim_id values must be unique")
        seen.add(claim_id)
        value = finite_number(item.get("value"), "value")
        if abs(value) > 1e300:
            raise ValueError("value exceeds supported magnitude")
        row = {"claim_id": claim_id, "metric": text(item.get("metric"), "metric", 200).casefold(), "value": value}
        for field in CONTEXT_FIELDS:
            raw = item.get(field)
            row[field] = text(raw, field, 500).casefold() if raw not in (None, "") else None
        refs = item.get("source_ids", [])
        if not isinstance(refs, list) or len(refs) > 20:
            raise ValueError("source_ids must contain at most 20 items")
        row["source_ids"] = sorted(set(identifier(ref, "source_id") for ref in refs))
        normalized.append(row)
    comparisons = []
    for index, left in enumerate(normalized):
        for right in normalized[index + 1:]:
            if left["metric"] != right["metric"]:
                status, reasons = "different_metric", ["metric_mismatch"]
            else:
                missing = [field for field in CONTEXT_FIELDS if left[field] is None or right[field] is None]
                mismatches = [field for field in CONTEXT_FIELDS if left[field] is not None and right[field] is not None and left[field] != right[field]]
                if mismatches:
                    status, reasons = "incomparable_context", [field + "_mismatch" for field in mismatches]
                elif missing:
                    status, reasons = "insufficient_context", [field + "_missing" for field in missing]
                else:
                    status, reasons = "comparable_for_human_review", []
            comparable = status == "comparable_for_human_review"
            comparisons.append({"left_claim_id": left["claim_id"], "right_claim_id": right["claim_id"], "status": status, "reason_codes": reasons, "value_difference": left["value"] - right["value"] if comparable else None, "value_disagreement_for_review": comparable and not math.isclose(left["value"], right["value"], rel_tol=1e-9, abs_tol=1e-12), "contradiction_inferred": False})
    return {"schema_version": SCHEMA_VERSION, "claim_count": len(normalized), "comparison_count": len(comparisons), "comparisons": comparisons, "claims_deleted_or_rewritten": False, "scientific_truth_or_contradiction_determined": False}

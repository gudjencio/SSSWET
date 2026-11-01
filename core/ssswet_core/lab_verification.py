"""Read-only, evidence-linked verification plans for laboratory review leads.

Plans identify missing checks; they do not schedule work, execute experiments,
change records, or establish scientific validity.
"""
from __future__ import annotations

from typing import Any
from datetime import datetime, timezone
import hashlib

from .lab_discrepancies import LabDiscrepancyAnalyzer


class LabVerificationPlanner:
    """Turn recorded discrepancy leads into bounded human-review checklists."""

    def __init__(self, store: Any):
        self.store = store

    def build(self, limit: int = 200) -> dict:
        screening = LabDiscrepancyAnalyzer(self.store).build(limit=limit)
        runs = {
            item["run_id"]: item
            for item in self.store.lab_run_history(limit=limit * 2)
            if item.get("run_id")
        }
        comparisons = {
            item.get("comparison_id"): item
            for item in self.store.lab_comparison_history(limit=limit)
        }
        plans = []
        for finding in screening["findings"]:
            comparison = comparisons.get(finding["comparison_id"], {})
            left = runs.get(finding["left_run_id"], {})
            right = runs.get(finding["right_run_id"], {})
            checks: list[dict[str, str]] = []

            def add(code: str, instruction: str, reason: str) -> None:
                checks.append({"code": code, "instruction": instruction, "reason": reason})

            if not left or not right:
                add("recover_run_records", "Recover both original run records and verify their fingerprints.",
                    "One or both run records are unavailable in the current history window.")
            if comparison.get("comparable") is not True:
                add("establish_comparability", "Review protocol version, execution kind and required parameters before comparing outputs.",
                    "The comparison is not explicitly marked comparable.")
            if comparison.get("same_environment") is False:
                add("environment", "Document whether environment differences could affect the measured outputs.",
                    "The recorded execution environments differ.")
            if comparison.get("same_code_or_model_reference") is False:
                add("implementation", "Review the code or model references and identify implementation differences.",
                    "The recorded code or model references differ.")
            if comparison.get("independence_independently_verified") is not True:
                add("independence", "Have a reviewer assess campaign separation, provenance groups, shared sources and shared datasets.",
                    "Declared independence has not been independently verified.")
            if comparison.get("shared_dataset_ids"):
                add("dataset_provenance", "Review dataset versions, transformations and shared-data dependencies.",
                    "The runs share one or more dataset identifiers.")
            if comparison.get("shared_source_ids"):
                add("source_provenance", "Review shared source material and possible common-source dependence.",
                    "The runs share one or more source identifiers.")
            if finding["classification"] == "recorded_result_divergence":
                add("measurement_and_tolerance", "Recheck units, measurement definitions, uncertainty and the declared comparison tolerance.",
                    "Recorded outputs differ beyond the stated tolerance.")
                add("independent_repeat", "Consider an independently prepared repeat or a separately implemented computational check, subject to appropriate review.",
                    "A targeted check may help distinguish reproducible divergence from procedural or implementation effects.")
            elif finding["classification"] == "incompatible_conditions":
                add("align_conditions", "Identify which conditions differ and decide whether a justified like-for-like comparison is possible.",
                    "The existing comparison explicitly reports incompatible conditions.")
            else:
                add("complete_record", "Complete the missing comparison fields and preserve the original comparison record.",
                    "The existing comparison does not contain enough explicit information for classification.")

            plan_id = "verification:" + finding["finding_id"].split(":", 1)[-1]
            history = self.store.lab_verification_event_history(plan_id=plan_id) if hasattr(self.store, "lab_verification_event_history") else []
            latest = {event["check_code"]: event for event in history}
            for check in checks:
                check["check_id"] = plan_id + ":" + check["code"]
                check["review_state"] = latest.get(check["code"], {}).get("state", "pending")
                check["review_history"] = [event for event in history if event["check_code"] == check["code"]]
            plans.append({
                "plan_id": plan_id,
                "finding_id": finding["finding_id"],
                "comparison_id": finding["comparison_id"],
                "classification": finding["classification"],
                "checks": checks,
                "requires_human_review": True,
                "automatic_execution": False,
                "automatic_task_creation": False,
                "scientific_contradiction_established": False,
                "scientific_validity_established": False,
            })

        return {
            "plans": plans,
            "count": len(plans),
            "read_only": True,
            "automatic_execution": False,
            "automatic_task_creation": False,
            "scientific_validity_established": False,
            "interpretation": "Checklists are review suggestions derived from recorded metadata, not experimental instructions or scientific conclusions.",
        }


    def record_check_review(self, plan_id: str, check_code: str, state: str, note: str, reviewer: str) -> dict:
        if state not in {"in_progress", "completed", "blocked"}:
            raise ValueError("Unsupported verification check state")
        if not isinstance(note, str) or not note.strip() or len(note.strip()) > 4000:
            raise ValueError("A review note between 1 and 4000 characters is required")
        if not isinstance(reviewer, str) or not reviewer.strip() or len(reviewer.strip()) > 200:
            raise ValueError("A reviewer label between 1 and 200 characters is required")
        plan = next((item for item in self.build()["plans"] if item["plan_id"] == plan_id), None)
        if plan is None:
            raise ValueError("Unknown or no longer active verification plan")
        if not any(item["code"] == check_code for item in plan["checks"]):
            raise ValueError("Unknown check code for this verification plan")
        previous = self.store.lab_verification_event_history(plan_id=plan_id)
        latest = next((event for event in reversed(previous) if event["check_code"] == check_code), None)
        if latest and latest["state"] == "completed":
            raise ValueError("A completed check is closed; create a new plan to reassess it")
        now = datetime.now(timezone.utc).isoformat()
        event = {
            "event_id": hashlib.sha256((plan_id + "|" + check_code + "|" + now + "|" + reviewer.strip() + "|" + note.strip()).encode("utf-8")).hexdigest(),
            "plan_id": plan_id, "check_code": check_code, "state": state,
            "note": note.strip(), "reviewer": reviewer.strip(), "created_at": now,
        }
        self.store.append_lab_verification_event(event)
        return event

"""Evidence-linked reproducibility intelligence for recorded digital-lab data.

The index measures the completeness of recorded reproducibility evidence only.
It is not a probability, scientific-quality score, safety assessment or truth claim.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any

from .digital_lab import _verify_fingerprint


class ReproducibilityIntelligence:
    """Summarize recorded protocol reproductions using an explicit rubric."""

    COMPONENTS = {
        "record_integrity": 20,
        "comparability": 20,
        "output_consistency": 20,
        "independent_verification": 20,
        "provenance_separation": 20,
    }

    def __init__(self, store: Any):
        self.store = store

    @staticmethod
    def _pair_key(item: dict) -> frozenset:
        return frozenset((item.get("left_run_id"), item.get("right_run_id")))

    @staticmethod
    def _parameter_sensitivity(runs: list[dict]) -> dict:
        """Describe one-parameter numeric contrasts under matched recorded conditions."""
        contrasts = []
        eligible_records = [
            run for run in runs
            if _verify_fingerprint(run, "record_hash")
            and isinstance(run.get("parameters"), dict)
            and isinstance(run.get("outputs"), dict)
        ]
        for index, left in enumerate(eligible_records):
            for right in eligible_records[index + 1:]:
                if not (
                    left.get("campaign_id")
                    and left.get("campaign_id") == right.get("campaign_id")
                    and left.get("provenance_group")
                    and left.get("provenance_group") == right.get("provenance_group")
                    and left.get("kind") == right.get("kind")
                    and left.get("method") == right.get("method")
                    and left.get("environment") == right.get("environment")
                    and left.get("code_or_model_reference") == right.get("code_or_model_reference")
                ):
                    continue
                left_params, right_params = left["parameters"], right["parameters"]
                if set(left_params) != set(right_params):
                    continue
                changed = [
                    key for key in sorted(left_params)
                    if left_params[key] != right_params[key]
                ]
                if len(changed) != 1:
                    continue
                parameter = changed[0]
                left_value, right_value = left_params[parameter], right_params[parameter]
                if (
                    isinstance(left_value, bool) or isinstance(right_value, bool)
                    or not isinstance(left_value, (int, float))
                    or not isinstance(right_value, (int, float))
                    or not isfinite(float(left_value)) or not isfinite(float(right_value))
                ):
                    continue
                output_changes = []
                for key in sorted(set(left["outputs"]) & set(right["outputs"])):
                    a, b = left["outputs"][key], right["outputs"][key]
                    if (
                        isinstance(a, bool) or isinstance(b, bool)
                        or not isinstance(a, (int, float))
                        or not isinstance(b, (int, float))
                        or not isfinite(float(a)) or not isfinite(float(b))
                    ):
                        continue
                    delta = float(b) - float(a)
                    output_changes.append({
                        "output": key,
                        "left_value": float(a),
                        "right_value": float(b),
                        "absolute_change": delta,
                        "relative_change_percent": (delta / abs(float(a)) * 100) if float(a) != 0 else None,
                    })
                if output_changes:
                    contrasts.append({
                        "left_run_id": left.get("run_id", ""),
                        "right_run_id": right.get("run_id", ""),
                        "parameter": parameter,
                        "left_parameter_value": float(left_value),
                        "right_parameter_value": float(right_value),
                        "output_changes": output_changes,
                    })
        return {
            "status": "candidate_contrasts_recorded" if contrasts else "insufficient_comparable_parameter_variation",
            "contrast_count": len(contrasts),
            "contrasts": contrasts[:100],
            "conditions": [
                "matching campaign and provenance group",
                "matching execution kind, method, environment and code/model reference",
                "exactly one changed numeric parameter",
                "valid run fingerprints and at least one shared numeric output",
            ],
            "interpretation": (
                "Descriptive one-parameter contrasts only. They do not establish causality, "
                "a general sensitivity function, statistical significance or scientific validity."
            ),
            "causal_effect_established": False,
            "scientific_validity_established": False,
        }

    def build(self, limit: int = 200) -> dict:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 500:
            raise ValueError("limit must be an integer between 1 and 500")

        protocols = self.store.lab_protocol_history(limit=limit)
        runs = self.store.lab_run_history(limit=limit * 2)
        comparisons = self.store.lab_comparison_history(limit=limit * 2)
        run_map = {item.get("run_id"): item for item in runs if item.get("run_id")}

        groups: dict[tuple[str, int], list[dict]] = defaultdict(list)
        for run in runs:
            groups[(run.get("protocol_id", ""), run.get("protocol_version", 0))].append(run)

        protocol_map = {
            (item.get("protocol_id"), item.get("version")): item
            for item in protocols
        }
        comparison_groups: dict[tuple[str, int], list[dict]] = defaultdict(list)
        unassigned_comparisons = 0
        for comparison in comparisons:
            left = run_map.get(comparison.get("left_run_id"))
            right = run_map.get(comparison.get("right_run_id"))
            anchor = left or right
            if anchor:
                comparison_groups[(anchor.get("protocol_id", ""), anchor.get("protocol_version", 0))].append(comparison)
            else:
                unassigned_comparisons += 1

        keys = set(groups) | set(comparison_groups) | set(protocol_map)
        reports = []
        for key in sorted(keys, key=lambda value: (str(value[0]), int(value[1] or 0))):
            protocol_id, version = key
            protocol_runs = groups.get(key, [])
            protocol_comparisons = comparison_groups.get(key, [])
            pair_scores = []
            classifications = []
            pair_details = []

            for comparison in protocol_comparisons:
                left = run_map.get(comparison.get("left_run_id"))
                right = run_map.get(comparison.get("right_run_id"))
                integrity = bool(
                    left and right
                    and _verify_fingerprint(left, "record_hash")
                    and _verify_fingerprint(right, "record_hash")
                )
                comparable = comparison.get("comparable") is True
                matches = comparison.get("outputs_match_within_tolerance") is True
                different_campaigns = bool(
                    left and right and left.get("campaign_id") != right.get("campaign_id")
                )
                independent = bool(
                    comparison.get("independence_independently_verified") is True
                    and different_campaigns
                    and left and right
                    and left.get("independence_declared") is True
                    and right.get("independence_declared") is True
                )
                shared_sources = sorted(
                    set((left or {}).get("source_ids", [])) & set((right or {}).get("source_ids", []))
                )
                shared_datasets = sorted(
                    set((left or {}).get("dataset_ids", [])) & set((right or {}).get("dataset_ids", []))
                )
                left_group = (left or {}).get("provenance_group", "")
                right_group = (right or {}).get("provenance_group", "")
                separated = bool(
                    left_group and right_group and left_group != right_group
                    and not shared_sources and not shared_datasets
                )
                components = {
                    "record_integrity": self.COMPONENTS["record_integrity"] if integrity else 0,
                    "comparability": self.COMPONENTS["comparability"] if comparable else 0,
                    "output_consistency": self.COMPONENTS["output_consistency"] if comparable and matches else 0,
                    "independent_verification": self.COMPONENTS["independent_verification"] if independent else 0,
                    "provenance_separation": self.COMPONENTS["provenance_separation"] if separated else 0,
                }
                pair_scores.append(sum(components.values()))
                if not left or not right or not integrity:
                    classification = "insufficient_record_integrity"
                elif comparison.get("comparable") is False:
                    classification = "incomparable_conditions"
                elif not comparable or not isinstance(comparison.get("outputs_match_within_tolerance"), bool):
                    classification = "incomplete_comparison"
                elif not matches:
                    classification = "recorded_output_divergence"
                elif independent and separated:
                    classification = "independently_verified_match_recorded"
                else:
                    classification = "matching_outputs_not_independently_verified"
                classifications.append(classification)
                pair_details.append({
                    "comparison_id": comparison.get("comparison_id", ""),
                    "left_run_id": comparison.get("left_run_id", ""),
                    "right_run_id": comparison.get("right_run_id", ""),
                    "classification": classification,
                    "index": sum(components.values()),
                    "components": components,
                    "shared_source_ids": shared_sources,
                    "shared_dataset_ids": shared_datasets,
                    "independence_independently_verified": independent,
                    "scientific_validity_established": False,
                })

            if not protocol_comparisons:
                status = "no_recorded_comparisons"
                index = None
            elif "recorded_output_divergence" in classifications:
                status = "recorded_output_divergence"
                index = round(sum(pair_scores) / len(pair_scores), 1)
            elif all(item == "incomparable_conditions" for item in classifications):
                status = "incomparable_conditions"
                index = round(sum(pair_scores) / len(pair_scores), 1)
            elif all(item in {"insufficient_record_integrity", "incomplete_comparison"} for item in classifications):
                status = "insufficient_data"
                index = round(sum(pair_scores) / len(pair_scores), 1)
            elif "independently_verified_match_recorded" in classifications:
                status = "independent_match_evidence_recorded"
                index = round(sum(pair_scores) / len(pair_scores), 1)
            else:
                status = "matching_outputs_not_independently_verified"
                index = round(sum(pair_scores) / len(pair_scores), 1)

            campaign_ids = sorted({item.get("campaign_id", "") for item in protocol_runs if item.get("campaign_id")})
            reports.append({
                "protocol_id": protocol_id,
                "protocol_version": version,
                "protocol_title": protocol_map.get(key, {}).get("title", ""),
                "run_count": len(protocol_runs),
                "campaign_count": len(campaign_ids),
                "comparison_count": len(protocol_comparisons),
                "campaign_ids": campaign_ids,
                "status": status,
                "reproducibility_evidence_index": index,
                "index_label": "recorded evidence completeness; not scientific validity",
                "index_maximum": 100,
                "index_components": dict(self.COMPONENTS),
                "comparisons": pair_details,
                "parameter_sensitivity": self._parameter_sensitivity(protocol_runs),
                "requires_human_review": True,
                "scientific_validity_established": False,
            })

        return {
            "protocols": reports,
            "protocol_count": len(reports),
            "comparison_count": sum(item["comparison_count"] for item in reports),
            "unassigned_comparison_count": unassigned_comparisons,
            "scoring_method": "Five equally weighted, binary, explicitly documented evidence dimensions (20 points each); the protocol index is the arithmetic mean of recorded comparison indices.",
            "score_interpretation": "The index describes only the completeness of recorded evidence. It is not a probability, scientific-quality score, causal assessment, safety certification or measure of truth.",
            "parameter_sensitivity_automatically_established": False,
            "scientific_validity_established": False,
            "read_only": True,
            "automatic_task_creation": False,
            "automatic_experiment_execution": False,
        }

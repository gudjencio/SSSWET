"""Anchor-bounded, provenance-preserving clock alignment for Virtual Time Mapping."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from math import isfinite

MAX_ANCHORS = 500
MAX_EVENTS = 5000
MAX_ID_LENGTH = 160
MAX_EVIDENCE_REF_LENGTH = 500
ALIGNMENT_METHOD = "piecewise_linear_interpolation"
CLOCK_MAPPING_ASSUMPTION = "piecewise_linear_between_declared_anchors"
UNCERTAINTY_METHOD = "linear_sum_of_declared_absolute_bounds_under_piecewise_linear_model"
UNCERTAINTY_INTERPRETATION = "conditional_envelope_under_piecewise_linear_clock_mapping"
UNCERTAINTY_SEMANTICS = (
    "Declared values are conservative absolute bounds in seconds; "
    "they are not standard deviations or confidence intervals."
)


def _timestamp(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be an ISO timestamp")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{field} must include an explicit timezone")
    return parsed.astimezone(timezone.utc)


def _identifier(value, field):
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > MAX_ID_LENGTH:
        raise ValueError(f"{field} must contain 1 to {MAX_ID_LENGTH} characters")
    return value.strip()


def _evidence_ref(value):
    if value is None:
        return None
    if not isinstance(value, str) or len(value.strip()) > MAX_EVIDENCE_REF_LENGTH:
        raise ValueError(f"reference_evidence_ref must contain at most {MAX_EVIDENCE_REF_LENGTH} characters")
    return value.strip() or None


def _nonnegative(value, field):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be finite and non-negative")
    try:
        result = float(value)
    except (OverflowError, TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be finite and non-negative") from exc
    if not isfinite(result) or result < 0:
        raise ValueError(f"{field} must be finite and non-negative")
    return result


def _canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _drift(previous_source, current_source, previous_reference, current_reference):
    source_seconds = (current_source - previous_source).total_seconds()
    reference_seconds = (current_reference - previous_reference).total_seconds()
    if source_seconds <= 0 or reference_seconds <= 0:
        raise ValueError("source and reference anchor timestamps must be strictly increasing")
    return source_seconds, reference_seconds, (reference_seconds / source_seconds - 1.0) * 1_000_000


def _close_number(actual, expected):
    if not isinstance(actual, (int, float)) or isinstance(actual, bool):
        return False
    try:
        numeric = float(actual)
    except (OverflowError, TypeError, ValueError):
        return False
    return isfinite(numeric) and abs(numeric - expected) <= max(1e-9, abs(expected) * 1e-12)


def build_clock_model(anchors: list[dict]) -> dict:
    """Build a deterministic model from paired, timezone-aware clock anchors.

    Anchor uncertainties are optional user-declared absolute bounds. Missing
    bounds are retained as undeclared rather than silently treated as zero.
    """
    if not isinstance(anchors, list) or not 2 <= len(anchors) <= MAX_ANCHORS:
        raise ValueError(f"anchors must contain 2 to {MAX_ANCHORS} records")

    normalized = []
    session_id = source_id = None
    for item in anchors:
        if not isinstance(item, dict):
            raise ValueError("every anchor must be an object")
        session = _identifier(item.get("session_id"), "session_id")
        source = _identifier(item.get("source_id"), "source_id")
        if session_id is None:
            session_id, source_id = session, source
        if session != session_id or source != source_id:
            raise ValueError("one clock model may contain only one session and source")

        source_time = _timestamp(item.get("source_timestamp"), "source_timestamp")
        reference_time = _timestamp(item.get("reference_timestamp"), "reference_timestamp")
        uncertainty_declared = item.get("uncertainty_seconds") is not None
        uncertainty = (
            _nonnegative(item.get("uncertainty_seconds"), "uncertainty_seconds")
            if uncertainty_declared else 0.0
        )
        raw_anchor_id = item.get("anchor_id")
        anchor_id = None if raw_anchor_id is None else _identifier(raw_anchor_id, "anchor_id")
        normalized.append({
            "anchor_id": anchor_id,
            "source_timestamp": source_time,
            "reference_timestamp": reference_time,
            "uncertainty_seconds": uncertainty,
            "uncertainty_declared": uncertainty_declared,
            "reference_evidence_ref": _evidence_ref(item.get("reference_evidence_ref")),
        })

    normalized.sort(key=lambda item: item["source_timestamp"])
    for previous, current in zip(normalized, normalized[1:]):
        _drift(
            previous["source_timestamp"], current["source_timestamp"],
            previous["reference_timestamp"], current["reference_timestamp"],
        )

    for index, item in enumerate(normalized, start=1):
        if item["anchor_id"] is None:
            item["anchor_id"] = f"anchor-{index:04d}"
    anchor_ids = [item["anchor_id"] for item in normalized]
    if len(anchor_ids) != len(set(anchor_ids)):
        raise ValueError("anchor_id values must be unique")

    serialized_anchors = [{
        "anchor_id": item["anchor_id"],
        "source_timestamp": item["source_timestamp"].isoformat(),
        "reference_timestamp": item["reference_timestamp"].isoformat(),
        "uncertainty_seconds": item["uncertainty_seconds"],
        "uncertainty_declared": item["uncertainty_declared"],
        "reference_evidence_ref": item["reference_evidence_ref"],
    } for item in normalized]

    drift_intervals = []
    for previous, current in zip(normalized, normalized[1:]):
        source_seconds, reference_seconds, drift_ppm = _drift(
            previous["source_timestamp"], current["source_timestamp"],
            previous["reference_timestamp"], current["reference_timestamp"],
        )
        drift_intervals.append({
            "from_anchor_id": previous["anchor_id"],
            "to_anchor_id": current["anchor_id"],
            "source_interval_seconds": source_seconds,
            "reference_interval_seconds": reference_seconds,
            "drift_ppm": drift_ppm,
        })

    payload = {
        "schema_version": 2,
        "session_id": session_id,
        "source_id": source_id,
        "anchors": serialized_anchors,
        "anchor_count": len(serialized_anchors),
        "anchor_evidence_ref_count": sum(
            item["reference_evidence_ref"] is not None for item in serialized_anchors
        ),
        "all_anchor_uncertainties_declared": all(
            item["uncertainty_declared"] for item in serialized_anchors
        ),
        "alignment_method": ALIGNMENT_METHOD,
        "clock_mapping_assumption": CLOCK_MAPPING_ASSUMPTION,
        "drift_intervals": drift_intervals,
        "max_absolute_drift_ppm": max(abs(item["drift_ppm"]) for item in drift_intervals),
        "drift_is_diagnostic_only": True,
        "extrapolation_permitted": False,
        "uncertainty_method": UNCERTAINTY_METHOD,
        "uncertainty_semantics": UNCERTAINTY_SEMANTICS,
        "uncertainty_interpretation": UNCERTAINTY_INTERPRETATION,
        "uncertainty_is_confidence_interval": False,
    }
    digest = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()
    return {**payload, "model_sha256": digest}


def verify_clock_model(model: dict) -> dict:
    """Verify model structure, declared scientific limits and canonical digest."""
    if not isinstance(model, dict):
        return {
            "valid": False, "recorded_sha256": None,
            "expected_sha256": None, "tampered_or_incomplete": True,
        }

    payload = {key: value for key, value in model.items() if key != "model_sha256"}
    expected = None
    structural = False
    try:
        schema_version = payload.get("schema_version")
        anchors = payload.get("anchors")
        session_id = _identifier(payload.get("session_id"), "session_id")
        source_id = _identifier(payload.get("source_id"), "source_id")
        structural = (
            isinstance(schema_version, int)
            and not isinstance(schema_version, bool)
            and schema_version in {1, 2}
            and payload.get("session_id") == session_id
            and payload.get("source_id") == source_id
            and isinstance(anchors, list)
            and 2 <= len(anchors) <= MAX_ANCHORS
            and len(anchors) == payload.get("anchor_count")
            and payload.get("drift_is_diagnostic_only") is True
            and payload.get("extrapolation_permitted") is False
        )

        normalized = []
        if structural and schema_version == 1:
            for item in anchors:
                if not isinstance(item, dict):
                    structural = False
                    break
                uncertainty = _nonnegative(item.get("uncertainty_seconds"), "uncertainty_seconds")
                normalized.append((
                    _timestamp(item.get("source_timestamp"), "source_timestamp"),
                    _timestamp(item.get("reference_timestamp"), "reference_timestamp"),
                    uncertainty,
                ))
            drifts = []
            if structural:
                for previous, current in zip(normalized, normalized[1:]):
                    source_seconds, _, drift_ppm = _drift(
                        previous[0], current[0], previous[1], current[1]
                    )
                    drifts.append(drift_ppm)
                calculated_drift = max(abs(value) for value in drifts)
                structural = _close_number(payload.get("max_absolute_drift_ppm"), calculated_drift)

        elif structural and schema_version == 2:
            structural = (
                payload.get("alignment_method") == ALIGNMENT_METHOD
                and payload.get("clock_mapping_assumption") == CLOCK_MAPPING_ASSUMPTION
                and payload.get("uncertainty_method") == UNCERTAINTY_METHOD
                and payload.get("uncertainty_semantics") == UNCERTAINTY_SEMANTICS
                and payload.get("uncertainty_interpretation") == UNCERTAINTY_INTERPRETATION
                and payload.get("uncertainty_is_confidence_interval") is False
            )
            seen_ids = set()
            if structural:
                for item in anchors:
                    if not isinstance(item, dict):
                        structural = False
                        break
                    anchor_id = _identifier(item.get("anchor_id"), "anchor_id")
                    if anchor_id != item.get("anchor_id") or anchor_id in seen_ids:
                        structural = False
                        break
                    seen_ids.add(anchor_id)
                    declared = item.get("uncertainty_declared")
                    if not isinstance(declared, bool):
                        structural = False
                        break
                    uncertainty = _nonnegative(item.get("uncertainty_seconds"), "uncertainty_seconds")
                    if not declared and uncertainty != 0:
                        structural = False
                        break
                    reference_ref = _evidence_ref(item.get("reference_evidence_ref"))
                    source_time = _timestamp(item.get("source_timestamp"), "source_timestamp")
                    reference_time = _timestamp(item.get("reference_timestamp"), "reference_timestamp")
                    if (
                        reference_ref != item.get("reference_evidence_ref")
                        or source_time.isoformat() != item.get("source_timestamp")
                        or reference_time.isoformat() != item.get("reference_timestamp")
                    ):
                        structural = False
                        break
                    normalized.append((source_time, reference_time, uncertainty))
            drift_intervals = []
            if structural:
                for index, (previous, current) in enumerate(zip(normalized, normalized[1:])):
                    source_seconds, reference_seconds, drift_ppm = _drift(
                        previous[0], current[0], previous[1], current[1]
                    )
                    stored = payload.get("drift_intervals")
                    if not isinstance(stored, list) or len(stored) != len(normalized) - 1:
                        structural = False
                        break
                    item = stored[index]
                    if not isinstance(item, dict):
                        structural = False
                        break
                    if (
                        item.get("from_anchor_id") != anchors[index]["anchor_id"]
                        or item.get("to_anchor_id") != anchors[index + 1]["anchor_id"]
                        or not _close_number(item.get("source_interval_seconds"), source_seconds)
                        or not _close_number(item.get("reference_interval_seconds"), reference_seconds)
                        or not _close_number(item.get("drift_ppm"), drift_ppm)
                    ):
                        structural = False
                        break
                    drift_intervals.append(drift_ppm)
            if structural:
                calculated_drift = max(abs(value) for value in drift_intervals)
                declared_refs = sum(item.get("reference_evidence_ref") is not None for item in anchors)
                all_declared = all(item.get("uncertainty_declared") is True for item in anchors)
                reference_count = payload.get("anchor_evidence_ref_count")
                structural = (
                    _close_number(payload.get("max_absolute_drift_ppm"), calculated_drift)
                    and isinstance(reference_count, int)
                    and not isinstance(reference_count, bool)
                    and reference_count == declared_refs
                    and payload.get("all_anchor_uncertainties_declared") is all_declared
                )

        if structural:
            expected = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()
    except (KeyError, TypeError, ValueError, OverflowError):
        structural = False
    valid = bool(structural and model.get("model_sha256") == expected)
    return {
        "valid": valid,
        "recorded_sha256": model.get("model_sha256"),
        "expected_sha256": expected,
        "tampered_or_incomplete": not valid,
    }


def align_events(model: dict, events: list[dict]) -> dict:
    """Return a derived aligned view; never mutates source events or model inputs."""
    verification = verify_clock_model(model)
    if not verification["valid"]:
        raise ValueError("clock model failed integrity verification")
    if not isinstance(events, list) or len(events) > MAX_EVENTS:
        raise ValueError(f"events must be a list of at most {MAX_EVENTS} records")

    legacy = model["schema_version"] == 1
    anchors = []
    for index, item in enumerate(model["anchors"], start=1):
        anchors.append({
            "anchor_id": item.get("anchor_id", f"legacy-anchor-{index:04d}"),
            "source": _timestamp(item["source_timestamp"], "source_timestamp"),
            "reference": _timestamp(item["reference_timestamp"], "reference_timestamp"),
            "uncertainty": float(item["uncertainty_seconds"]),
            "uncertainty_declared": item.get("uncertainty_declared", False) if not legacy else False,
            "reference_evidence_ref": item.get("reference_evidence_ref") if not legacy else None,
        })

    reports = []
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            raise ValueError("each event must be an object")
        event_id = event.get("event_id", str(index))
        if not isinstance(event_id, str) or not event_id.strip() or len(event_id) > MAX_ID_LENGTH:
            raise ValueError(f"event_id must contain 1 to {MAX_ID_LENGTH} characters")
        if event.get("session_id") != model["session_id"] or event.get("source_id") != model["source_id"]:
            reports.append({
                "event_id": event_id, "status": "different_session_or_source",
                "aligned_at": None, "extrapolation_used": False,
            })
            continue

        instant = _timestamp(event.get("timestamp"), "event timestamp")
        event_uncertainty_declared = event.get("uncertainty_seconds") is not None
        event_uncertainty = (
            _nonnegative(event.get("uncertainty_seconds"), "event uncertainty_seconds")
            if event_uncertainty_declared else 0.0
        )
        if instant < anchors[0]["source"] or instant > anchors[-1]["source"]:
            reports.append({
                "event_id": event_id, "status": "outside_anchor_range",
                "aligned_at": None, "extrapolation_used": False,
            })
            continue

        right_index = next(
            (i for i, anchor in enumerate(anchors) if anchor["source"] >= instant),
            len(anchors) - 1,
        )
        if anchors[right_index]["source"] == instant:
            left = right = anchors[right_index]
            fraction = 0.0
            interval_seconds = 0.0
            interval_drift_ppm = None
            aligned = right["reference"]
            anchor_uncertainty_declared = right["uncertainty_declared"]
            anchor_uncertainty = right["uncertainty"] if anchor_uncertainty_declared else None
        else:
            left, right = anchors[right_index - 1], anchors[right_index]
            interval_seconds = (right["source"] - left["source"]).total_seconds()
            fraction = (instant - left["source"]).total_seconds() / interval_seconds
            aligned = left["reference"] + (right["reference"] - left["reference"]) * fraction
            anchor_uncertainty_declared = (
                left["uncertainty_declared"] and right["uncertainty_declared"]
            )
            anchor_uncertainty = (
                left["uncertainty"] * (1 - fraction) + right["uncertainty"] * fraction
                if anchor_uncertainty_declared else None
            )
            interval_drift_ppm = (
                model["drift_intervals"][right_index - 1]["drift_ppm"]
                if not legacy else None
            )

        bracket_anchors = (left,) if left is right else (left, right)
        anchor_refs = [
            item["reference_evidence_ref"]
            for item in bracket_anchors
            if item["reference_evidence_ref"] is not None
        ]
        required_ref_count = 1 if left is right else 2
        uncertainty_complete = anchor_uncertainty_declared and event_uncertainty_declared
        total_uncertainty = (
            anchor_uncertainty + event_uncertainty if uncertainty_complete else None
        )
        reports.append({
            "event_id": event_id,
            "status": "aligned_within_anchors",
            "source_timestamp": instant.isoformat(),
            "aligned_at": aligned.isoformat(),
            "left_anchor_id": left["anchor_id"],
            "right_anchor_id": right["anchor_id"],
            "interpolation_fraction": fraction,
            "interpolation_fraction_not_a_probability": True,
            "anchor_interval_seconds": interval_seconds,
            "interval_drift_ppm": interval_drift_ppm,
            "anchor_reference_evidence_refs": anchor_refs,
            "anchor_provenance_complete": len(anchor_refs) == required_ref_count,
            "anchor_uncertainty_seconds": anchor_uncertainty,
            "anchor_uncertainty_declared": anchor_uncertainty_declared,
            "event_uncertainty_seconds": event_uncertainty if event_uncertainty_declared else None,
            "event_uncertainty_declared": event_uncertainty_declared,
            "declared_uncertainty_envelope_seconds": total_uncertainty,
            "declared_uncertainty_inputs_complete": uncertainty_complete,
            "uncertainty_method": (
                UNCERTAINTY_METHOD if not legacy else "legacy_uncertainty_semantics_unverified"
            ),
            "uncertainty_interpretation": (
                UNCERTAINTY_INTERPRETATION if not legacy else "legacy_uncertainty_semantics_unverified"
            ),
            "clock_mapping_assumption": (
                CLOCK_MAPPING_ASSUMPTION if not legacy else "legacy_assumption_not_recorded"
            ),
            "uncertainty_is_confidence_interval": False,
            "extrapolation_used": False,
        })

    aligned = [item for item in reports if item["status"] == "aligned_within_anchors"]
    return {
        "events": reports,
        "event_count": len(reports),
        "aligned_count": len(aligned),
        "complete_declared_uncertainty_input_count": sum(
            item["declared_uncertainty_inputs_complete"] for item in aligned
        ),
        "complete_anchor_provenance_count": sum(
            item["anchor_provenance_complete"] for item in aligned
        ),
        "clock_model_sha256": model["model_sha256"],
        "alignment_method": (
            ALIGNMENT_METHOD if not legacy else "legacy_piecewise_linear_interpolation"
        ),
        "clock_mapping_assumption": (
            CLOCK_MAPPING_ASSUMPTION if not legacy else "legacy_assumption_not_recorded"
        ),
        "drift_is_diagnostic_only": True,
        "extrapolation_permitted": False,
        "session_isolation_preserved": True,
        "unrecorded_history_recovered": False,
        "event_identity_established": False,
        "future_prediction_performed": False,
    }

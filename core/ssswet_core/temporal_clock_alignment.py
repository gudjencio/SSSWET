"""Anchor-bounded alignment of recorded clocks for Virtual Time Mapping sessions."""
from __future__ import annotations

from datetime import datetime, timezone
from math import isfinite

MAX_ANCHORS = 500
MAX_EVENTS = 5000


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


def build_clock_model(anchors: list[dict]) -> dict:
    if not isinstance(anchors, list) or not 2 <= len(anchors) <= MAX_ANCHORS:
        raise ValueError(f"anchors must contain 2 to {MAX_ANCHORS} records")
    normalized = []
    session_id = source_id = None
    for item in anchors:
        if not isinstance(item, dict):
            raise ValueError("every anchor must be an object")
        session = item.get("session_id")
        source = item.get("source_id")
        if not isinstance(session, str) or not session.strip() or not isinstance(source, str) or not source.strip():
            raise ValueError("each anchor requires session_id and source_id")
        if session_id is None:
            session_id, source_id = session.strip(), source.strip()
        if session.strip() != session_id or source.strip() != source_id:
            raise ValueError("one clock model may contain only one session and source")
        source_time = _timestamp(item.get("source_timestamp"), "source_timestamp")
        reference_time = _timestamp(item.get("reference_timestamp"), "reference_timestamp")
        uncertainty = item.get("uncertainty_seconds", 0.0)
        if isinstance(uncertainty, bool) or not isinstance(uncertainty, (int, float)) or not isfinite(float(uncertainty)) or uncertainty < 0:
            raise ValueError("uncertainty_seconds must be finite and non-negative")
        normalized.append({
            "source_timestamp": source_time, "reference_timestamp": reference_time,
            "uncertainty_seconds": float(uncertainty),
        })
    normalized.sort(key=lambda item: item["source_timestamp"])
    for previous, current in zip(normalized, normalized[1:]):
        if current["source_timestamp"] <= previous["source_timestamp"]:
            raise ValueError("source anchor timestamps must be strictly increasing")
        if current["reference_timestamp"] <= previous["reference_timestamp"]:
            raise ValueError("reference anchor timestamps must be strictly increasing")
    drifts = []
    for previous, current in zip(normalized, normalized[1:]):
        source_seconds = (current["source_timestamp"] - previous["source_timestamp"]).total_seconds()
        reference_seconds = (current["reference_timestamp"] - previous["reference_timestamp"]).total_seconds()
        drifts.append((reference_seconds / source_seconds - 1.0) * 1_000_000)
    return {
        "session_id": session_id, "source_id": source_id,
        "anchors": [{
            "source_timestamp": item["source_timestamp"].isoformat(),
            "reference_timestamp": item["reference_timestamp"].isoformat(),
            "uncertainty_seconds": item["uncertainty_seconds"],
        } for item in normalized],
        "anchor_count": len(normalized),
        "max_absolute_drift_ppm": max(abs(value) for value in drifts),
        "drift_is_diagnostic_only": True,
        "extrapolation_permitted": False,
    }


def align_events(model: dict, events: list[dict]) -> dict:
    if not isinstance(model, dict) or model.get("anchor_count", 0) < 2:
        raise ValueError("a valid clock model is required")
    if not isinstance(events, list) or len(events) > MAX_EVENTS:
        raise ValueError(f"events must be a list of at most {MAX_EVENTS}")
    anchors = [{
        "source": _timestamp(item["source_timestamp"], "source_timestamp"),
        "reference": _timestamp(item["reference_timestamp"], "reference_timestamp"),
        "uncertainty": float(item["uncertainty_seconds"]),
    } for item in model["anchors"]]
    reports = []
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            raise ValueError("each event must be an object")
        if event.get("session_id") != model["session_id"] or event.get("source_id") != model["source_id"]:
            reports.append({"event_id": event.get("event_id", str(index)), "status": "different_session_or_source", "aligned_at": None, "extrapolation_used": False})
            continue
        instant = _timestamp(event.get("timestamp"), "event timestamp")
        if instant < anchors[0]["source"] or instant > anchors[-1]["source"]:
            reports.append({"event_id": event.get("event_id", str(index)), "status": "outside_anchor_range", "aligned_at": None, "extrapolation_used": False})
            continue
        right_index = next((i for i, anchor in enumerate(anchors) if anchor["source"] >= instant), len(anchors) - 1)
        if anchors[right_index]["source"] == instant:
            aligned = anchors[right_index]["reference"]
            uncertainty = anchors[right_index]["uncertainty"]
        else:
            left, right = anchors[right_index - 1], anchors[right_index]
            span = (right["source"] - left["source"]).total_seconds()
            fraction = (instant - left["source"]).total_seconds() / span
            reference_span = (right["reference"] - left["reference"]).total_seconds()
            aligned = left["reference"] + (right["reference"] - left["reference"]) * fraction
            uncertainty = left["uncertainty"] * (1 - fraction) + right["uncertainty"] * fraction
        reports.append({
            "event_id": event.get("event_id", str(index)), "status": "aligned_within_anchors",
            "aligned_at": aligned.isoformat(), "uncertainty_seconds": uncertainty,
            "extrapolation_used": False, "interpolation_fraction_not_a_probability": True,
        })
    return {
        "events": reports, "event_count": len(reports),
        "aligned_count": sum(item["status"] == "aligned_within_anchors" for item in reports),
        "session_isolation_preserved": True,
        "unrecorded_history_recovered": False,
        "event_identity_established": False,
        "future_prediction_performed": False,
    }

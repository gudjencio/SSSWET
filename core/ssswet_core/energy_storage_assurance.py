"""Bounded, provenance-aware analysis of researcher-supplied field power logs.

This module performs retrospective calculations only. It does not control chargers,
batteries, rescue equipment or other hardware, and it never certifies safety.
"""
from __future__ import annotations

from collections import OrderedDict, defaultdict
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
from statistics import median

MAX_SAMPLES = 20_000
MAX_CELLS = 128
MAX_PROTOCOL_BYTES = 1_000_000
MAX_METRICS_BYTES = 250_000
MAX_PACKET_BYTES = 2_000_000
VALID_MODES = {"charge", "discharge", "rest"}
SIGNAL_FIELDS = {"current_a", "voltage_v", "temperature_c"}
UNCERTAINTY_FIELDS = {"current_std_a", "voltage_std_v", "temperature_std_c"}


def _required_text(value: object, name: str, limit: int = 200) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f"{name} must be a non-empty string of at most {limit} characters")
    return value.strip()


def _number(value: object, name: str, minimum: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be a finite number")
    if minimum is not None and result < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    return result


def _timestamp(value: object) -> datetime:
    if not isinstance(value, str) or len(value) > 64:
        raise ValueError("timestamp_utc must be an ISO-8601 string with a timezone")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("timestamp_utc must be a valid ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamp_utc must include an explicit timezone")
    return parsed.astimezone(timezone.utc)


def _iso(value: datetime) -> str:
    return value.isoformat(timespec="microseconds").replace("+00:00", "Z")


def _canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _positive_limit(value: object, name: str) -> float:
    result = _number(value, name, 0.0)
    if result <= 0:
        raise ValueError(f"{name} must be greater than zero")
    return result


def validate_energy_samples(samples: object) -> list[dict]:
    """Validate and normalize a bounded log; unknown fields are deliberately omitted.

    Each sample must declare its session, cycle, mode, source, timestamp, current and
    voltage. Input order is preserved and timestamps must increase within each session.
    """
    if not isinstance(samples, (list, tuple)):
        raise ValueError("samples must be a list or tuple")
    if len(samples) > MAX_SAMPLES:
        raise ValueError(f"samples exceed the {MAX_SAMPLES} record limit")
    normalized: list[dict] = []
    seen_ids: set[str] = set()
    last_by_session: dict[str, datetime] = {}
    for index, raw in enumerate(samples):
        if not isinstance(raw, dict):
            raise ValueError(f"sample {index} must be an object")
        sample_id = _required_text(raw.get("sample_id"), "sample_id")
        session_id = _required_text(raw.get("session_id"), "session_id")
        cycle_id = _required_text(raw.get("cycle_id"), "cycle_id")
        source_id = _required_text(raw.get("source_id"), "source_id")
        if sample_id in seen_ids:
            raise ValueError("sample_id values must be unique")
        seen_ids.add(sample_id)
        mode = raw.get("mode")
        if not isinstance(mode, str) or mode not in VALID_MODES:
            raise ValueError("mode must be charge, discharge or rest")
        stamp = _timestamp(raw.get("timestamp_utc"))
        previous = last_by_session.get(session_id)
        if previous is not None and stamp <= previous:
            raise ValueError("timestamps must strictly increase within each session")
        last_by_session[session_id] = stamp
        current = _number(raw.get("current_a"), "current_a", 0.0)
        voltage = _number(raw.get("voltage_v"), "voltage_v", 0.0)
        if voltage <= 0:
            raise ValueError("voltage_v must be greater than zero")
        item = {
            "sample_id": sample_id,
            "session_id": session_id,
            "cycle_id": cycle_id,
            "source_id": source_id,
            "timestamp_utc": _iso(stamp),
            "mode": mode,
            "current_a": current,
            "voltage_v": voltage,
        }
        if raw.get("temperature_c") is not None:
            item["temperature_c"] = _number(raw["temperature_c"], "temperature_c")
        cells = raw.get("cell_voltages_v")
        if cells is not None:
            if not isinstance(cells, (list, tuple)) or len(cells) > MAX_CELLS:
                raise ValueError(f"cell_voltages_v must contain at most {MAX_CELLS} values")
            item["cell_voltages_v"] = [
                _number(value, "cell voltage", 0.0) for value in cells
            ]
            if any(value <= 0 for value in item["cell_voltages_v"]):
                raise ValueError("cell voltages must be greater than zero")
        refs = raw.get("calibration_refs", [])
        if not isinstance(refs, (list, tuple)) or len(refs) > 32:
            raise ValueError("calibration_refs must contain at most 32 identifiers")
        clean_refs = [_required_text(ref, "calibration reference") for ref in refs]
        if len(set(clean_refs)) != len(clean_refs):
            raise ValueError("calibration references must be unique per sample")
        if clean_refs:
            item["calibration_refs"] = clean_refs
        for field in UNCERTAINTY_FIELDS:
            if raw.get(field) is not None:
                item[field] = _number(raw[field], field, 0.0)
        normalized.append(item)
    return normalized


def segment_cycles(samples: object) -> list[dict]:
    """Group samples by explicitly declared session and cycle IDs.

    Incomplete or unexpectedly ordered cycles are retained and flagged; no cycle
    boundary is inferred from a current threshold.
    """
    normalized = validate_energy_samples(samples)
    groups: OrderedDict[tuple[str, str], list[dict]] = OrderedDict()
    for sample in normalized:
        groups.setdefault((sample["session_id"], sample["cycle_id"]), []).append(sample)
    results = []
    for (session_id, cycle_id), rows in groups.items():
        counts = {mode: sum(row["mode"] == mode for row in rows) for mode in sorted(VALID_MODES)}
        sequence: list[str] = []
        for row in rows:
            mode = row["mode"]
            if mode == "rest":
                continue
            if not sequence or sequence[-1] != mode:
                sequence.append(mode)
        flags = []
        if counts["charge"] == 0:
            flags.append("charge_observations_missing")
        if counts["discharge"] == 0:
            flags.append("discharge_observations_missing")
        if counts["charge"] and counts["discharge"] and sequence != ["charge", "discharge"]:
            flags.append("unexpected_charge_discharge_order")
        results.append({
            "session_id": session_id,
            "cycle_id": cycle_id,
            "sample_count": len(rows),
            "mode_counts": counts,
            "mode_sequence": sequence,
            "complete_charge_discharge_pair": counts["charge"] > 0 and counts["discharge"] > 0,
            "review_flags": flags,
            "sample_ids": [row["sample_id"] for row in rows],
            "source_ids": sorted({row["source_id"] for row in rows}),
            "first_timestamp_utc": rows[0]["timestamp_utc"],
            "last_timestamp_utc": rows[-1]["timestamp_utc"],
        })
    return results


def _cycle_mode_samples(
    samples: object,
    cycle_id: str,
    mode: str,
    session_id: str | None,
    max_gap_seconds: object,
) -> tuple[list[dict], float]:
    if mode not in {"charge", "discharge"}:
        raise ValueError("mode must be charge or discharge")
    gap_limit = _positive_limit(max_gap_seconds, "max_gap_seconds")
    normalized = validate_energy_samples(samples)
    cycle_id = _required_text(cycle_id, "cycle_id")
    matches = [row for row in normalized if row["cycle_id"] == cycle_id]
    sessions = {row["session_id"] for row in matches}
    if session_id is not None:
        session_id = _required_text(session_id, "session_id")
        matches = [row for row in matches if row["session_id"] == session_id]
    elif len(sessions) > 1:
        raise ValueError("cycle_id occurs in multiple sessions; session_id is required")
    cycle_rows = matches
    selected_positions = [index for index, row in enumerate(cycle_rows) if row["mode"] == mode]
    if len(selected_positions) < 2:
        raise ValueError(f"at least two {mode} samples are required in the selected cycle")
    if selected_positions != list(range(selected_positions[0], selected_positions[-1] + 1)):
        raise ValueError("integration cannot bridge an intervening rest or opposite-mode sample")
    selected = [cycle_rows[index] for index in selected_positions]
    stamps = [_timestamp(row["timestamp_utc"]) for row in selected]
    gaps = [(right - left).total_seconds() for left, right in zip(stamps, stamps[1:])]
    if any(gap <= 0 for gap in gaps):
        raise ValueError("selected sample timestamps must strictly increase")
    if any(gap > gap_limit for gap in gaps):
        raise ValueError("sample gap exceeds max_gap_seconds; integration was not performed")
    return selected, max(gaps, default=0.0)


def _integrate(
    samples: object,
    cycle_id: str,
    mode: str,
    field: str,
    session_id: str | None,
    max_gap_seconds: object,
) -> dict:
    rows, max_gap = _cycle_mode_samples(samples, cycle_id, mode, session_id, max_gap_seconds)
    stamps = [_timestamp(row["timestamp_utc"]) for row in rows]
    total = 0.0
    for left, right, t0, t1 in zip(rows, rows[1:], stamps, stamps[1:]):
        dt = (t1 - t0).total_seconds()
        if field == "capacity":
            v0, v1 = left["current_a"], right["current_a"]
        else:
            v0 = left["current_a"] * left["voltage_v"]
            v1 = right["current_a"] * right["voltage_v"]
        total += ((v0 + v1) / 2.0) * dt / 3600.0
    return {
        "cycle_id": cycle_id,
        "session_id": rows[0]["session_id"],
        "mode": mode,
        "metric": total,
        "unit": "Ah" if field == "capacity" else "Wh",
        "sample_count": len(rows),
        "integrated_intervals": len(rows) - 1,
        "max_observed_gap_seconds": max_gap,
        "sample_ids": [row["sample_id"] for row in rows],
        "source_ids": sorted({row["source_id"] for row in rows}),
        "calibration_refs": sorted({ref for row in rows for ref in row.get("calibration_refs", [])}),
        "method": "trapezoidal_integration",
    }


def integrate_capacity(
    samples: object,
    cycle_id: str,
    mode: str = "discharge",
    session_id: str | None = None,
    max_gap_seconds: float = 900.0,
) -> dict:
    """Integrate current magnitude over a single explicitly identified cycle/mode."""
    return _integrate(samples, cycle_id, mode, "capacity", session_id, max_gap_seconds)


def integrate_energy(
    samples: object,
    cycle_id: str,
    mode: str = "discharge",
    session_id: str | None = None,
    max_gap_seconds: float = 900.0,
) -> dict:
    """Integrate measured voltage × current over a single cycle/mode."""
    return _integrate(samples, cycle_id, mode, "energy", session_id, max_gap_seconds)


def round_trip_efficiency(
    samples: object,
    cycle_id: str,
    session_id: str | None = None,
    max_gap_seconds: float = 900.0,
) -> dict:
    """Compare integrated discharge and charge energy without clipping the ratio."""
    charge = integrate_energy(samples, cycle_id, "charge", session_id, max_gap_seconds)
    discharge = integrate_energy(samples, cycle_id, "discharge", session_id, max_gap_seconds)
    if charge["metric"] <= 0:
        raise ValueError("integrated charge energy must be greater than zero")
    efficiency = discharge["metric"] / charge["metric"] * 100.0
    return {
        "cycle_id": cycle_id,
        "session_id": charge["session_id"],
        "charge_energy_wh": charge["metric"],
        "discharge_energy_wh": discharge["metric"],
        "round_trip_efficiency_percent": efficiency,
        "review_flags": ["efficiency_above_100_percent_review"] if efficiency > 100.0 else [],
        "charge_provenance": charge,
        "discharge_provenance": discharge,
        "interpretation": "measured ratio only; not a product rating or safety determination",
    }


def capacity_fade(cycle_measurements: object) -> dict:
    """Fit a descriptive least-squares capacity trend; never extrapolate it."""
    if not isinstance(cycle_measurements, (list, tuple)) or len(cycle_measurements) > 5000:
        raise ValueError("cycle_measurements must contain at most 5000 records")
    points = []
    seen = set()
    for row in cycle_measurements:
        if not isinstance(row, dict):
            raise ValueError("each cycle measurement must be an object")
        number = row.get("cycle_number")
        if isinstance(number, bool) or not isinstance(number, int) or number < 1:
            raise ValueError("cycle_number must be a positive integer")
        if number in seen:
            raise ValueError("cycle_number values must be unique")
        seen.add(number)
        capacity = _number(row.get("capacity_ah"), "capacity_ah", 0.0)
        if capacity <= 0:
            raise ValueError("capacity_ah must be greater than zero")
        points.append((number, capacity))
    if len(points) < 3:
        raise ValueError("at least three unique cycle measurements are required")
    points.sort()
    xs = [float(point[0]) for point in points]
    ys = [point[1] for point in points]
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    denominator = sum((x - x_mean) ** 2 for x in xs)
    if denominator <= 0:
        raise ValueError("cycle numbers must span a non-zero range")
    slope = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / denominator
    intercept = y_mean - slope * x_mean
    residual = sum((y - (intercept + slope * x)) ** 2 for x, y in zip(xs, ys))
    total = sum((y - y_mean) ** 2 for y in ys)
    r_squared = 1.0 if total == 0 and residual == 0 else (0.0 if total == 0 else 1.0 - residual / total)
    return {
        "sample_count": len(points),
        "first_cycle": int(xs[0]),
        "last_cycle": int(xs[-1]),
        "slope_ah_per_cycle": slope,
        "relative_change_percent": (ys[-1] - ys[0]) / ys[0] * 100.0,
        "r_squared_descriptive": max(0.0, min(1.0, r_squared)),
        "trend_direction": "decreasing" if slope < 0 else ("increasing" if slope > 0 else "flat"),
        "extrapolation_performed": False,
        "cycle_numbers": [int(value) for value in xs],
    }


def temperature_excursions(
    samples: object,
    minimum_c: float,
    maximum_c: float,
    max_gap_seconds: float = 900.0,
) -> dict:
    """Count observations outside caller-supplied limits and only confirmed spans."""
    minimum = _number(minimum_c, "minimum_c")
    maximum = _number(maximum_c, "maximum_c")
    if minimum >= maximum:
        raise ValueError("minimum_c must be less than maximum_c")
    gap_limit = _positive_limit(max_gap_seconds, "max_gap_seconds")
    normalized = validate_energy_samples(samples)
    measured = [row for row in normalized if "temperature_c" in row]
    if not measured:
        raise ValueError("at least one temperature measurement is required")
    below = [row for row in measured if row["temperature_c"] < minimum]
    above = [row for row in measured if row["temperature_c"] > maximum]
    by_session: dict[str, list[dict]] = defaultdict(list)
    for row in measured:
        by_session[row["session_id"]].append(row)
    confirmed_seconds = 0.0
    for rows in by_session.values():
        for left, right in zip(rows, rows[1:]):
            t0, t1 = _timestamp(left["timestamp_utc"]), _timestamp(right["timestamp_utc"])
            dt = (t1 - t0).total_seconds()
            if dt > gap_limit:
                continue
            a, b = left["temperature_c"], right["temperature_c"]
            if (a < minimum and b < minimum) or (a > maximum and b > maximum):
                confirmed_seconds += dt
    values = [row["temperature_c"] for row in measured]
    return {
        "measurement_count": len(measured),
        "below_limit_count": len(below),
        "above_limit_count": len(above),
        "out_of_range_sample_ids": [row["sample_id"] for row in below + above],
        "minimum_observed_c": min(values),
        "maximum_observed_c": max(values),
        "confirmed_out_of_range_span_seconds": confirmed_seconds,
        "limits_c": {"minimum": minimum, "maximum": maximum},
        "duration_method": "sum of adjacent same-side out-of-range intervals only; no crossing interpolation",
        "safety_clearance_established": False,
    }


def cell_imbalance(samples: object, review_spread_v: float) -> dict:
    """Measure per-sample max-minus-min cell voltage spread against a supplied review limit."""
    threshold = _number(review_spread_v, "review_spread_v", 0.0)
    normalized = validate_energy_samples(samples)
    results = []
    for row in normalized:
        cells = row.get("cell_voltages_v")
        if cells is None:
            continue
        if len(cells) < 2:
            results.append({
                "sample_id": row["sample_id"],
                "cell_count": len(cells),
                "spread_v": None,
                "review_flag": "fewer_than_two_cell_measurements",
            })
            continue
        spread = max(cells) - min(cells)
        results.append({
            "sample_id": row["sample_id"],
            "cell_count": len(cells),
            "spread_v": spread,
            "review_flag": "spread_above_supplied_limit" if spread > threshold else None,
        })
    measured = [row["spread_v"] for row in results if row["spread_v"] is not None]
    if not results:
        raise ValueError("no cell_voltages_v measurements were supplied")
    return {
        "sample_count": len(results),
        "maximum_spread_v": max(measured) if measured else None,
        "median_spread_v": median(measured) if measured else None,
        "review_spread_limit_v": threshold,
        "samples": results,
        "safety_clearance_established": False,
    }


def detect_signal_anomalies(
    samples: object,
    fields: tuple[str, ...] = ("current_a", "voltage_v", "temperature_c"),
    robust_z_limit: float = 6.0,
) -> dict:
    """Flag robust-MAD outliers while retaining every source observation."""
    limit = _positive_limit(robust_z_limit, "robust_z_limit")
    if not isinstance(fields, (list, tuple)) or not fields:
        raise ValueError("fields must be a non-empty list or tuple")
    if any(not isinstance(field, str) or field not in SIGNAL_FIELDS for field in fields) or len(set(fields)) != len(fields):
        raise ValueError("fields contains an unsupported or duplicate signal")
    normalized = validate_energy_samples(samples)
    summaries = []
    anomalies = []
    for field in fields:
        rows = [row for row in normalized if field in row]
        values = [row[field] for row in rows]
        if len(values) < 5:
            summaries.append({"field": field, "sample_count": len(values), "status": "insufficient_samples"})
            continue
        centre = median(values)
        mad = median([abs(value - centre) for value in values])
        field_anomalies = []
        for row in rows:
            delta = row[field] - centre
            if mad == 0:
                flagged = delta != 0
                score = None
                reason = "deviation_from_zero_mad_baseline"
            else:
                score = 0.6744897501960817 * delta / mad
                flagged = abs(score) >= limit
                reason = "robust_mad_outlier"
            if flagged:
                item = {
                    "field": field,
                    "sample_id": row["sample_id"],
                    "value": row[field],
                    "median": centre,
                    "mad": mad,
                    "robust_z": score,
                    "reason": reason,
                }
                anomalies.append(item)
                field_anomalies.append(row["sample_id"])
        summaries.append({
            "field": field,
            "sample_count": len(values),
            "median": centre,
            "mad": mad,
            "flagged_sample_ids": field_anomalies,
            "method": "median_absolute_deviation",
        })
    return {
        "fields": summaries,
        "anomalies": anomalies,
        "source_observations_removed": 0,
        "interpretation": "screening flags only; investigate sensor faults and genuine transients separately",
    }


def _flatten_protocol(value: object, prefix: str = "", depth: int = 0) -> dict[str, object]:
    if depth > 16:
        raise ValueError("protocol nesting exceeds 16 levels")
    if isinstance(value, dict):
        if not value:
            return {prefix or "$": {}}
        flattened = {}
        if any(not isinstance(key, str) or not key.strip() or len(key) > 200 for key in value):
            raise ValueError("protocol keys must be non-empty strings of at most 200 characters")
        for key in sorted(value):
            path = f"{prefix}.{key}" if prefix else key
            flattened.update(_flatten_protocol(value[key], path, depth + 1))
        return flattened
    _canonical(value)
    return {prefix or "$": value}


def compare_protocols(previous: object, current: object) -> dict:
    """Fingerprint and compare bounded JSON-compatible protocol revisions."""
    if not isinstance(previous, dict) or not isinstance(current, dict):
        raise ValueError("protocol revisions must be objects")
    previous_text, current_text = _canonical(previous), _canonical(current)
    if len(previous_text.encode("utf-8")) > MAX_PROTOCOL_BYTES or len(current_text.encode("utf-8")) > MAX_PROTOCOL_BYTES:
        raise ValueError("protocol revision exceeds the 1 MB limit")
    old, new = _flatten_protocol(previous), _flatten_protocol(current)
    old_keys, new_keys = set(old), set(new)
    added = sorted(new_keys - old_keys)
    removed = sorted(old_keys - new_keys)
    changed = [
        {"path": key, "previous": old[key], "current": new[key]}
        for key in sorted(old_keys & new_keys) if old[key] != new[key]
    ]
    return {
        "schema_version": 1,
        "previous_sha256": sha256(previous_text.encode("utf-8")).hexdigest(),
        "current_sha256": sha256(current_text.encode("utf-8")).hexdigest(),
        "added_paths": added,
        "removed_paths": removed,
        "changed_paths": changed,
        "unchanged_path_count": len(old_keys & new_keys) - len(changed),
        "same_revision": previous_text == current_text,
    }


def build_evidence_packet(
    samples: object,
    protocol: object,
    metrics: object,
    calibration_refs: object = (),
    software_version: str = "ssswet-energy-assurance/1",
) -> dict:
    """Create a deterministic, bounded manifest; source files remain with the researcher."""
    normalized = validate_energy_samples(samples)
    if not normalized:
        raise ValueError("at least one source sample is required")
    if not isinstance(protocol, dict):
        raise ValueError("protocol must be an object")
    protocol_text = _canonical(protocol)
    if len(protocol_text.encode("utf-8")) > MAX_PROTOCOL_BYTES:
        raise ValueError("protocol revision exceeds the 1 MB limit")
    if not isinstance(metrics, dict):
        raise ValueError("metrics must be an object")
    metrics_text = _canonical(metrics)
    if len(metrics_text.encode("utf-8")) > MAX_METRICS_BYTES:
        raise ValueError("metrics exceed the 250 KB limit")
    if not isinstance(calibration_refs, (list, tuple)) or len(calibration_refs) > 1000:
        raise ValueError("calibration_refs must contain at most 1000 identifiers")
    declared_refs = sorted({_required_text(ref, "calibration reference") for ref in calibration_refs})
    sample_refs = sorted({ref for row in normalized for ref in row.get("calibration_refs", [])})
    packet = {
        "schema_version": 1,
        "kind": "ssswet.energy_storage_assurance",
        "software_version": _required_text(software_version, "software_version", 100),
        "sample_count": len(normalized),
        "sample_sha256": sha256(_canonical(normalized).encode("utf-8")).hexdigest(),
        "protocol_sha256": sha256(protocol_text.encode("utf-8")).hexdigest(),
        "source_ids": sorted({row["source_id"] for row in normalized}),
        "session_ids": sorted({row["session_id"] for row in normalized}),
        "cycle_ids": sorted({row["cycle_id"] for row in normalized}),
        "calibration_refs": declared_refs,
        "sample_calibration_refs": sample_refs,
        "unresolved_calibration_refs": sorted(set(sample_refs) - set(declared_refs)),
        "metrics": json.loads(metrics_text),
        "review_state": "not_reviewed",
        "release_authorized": False,
        "limitations": [
            "Manifest integrity does not authenticate authorship or source instruments.",
            "The packet does not contain raw samples; retain source files under the applicable privacy policy.",
            "Caller-supplied metrics and thresholds require independent review.",
            "This analysis does not certify battery, equipment or operational safety.",
        ],
    }
    packet["packet_sha256"] = sha256(_canonical(packet).encode("utf-8")).hexdigest()
    if len(_canonical(packet).encode("utf-8")) > MAX_PACKET_BYTES:
        raise ValueError("evidence packet exceeds the 2 MB limit")
    return packet


def verify_evidence_packet(packet: object, samples: object | None = None) -> dict:
    """Verify manifest integrity and, optionally, the digest of supplied source samples."""
    issues = []
    if not isinstance(packet, dict):
        return {"valid": False, "issues": ["packet_must_be_an_object"]}
    try:
        if len(_canonical(packet).encode("utf-8")) > MAX_PACKET_BYTES:
            return {"valid": False, "issues": ["packet_exceeds_size_limit"], "manifest_integrity_only": True, "authorship_authenticated": False, "scientific_validity_established": False}
    except (TypeError, ValueError):
        return {"valid": False, "issues": ["packet_payload_not_canonical_json"], "manifest_integrity_only": True, "authorship_authenticated": False, "scientific_validity_established": False}
    digest = packet.get("packet_sha256")
    if not isinstance(digest, str) or len(digest) != 64:
        issues.append("packet_digest_missing_or_malformed")
    else:
        payload = dict(packet)
        payload.pop("packet_sha256", None)
        try:
            actual = sha256(_canonical(payload).encode("utf-8")).hexdigest()
            if actual != digest:
                issues.append("packet_digest_mismatch")
        except (TypeError, ValueError):
            issues.append("packet_payload_not_canonical_json")
    if packet.get("schema_version") != 1:
        issues.append("unsupported_schema_version")
    if packet.get("release_authorized") is not False:
        issues.append("unexpected_release_authorization_state")
    if samples is not None:
        try:
            normalized = validate_energy_samples(samples)
            source_digest = sha256(_canonical(normalized).encode("utf-8")).hexdigest()
            if source_digest != packet.get("sample_sha256"):
                issues.append("source_sample_digest_mismatch")
        except (TypeError, ValueError):
            issues.append("source_samples_invalid")
    return {
        "valid": not issues,
        "issues": issues,
        "manifest_integrity_only": True,
        "authorship_authenticated": False,
        "scientific_validity_established": False,
    }

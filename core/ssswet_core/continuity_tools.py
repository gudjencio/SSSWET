"""Bounded continuity tools for memory retrieval, agent hand-offs and temporal evidence.

These helpers organize research records. They do not establish scientific truth,
resolve contradictions, reconstruct unrecorded history or predict future events.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import unicodedata
from datetime import date, datetime, timezone
from typing import Iterable, Mapping, Sequence

SNAPSHOT_SCHEMA_VERSION = 1
DEFAULT_HANDOFF_LIMIT = 8
MAX_HANDOFF_LIMIT = 30
MAX_HANDOFF_CHARS = 24_000
MAX_TEMPORAL_GAPS = 500


def _canonical_text(value: object) -> str:
    return " ".join(unicodedata.normalize("NFKC", str(value or "")).casefold().split())


def normalize_memory_query(query: str) -> tuple[str, ...]:
    """Return stable Unicode-normalized query tokens, preserving meaningful terms."""
    if not isinstance(query, str):
        raise TypeError("query must be a string")
    normalized = unicodedata.normalize("NFKC", query).casefold()
    return tuple(dict.fromkeys(
        re.findall(r"[\w]+(?:['’-][\w]+)*", normalized, flags=re.UNICODE)
    ))


def search_memory_records(
    records: Iterable[Mapping], query: str, *, limit: int = 20,
    campaign_id: str | None = None, statuses: Sequence[str] | None = None,
    provenance_group: str | None = None, include_rejected: bool = False,
) -> list[dict]:
    """Search bounded records with transparent field weighting and explicit filters."""
    tokens = set(normalize_memory_query(query))
    if not tokens:
        return []
    limit = max(1, min(int(limit), 100))
    allowed = set(statuses) if statuses is not None else None
    ranked = []
    for raw in records:
        record = dict(raw)
        status = str(record.get("status", "candidate"))
        if status == "rejected" and not include_rejected:
            continue
        if allowed is not None and status not in allowed:
            continue
        if campaign_id is not None and record.get("campaign_id", "") != campaign_id:
            continue
        if provenance_group is not None and record.get("provenance_group", "") != provenance_group:
            continue
        fields = {
            "topic": set(normalize_memory_query(str(record.get("topic", "")))),
            "statement": set(normalize_memory_query(str(record.get("statement", "")))),
            "campaign": set(normalize_memory_query(str(record.get("campaign_id", "")))),
        }
        matched = tokens & (fields["topic"] | fields["statement"] | fields["campaign"])
        if not matched:
            continue
        weighted = (
            2.0 * len(tokens & fields["topic"])
            + 1.0 * len(tokens & fields["statement"])
            + 0.25 * len(tokens & fields["campaign"])
        )
        score = round(weighted / max(1.0, 2.0 * len(tokens)), 6)
        ranked.append({
            **record, "retrieval_score": score,
            "matched_terms": sorted(matched),
            "retrieval_method": "weighted_lexical_v1",
            "scientific_validity_established": False,
        })
    ranked.sort(key=lambda item: (
        -item["retrieval_score"], str(item.get("updated_at", "")),
        str(item.get("memory_id", "")),
    ))
    return ranked[:limit]


def group_exact_memory_duplicates(records: Iterable[Mapping]) -> list[dict]:
    """Group exact normalized topic/statement duplicates without merging records."""
    groups: dict[tuple[str, str], list[dict]] = {}
    for raw in records:
        record = dict(raw)
        key = (_canonical_text(record.get("topic", "")),
               _canonical_text(record.get("statement", "")))
        if not all(key):
            continue
        groups.setdefault(key, []).append(record)
    result = []
    for key, members in groups.items():
        if len(members) < 2:
            continue
        result.append({
            "canonical_topic": key[0],
            "canonical_statement": key[1],
            "memory_ids": sorted(str(m.get("memory_id", "")) for m in members),
            "source_ids": sorted({str(s) for m in members for s in m.get("source_ids", [])}),
            "record_count": len(members),
            "merge_performed": False,
        })
    return sorted(result, key=lambda g: (g["canonical_topic"], g["memory_ids"]))


def candidate_memory_conflicts(records: Iterable[Mapping]) -> list[dict]:
    """Flag same-topic opposite-polarity wording for review; never adjudicate it."""
    positive = re.compile(r"\b(is|are|does|do|can|will|increases|supports|present)\b", re.I)
    negative = re.compile(r"\b(not|no|never|cannot|can't|isn't|aren't|doesn't|don't|without|absent)\b", re.I)
    by_topic: dict[str, list[dict]] = {}
    for raw in records:
        record = dict(raw)
        topic = _canonical_text(record.get("topic", ""))
        statement = str(record.get("statement", ""))
        if topic and statement and record.get("status", "candidate") != "rejected":
            by_topic.setdefault(topic, []).append(record)
    conflicts = []
    for topic, members in by_topic.items():
        for index, left in enumerate(members):
            for right in members[index + 1:]:
                a, b = str(left.get("statement", "")), str(right.get("statement", ""))
                opposite = (bool(negative.search(a)) != bool(negative.search(b)))
                shared = set(normalize_memory_query(a)) & set(normalize_memory_query(b))
                shared -= {"not", "no", "never", "cannot", "can", "is", "are", "does", "do"}
                if opposite and shared and (positive.search(a) or positive.search(b)):
                    conflicts.append({
                        "topic": topic,
                        "memory_ids": sorted((str(left.get("memory_id", "")),
                                              str(right.get("memory_id", "")))),
                        "shared_terms": sorted(shared),
                        "reason": "opposite-polarity lexical signal",
                        "requires_human_review": True,
                        "scientific_contradiction_established": False,
                    })
    return sorted(conflicts, key=lambda item: (item["topic"], item["memory_ids"]))


def build_memory_snapshot(records: Iterable[Mapping], *, created_at: str | None = None) -> dict:
    """Create a deterministic, versioned and tamper-evident memory export."""
    normalized = [dict(record) for record in records]
    normalized.sort(key=lambda r: str(r.get("memory_id", "")))
    ids = [str(r.get("memory_id", "")) for r in normalized]
    if any(not item for item in ids) or len(ids) != len(set(ids)):
        raise ValueError("snapshot memory IDs must be present and unique")
    payload = {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "created_at": created_at or datetime.now(timezone.utc).isoformat(),
        "record_count": len(normalized),
        "records": normalized,
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":"), allow_nan=False)
    return {**payload, "sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest()}


def validate_memory_snapshot(snapshot: Mapping) -> dict:
    """Validate schema, count, unique IDs and canonical payload digest."""
    if not isinstance(snapshot, Mapping) or snapshot.get("schema_version") != SNAPSHOT_SCHEMA_VERSION:
        raise ValueError("unsupported memory snapshot schema")
    records = snapshot.get("records")
    if not isinstance(records, list):
        raise ValueError("snapshot records must be a list")
    if snapshot.get("record_count") != len(records):
        raise ValueError("snapshot record_count does not match records")
    ids = [str(r.get("memory_id", "")) for r in records if isinstance(r, Mapping)]
    if len(ids) != len(records) or any(not item for item in ids) or len(ids) != len(set(ids)):
        raise ValueError("snapshot memory IDs must be present and unique")
    payload = {k: snapshot[k] for k in ("schema_version", "created_at", "record_count", "records")}
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":"), allow_nan=False)
    expected = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    if snapshot.get("sha256") != expected:
        raise ValueError("snapshot checksum mismatch")
    return {"valid": True, "schema_version": SNAPSHOT_SCHEMA_VERSION,
            "record_count": len(records), "sha256": expected}


def build_agent_handoff(
    records: Iterable[Mapping], query: str, *, campaign_id: str | None = None,
    max_records: int = DEFAULT_HANDOFF_LIMIT, max_chars: int = MAX_HANDOFF_CHARS,
) -> dict:
    """Build a bounded, provenance-preserving hand-off packet for another agent."""
    max_records = max(1, min(int(max_records), MAX_HANDOFF_LIMIT))
    max_chars = max(1_000, min(int(max_chars), MAX_HANDOFF_CHARS))
    matches = search_memory_records(records, query, limit=100, campaign_id=campaign_id)
    selected = []
    for record in matches:
        compact = {
            key: record.get(key) for key in (
                "memory_id", "topic", "statement", "campaign_id", "status",
                "source_ids", "provenance_group", "confidence", "review_note",
                "retrieval_score", "matched_terms",
            ) if key in record
        }
        candidate = selected + [compact]
        if len(json.dumps(candidate, ensure_ascii=False, separators=(",", ":"))) > max_chars:
            break
        selected.append(compact)
        if len(selected) >= max_records:
            break
    packet = {
        "schema_version": 1,
        "query": query,
        "campaign_id": campaign_id,
        "records": selected,
        "source_ids": sorted({str(s) for r in selected for s in r.get("source_ids", [])}),
        "constraints": [
            "Treat retrieved statements as claims, not established facts.",
            "Preserve source IDs and provenance groups in downstream work.",
            "Keep rejected or superseded claims distinct from reviewed claims.",
            "Escalate apparent contradictions for human review; do not silently resolve them.",
            "Do not infer missing observations or present simulations as measurements.",
        ],
        "human_review_required": True,
        "truncated": len(selected) < len(matches),
    }
    packet["character_count"] = len(json.dumps(packet, ensure_ascii=False, separators=(",", ":")))
    return packet


def parse_temporal_instant(value: str) -> dict:
    """Parse ISO date or timezone-aware ISO datetime into a UTC instant."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("timestamp must be a non-empty ISO string")
    raw = value.strip()
    try:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
            parsed = datetime.combine(date.fromisoformat(raw), datetime.min.time(), tzinfo=timezone.utc)
            precision = "date"
        else:
            parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            if parsed.tzinfo is None or parsed.utcoffset() is None:
                raise ValueError("datetime timestamps must include a timezone")
            parsed = parsed.astimezone(timezone.utc)
            precision = "instant"
    except (ValueError, OverflowError) as exc:
        raise ValueError("timestamp must be a valid ISO date or timezone-aware datetime") from exc
    return {"utc": parsed, "precision": precision}


def query_temporal_window(
    observations: Iterable[Mapping], *, start: str | None = None,
    end: str | None = None, max_uncertainty_seconds: float | None = None,
) -> list[dict]:
    """Select observations in an inclusive UTC interval with finite uncertainty."""
    lower = parse_temporal_instant(start)["utc"] if start else None
    upper = parse_temporal_instant(end)["utc"] if end else None
    if lower and upper and lower > upper:
        raise ValueError("start must not be after end")
    if max_uncertainty_seconds is not None and (
        not math.isfinite(float(max_uncertainty_seconds)) or max_uncertainty_seconds < 0
    ):
        raise ValueError("max_uncertainty_seconds must be finite and non-negative")
    selected = []
    for raw in observations:
        item = dict(raw)
        instant = parse_temporal_instant(str(item.get("timestamp", "")))["utc"]
        uncertainty = float(item.get("uncertainty_seconds", 0))
        if not math.isfinite(uncertainty) or uncertainty < 0:
            raise ValueError("observation uncertainty must be finite and non-negative")
        if lower and instant < lower or upper and instant > upper:
            continue
        if max_uncertainty_seconds is not None and uncertainty > max_uncertainty_seconds:
            continue
        selected.append((instant, item))
    selected.sort(key=lambda pair: (pair[0], str(pair[1].get("source_id", ""))))
    return [item for _, item in selected]


def temporal_coverage_gaps(
    observations: Iterable[Mapping], *, start: str, end: str,
    cadence_seconds: float, tolerance_seconds: float = 0,
    max_gaps: int = MAX_TEMPORAL_GAPS,
) -> list[dict]:
    """Report expected cadence slots without a nearby observation; not proof of absence."""
    cadence = float(cadence_seconds)
    tolerance = float(tolerance_seconds)
    if not math.isfinite(cadence) or cadence <= 0:
        raise ValueError("cadence_seconds must be finite and positive")
    if not math.isfinite(tolerance) or tolerance < 0:
        raise ValueError("tolerance_seconds must be finite and non-negative")
    limit = max(1, min(int(max_gaps), MAX_TEMPORAL_GAPS))
    lower = parse_temporal_instant(start)["utc"]
    upper = parse_temporal_instant(end)["utc"]
    if lower > upper:
        raise ValueError("start must not be after end")
    instants = [parse_temporal_instant(str(item.get("timestamp", "")))["utc"]
                for item in observations]
    gaps = []
    current = lower
    while current <= upper and len(gaps) < limit:
        if not any(abs((seen - current).total_seconds()) <= tolerance for seen in instants):
            gaps.append({"expected_at": current.isoformat(), "cadence_seconds": cadence,
                         "status": "no_nearby_recorded_observation",
                         "absence_of_event_established": False})
        current = current.fromtimestamp(current.timestamp() + cadence, tz=timezone.utc)
    return gaps


def compare_temporal_observations(
    left: Iterable[Mapping], right: Iterable[Mapping],
) -> list[dict]:
    """Compare timestamps for shared source IDs and retain combined uncertainty."""
    def index(items: Iterable[Mapping]) -> dict[str, dict]:
        result = {}
        for raw in items:
            item = dict(raw)
            source_id = str(item.get("source_id", "")).strip()
            if not source_id or source_id in result:
                raise ValueError("source IDs must be present and unique within each timeline")
            instant = parse_temporal_instant(str(item.get("timestamp", "")))["utc"]
            uncertainty = float(item.get("uncertainty_seconds", 0))
            if not math.isfinite(uncertainty) or uncertainty < 0:
                raise ValueError("uncertainty must be finite and non-negative")
            result[source_id] = {**item, "_instant": instant, "_uncertainty": uncertainty}
        return result
    a, b = index(left), index(right)
    result = []
    for source_id in sorted(a.keys() & b.keys()):
        delta = (b[source_id]["_instant"] - a[source_id]["_instant"]).total_seconds()
        combined = a[source_id]["_uncertainty"] + b[source_id]["_uncertainty"]
        result.append({
            "source_id": source_id, "delta_seconds": delta,
            "combined_uncertainty_seconds": combined,
            "difference_exceeds_combined_uncertainty": abs(delta) > combined,
            "interpretation": "timestamp difference only; cause is not inferred",
        })
    return result

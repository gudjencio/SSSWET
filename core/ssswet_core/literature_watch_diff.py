"""Run-to-run literature-watch comparison without retraction or truth claims."""
from __future__ import annotations

import json
from typing import Any

from .source_identity import canonicalize_url

MAX_CANDIDATES = 200


def _identity(candidate: dict[str, Any]) -> str:
    doi = str(candidate.get("doi", "")).strip().casefold()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if doi.startswith(prefix):
            doi = doi[len(prefix):]
    if doi and doi not in {"unavailable", "unknown", "n/a", "not available"}:
        return "doi:" + doi
    source_id = str(candidate.get("source_id", "")).strip()
    if source_id.casefold().startswith("arxiv:"):
        return "arxiv:" + source_id.split(":", 1)[1].casefold()
    url = str(candidate.get("url", "")).strip()
    if url:
        try:
            return "url:" + canonicalize_url(url)
        except ValueError:
            pass
    return "source:" + source_id if source_id else ""


def _signature(candidate: dict[str, Any]) -> str:
    fields = {
        key: candidate.get(key)
        for key in (
            "title", "doi", "url", "provider", "classification",
            "provider_observations", "metadata_conflicts",
        )
    }
    return json.dumps(fields, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def compare_watch_reports(
    older: dict[str, Any],
    newer: dict[str, Any],
    *,
    max_candidates: int = MAX_CANDIDATES,
) -> dict[str, Any]:
    if not isinstance(older, dict) or not isinstance(newer, dict):
        raise ValueError("older and newer reports must be objects")
    if isinstance(max_candidates, bool) or not isinstance(max_candidates, int) or not 1 <= max_candidates <= MAX_CANDIDATES:
        raise ValueError(f"max_candidates must be between 1 and {MAX_CANDIDATES}")
    older_items = older.get("candidates", [])
    newer_items = newer.get("candidates", [])
    if not isinstance(older_items, list) or not isinstance(newer_items, list):
        raise ValueError("report candidates must be lists")
    if len(older_items) > max_candidates or len(newer_items) > max_candidates:
        raise ValueError(f"each report may contain at most {max_candidates} candidates")
    if any(not isinstance(item, dict) for item in older_items + newer_items):
        raise ValueError("every candidate must be an object")

    def index(items):
        result: dict[str, list[dict[str, Any]]] = {}
        unidentified = []
        for item in items:
            key = _identity(item)
            if not key:
                unidentified.append(item)
                continue
            result.setdefault(key, []).append(item)
        return result, unidentified

    old_index, old_unidentified = index(older_items)
    new_index, new_unidentified = index(newer_items)
    added, absent, changed, ambiguous = [], [], [], []
    for key in sorted(set(old_index) | set(new_index)):
        old_group, new_group = old_index.get(key, []), new_index.get(key, [])
        if len(old_group) > 1 or len(new_group) > 1:
            ambiguous.append({
                "identity": key,
                "older_count": len(old_group),
                "newer_count": len(new_group),
                "reason": "identity_not_unique_within_report",
            })
            continue
        if not old_group:
            added.append({"identity": key, "candidate": new_group[0]})
        elif not new_group:
            absent.append({"identity": key, "candidate": old_group[0]})
        elif _signature(old_group[0]) != _signature(new_group[0]):
            changed.append({
                "identity": key,
                "older": old_group[0],
                "newer": new_group[0],
                "metadata_change_is_not_correction": True,
            })

    return {
        "older_watch_id": older.get("watch_id", ""),
        "newer_watch_id": newer.get("watch_id", ""),
        "added": added,
        "absent_from_newer": absent,
        "metadata_changed": changed,
        "ambiguous_identities": ambiguous,
        "unidentified_candidate_counts": {
            "older": len(old_unidentified),
            "newer": len(new_unidentified),
        },
        "counts": {
            "added": len(added),
            "absent_from_newer": len(absent),
            "metadata_changed": len(changed),
            "ambiguous": len(ambiguous),
        },
        "absence_is_not_retraction": True,
        "metadata_change_is_not_a_correction": True,
        "scientific_validity_established": False,
        "memory_changed": False,
        "automatic_adjudication": False,
    }

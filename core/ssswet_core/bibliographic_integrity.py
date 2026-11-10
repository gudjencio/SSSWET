"""Bibliographic integrity checks for scholarly source records.

Detects metadata-level duplicates and publication-status warnings. It does not
assess truth, methodological validity, peer-review quality, or independence.
"""
from __future__ import annotations

import re
import unicodedata
from collections import defaultdict
from typing import Any

MAX_RECORDS = 2000


def normalize_doi(value: Any) -> str:
    """Normalize common DOI URL/prefix forms without guessing missing identifiers."""
    raw = str(value or "").strip().casefold()
    raw = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", raw)
    raw = re.sub(r"^doi\s*:\s*", "", raw)
    return raw.strip().rstrip(".,;)")


def normalize_title(value: Any) -> str:
    """Normalize exact-title matching; this is not fuzzy semantic matching."""
    text = unicodedata.normalize("NFKC", str(value or "")).casefold()
    text = re.sub(r"[^\w]+", " ", text, flags=re.UNICODE)
    return " ".join(text.split())


def _as_list(value: Any) -> list:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [item for item in value if item not in (None, "")]
    return [value] if value != "" else []


def _publication_flags(record: dict[str, Any]) -> list[str]:
    flags: list[str] = []
    status_values = [
        record.get("publication_status"),
        record.get("status"),
        record.get("type"),
        record.get("work_type"),
    ]
    relations = record.get("relation") or record.get("relations") or {}
    relation_text = str(relations).casefold() if relations else ""
    status_text = " ".join(str(value).casefold() for value in status_values if value)
    combined = status_text + " " + relation_text
    if record.get("is_retracted") is True or any(term in combined for term in ("retract", "retraction", "is-retracted-by")):
        flags.append("retraction_status_signal")
    if any(term in combined for term in ("expression of concern", "expression-of-concern", "concern")):
        flags.append("expression_of_concern_signal")
    if any(term in combined for term in ("correction", "erratum", "corrigendum", "is-correction-of")):
        flags.append("correction_or_erratum_signal")
    if record.get("is_preprint") is True or any(term in combined for term in ("preprint", "posted-content")):
        flags.append("preprint_or_posted_content")
    return flags


def analyze_bibliographic_integrity(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Return auditable DOI/title duplicate groups and metadata review flags."""
    if not isinstance(records, list) or len(records) > MAX_RECORDS:
        raise ValueError(f"records must be a list of at most {MAX_RECORDS} items")
    if any(not isinstance(item, dict) for item in records):
        raise ValueError("every bibliographic record must be a dictionary")

    doi_groups: dict[str, list[str]] = defaultdict(list)
    title_groups: dict[tuple[str, str], list[str]] = defaultdict(list)
    reviewed: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for index, record in enumerate(records):
        source_id = str(record.get("source_id") or record.get("id") or f"record:{index}").strip()
        if source_id in seen_ids:
            source_id = f"{source_id}#{index}"
        seen_ids.add(source_id)

        doi = normalize_doi(record.get("doi") or record.get("DOI"))
        title = normalize_title(record.get("title") or record.get("display_name"))
        year = str(record.get("publication_year") or record.get("year") or "")[:4]
        if doi:
            doi_groups[doi].append(source_id)
        if title and year:
            title_groups[(title, year)].append(source_id)

        flags = _publication_flags(record)
        authors = _as_list(record.get("authors") or record.get("author") or record.get("authorships"))
        venue = record.get("venue") or record.get("journal") or record.get("container_title") or record.get("source")
        publication_date = record.get("publication_date") or record.get("published") or record.get("date") or year
        if not doi:
            flags.append("doi_missing")
        if not authors:
            flags.append("author_metadata_missing")
        if not publication_date:
            flags.append("publication_date_missing")
        if not venue:
            flags.append("venue_metadata_missing")
        if record.get("peer_reviewed") is not True and not record.get("peer_review_status"):
            flags.append("peer_review_status_not_established")

        reviewed.append({
            "source_id": source_id,
            "normalized_doi": doi or None,
            "normalized_title": title or None,
            "publication_year": year or None,
            "flags": sorted(set(flags)),
            "review_required": bool(flags),
        })

    duplicate_groups = []
    for basis, groups in (("doi", doi_groups), ("exact_title_and_year", title_groups)):
        for key, source_ids in sorted(groups.items(), key=lambda item: str(item[0])):
            if len(source_ids) > 1:
                duplicate_groups.append({
                    "basis": basis,
                    "normalized_key": key,
                    "source_ids": sorted(source_ids),
                    "count": len(source_ids),
                    "requires_human_confirmation": True,
                })

    retraction_count = sum("retraction_status_signal" in row["flags"] for row in reviewed)
    correction_count = sum("correction_or_erratum_signal" in row["flags"] for row in reviewed)
    preprint_count = sum("preprint_or_posted_content" in row["flags"] for row in reviewed)
    return {
        "record_count": len(records),
        "records": reviewed,
        "duplicate_groups": duplicate_groups,
        "duplicate_record_count": len({sid for group in duplicate_groups for sid in group["source_ids"]}),
        "retraction_signal_count": retraction_count,
        "correction_signal_count": correction_count,
        "preprint_signal_count": preprint_count,
        "metadata_review_required_count": sum(row["review_required"] for row in reviewed),
        "automatic_deduplication": False,
        "publication_status_verified": False,
        "scientific_validity_established": False,
        "notice": (
            "DOI and exact-title/year groups are duplicate candidates, not automatic deletion instructions. "
            "Publication-status flags are metadata signals that must be checked against the publisher's "
            "version of record and authoritative notices. Missing metadata means unknown, not negative. "
            "No score or flag establishes scientific truth, peer-review quality, or study independence."
        ),
    }

"""Conservative detection of duplicated or syndicated research sources.

analyze_sources is the preferred independence audit. group_sources remains a
legacy metadata-bucket helper for callers that historically grouped by the
first available publisher/DOI/domain field; those buckets must not be treated
as evidence of independent corroboration.
"""
from __future__ import annotations

import hashlib
import re
from urllib.parse import urlsplit


def _text(value: object) -> str:
    return " ".join(str(value or "").casefold().split())


def _doi(value: object) -> str:
    text = str(value or "").strip().casefold()
    text = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", text)
    text = re.sub(r"^doi:\s*", "", text)
    return text.rstrip(" .")


def _url(value: object) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    parsed = urlsplit(raw if "://" in raw else "https://" + raw)
    if not parsed.hostname:
        return ""
    host = parsed.hostname.casefold().removeprefix("www.")
    port = parsed.port
    if port and not ((parsed.scheme == "https" and port == 443) or
                     (parsed.scheme == "http" and port == 80)):
        host += f":{port}"
    path = re.sub(r"/{2,}", "/", parsed.path).rstrip("/")
    return host + path


def analyze_sources(sources: list[dict]) -> dict:
    if not isinstance(sources, list):
        raise ValueError("sources must be a list")
    ids: list[str] = []
    records: list[dict] = []
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError("each source must be a dictionary")
        source_id = source.get("id")
        if not isinstance(source_id, str) or not source_id.strip():
            raise ValueError("every source requires a non-empty string id")
        source_id = source_id.strip()
        if source_id in ids:
            raise ValueError(f"duplicate source id: {source_id}")
        ids.append(source_id)
        records.append(source)

    parent = {source_id: source_id for source_id in ids}
    signals: dict[str, set[str]] = {}

    def find(item: str) -> str:
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(left: str, right: str) -> None:
        a, b = find(left), find(right)
        if a != b:
            low, high = sorted((a, b))
            parent[high] = low

    identity_index: dict[str, list[str]] = {}
    domain_counts: dict[str, int] = {}
    publisher_counts: dict[str, int] = {}
    for source_id, source in zip(ids, records):
        doi = _doi(source.get("doi"))
        canonical_url = _url(source.get("url") or source.get("source_url"))
        canonical_id = _text(source.get("canonical_source_id") or source.get("syndicated_from"))
        publisher = _text(source.get("publisher"))
        title = _text(source.get("title"))
        domain = _text(source.get("domain"))
        if canonical_id:
            identity_index.setdefault("canonical:" + canonical_id, []).append(source_id)
            signals.setdefault(source_id, set()).add("canonical_source_id")
        if doi:
            identity_index.setdefault("doi:" + doi, []).append(source_id)
            signals.setdefault(source_id, set()).add("doi")
        if canonical_url:
            identity_index.setdefault("url:" + canonical_url, []).append(source_id)
            signals.setdefault(source_id, set()).add("canonical_url")
        if publisher and title:
            identity_index.setdefault("publisher_title:" + publisher + "|" + title, []).append(source_id)
            signals.setdefault(source_id, set()).add("publisher_title")
        if domain:
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        if publisher:
            publisher_counts[publisher] = publisher_counts.get(publisher, 0) + 1

    for key, members in identity_index.items():
        if len(members) > 1:
            for member in members[1:]:
                union(members[0], member)
            for member in members:
                signals.setdefault(member, set()).add(key.split(":", 1)[0])

    grouped: dict[str, list[str]] = {}
    for source_id in ids:
        grouped.setdefault(find(source_id), []).append(source_id)

    groups = []
    mapping = {}
    for members in sorted((sorted(items) for items in grouped.values()), key=lambda x: x[0]):
        group_id = "src-" + hashlib.sha256("|".join(members).encode("utf-8")).hexdigest()[:12]
        mapping[group_id] = members
        matched = sorted({signal for member in members for signal in signals.get(member, set())})
        groups.append({
            "group_id": group_id,
            "source_ids": members,
            "duplicate_candidate": len(members) > 1,
            "match_signals": matched,
        })

    duplicate_groups = [item for item in groups if item["duplicate_candidate"]]
    return {
        "groups": groups,
        "group_map": mapping,
        "source_count": len(ids),
        "independent_group_count": len(groups),
        "duplicate_candidate_count": sum(len(item["source_ids"]) - 1 for item in duplicate_groups),
        "duplicate_groups": duplicate_groups,
        "domain_counts": dict(sorted(domain_counts.items())),
        "publisher_counts": dict(sorted(publisher_counts.items())),
        "domain_or_publisher_alone_used_to_merge": False,
        "scientific_independence_certified": False,
    }


def group_sources(sources: list[dict]) -> dict:
    """Preserve legacy publisher/DOI/domain metadata buckets for compatibility."""
    groups = {}
    for source in sources:
        key = source.get("publisher") or source.get("doi") or source.get("domain") or source.get("id")
        groups.setdefault(str(key).casefold(), []).append(source.get("id"))
    return {key: sorted(value) for key, value in sorted(groups.items())}

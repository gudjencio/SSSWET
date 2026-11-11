"""Strong-identifier source normalization and conservative duplicate clustering."""
from __future__ import annotations

import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

MAX_SOURCES = 2000
_TRACKING = {
    "fbclid", "gclid", "dclid", "mc_cid", "mc_eid", "igshid",
    "ref_src", "utm_campaign", "utm_content", "utm_medium",
    "utm_source", "utm_term",
}


def canonicalize_url(value: str) -> str:
    """Normalize an HTTP(S) URL while preserving content-bearing query fields."""
    if not isinstance(value, str) or not value.strip() or len(value) > 4000:
        raise ValueError("url must contain 1 to 4000 characters")
    parts = urlsplit(value.strip())
    if parts.scheme.lower() not in {"http", "https"} or not parts.hostname:
        raise ValueError("only absolute HTTP(S) URLs are accepted")
    if parts.username or parts.password:
        raise ValueError("URLs containing user credentials are not accepted")
    host = parts.hostname.encode("idna").decode("ascii").lower()
    if host.startswith("www."):
        host = host[4:]
    try:
        port = parts.port
    except ValueError as exc:
        raise ValueError("URL port is invalid") from exc
    netloc = host if port is None or (parts.scheme.lower(), port) in {("http", 80), ("https", 443)} else f"{host}:{port}"
    path = re.sub(r"/{2,}", "/", parts.path or "/")
    if path != "/":
        path = path.rstrip("/")
    query = [
        (key, val) for key, val in parse_qsl(parts.query, keep_blank_values=True)
        if key.casefold() not in _TRACKING
    ]
    query.sort(key=lambda pair: (pair[0], pair[1]))
    return urlunsplit((parts.scheme.lower(), netloc, path, urlencode(query, doseq=True), ""))


def _normalize_doi(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("doi must be a string")
    cleaned = value.strip().casefold()
    cleaned = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", cleaned)
    cleaned = re.sub(r"^doi:\s*", "", cleaned)
    if not re.fullmatch(r"10\.\d{4,9}/[-._;()/:a-z0-9]+", cleaned):
        raise ValueError("doi is not in a recognized DOI form")
    return cleaned


def _normalize_arxiv(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("arxiv_id must be a string")
    cleaned = value.strip().casefold()
    cleaned = re.sub(r"^https?://arxiv\.org/(?:abs|pdf)/", "", cleaned)
    cleaned = cleaned.removesuffix(".pdf")
    if not re.fullmatch(r"(?:\d{4}\.\d{4,5}|[a-z-]+(?:\.[a-z-]+)?/\d{7})(?:v\d+)?", cleaned):
        raise ValueError("arXiv identifier is not recognized")
    return cleaned


def source_identity(record: dict) -> dict:
    if not isinstance(record, dict):
        raise ValueError("source record must be an object")
    source_id = record.get("source_id")
    if not isinstance(source_id, str) or not source_id.strip() or len(source_id) > 240:
        raise ValueError("source_id is required")
    keys = []
    if record.get("doi"):
        keys.append("doi:" + _normalize_doi(record["doi"]))
    if record.get("arxiv_id"):
        keys.append("arxiv:" + _normalize_arxiv(record["arxiv_id"]))
    canonical_url = canonicalize_url(record["url"]) if record.get("url") else ""
    if canonical_url:
        keys.append("url:" + canonical_url)
    checksum = record.get("content_sha256", "")
    if checksum not in ("", None):
        if not isinstance(checksum, str) or not re.fullmatch(r"[a-fA-F0-9]{64}", checksum):
            raise ValueError("content_sha256 must be a 64-character hexadecimal digest")
        keys.append("sha256:" + checksum.lower())
    return {
        "source_id": source_id.strip(),
        "canonical_url": canonical_url,
        "strong_identity_keys": sorted(set(keys)),
        "title_used_for_identity": False,
    }


def cluster_sources(records: list[dict]) -> dict:
    """Cluster only shared DOI, arXiv ID, canonical URL or exact content hash."""
    if not isinstance(records, list) or len(records) > MAX_SOURCES:
        raise ValueError(f"records must be a list of at most {MAX_SOURCES} items")
    identities = [source_identity(item) for item in records]
    ids = [item["source_id"] for item in identities]
    if len(ids) != len(set(ids)):
        raise ValueError("source_id values must be unique")
    parent = list(range(len(records)))

    def find(index):
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(left, right):
        a, b = find(left), find(right)
        if a != b:
            parent[max(a, b)] = min(a, b)

    owner = {}
    for index, identity in enumerate(identities):
        for key in identity["strong_identity_keys"]:
            if key in owner:
                union(index, owner[key])
            else:
                owner[key] = index
    groups = {}
    for index, identity in enumerate(identities):
        groups.setdefault(find(index), []).append(identity)
    clusters = []
    for group in groups.values():
        if len(group) < 2:
            continue
        clusters.append({
            "source_ids": sorted(item["source_id"] for item in group),
            "shared_identity_keys": sorted(set.intersection(*[
                set(item["strong_identity_keys"]) for item in group
            ])) if len(group) == 2 else sorted({
                key for item in group for key in item["strong_identity_keys"]
                if sum(key in other["strong_identity_keys"] for other in group) > 1
            }),
            "canonical_urls": sorted({item["canonical_url"] for item in group if item["canonical_url"]}),
            "original_records_preserved": True,
            "duplicate_confirmed": False,
        })
    clustered = {source_id for group in clusters for source_id in group["source_ids"]}
    return {
        "clusters": sorted(clusters, key=lambda item: item["source_ids"]),
        "unclustered_source_ids": sorted(set(ids) - clustered),
        "source_count": len(records),
        "cluster_count": len(clusters),
        "title_only_matches_used": False,
        "records_deleted_or_merged": False,
        "identity_is_not_scientific_independence": True,
    }

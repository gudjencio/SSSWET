"""Review-oriented literature watch over scholarly metadata providers."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import re
import uuid
from typing import Protocol

from .providers import ProviderResult


class LiteratureProvider(Protocol):
    name: str
    def investigate(self, objective: str, strategy: str) -> ProviderResult: ...


def _normalize_doi(value: str) -> str:
    return value.strip().casefold().removeprefix("https://doi.org/").removeprefix("http://doi.org/").removeprefix("doi:")


def _tokens(value: str) -> set[str]:
    ignored = {"the", "and", "for", "with", "from", "this", "that", "les", "des", "une", "pour", "dans", "avec", "sur"}
    return {word for word in re.findall(r"[\w-]{3,}", value.casefold()) if word not in ignored}


def _title_similarity(left: str, right: str) -> float:
    a, b = _tokens(left), _tokens(right)
    return len(a & b) / len(a | b) if a and b else 0.0


@dataclass(frozen=True)
class WatchCandidate:
    candidate_id: str
    provider: str
    source_id: str
    title: str
    doi: str = ""
    url: str = ""
    duplicate_source_ids: tuple[str, ...] = ()
    similar_source_ids: tuple[str, ...] = ()
    related_memory_ids: tuple[str, ...] = ()
    classification: str = "candidate_for_review"
    note: str = "Bibliographic metadata only; inspect the publication and its methods."
    provider_observations: tuple[dict, ...] = ()
    metadata_conflicts: tuple[str, ...] = ()


@dataclass(frozen=True)
class LiteratureWatchReport:
    watch_id: str
    query: str
    created_at: str
    provider: str
    provider_summary: str
    candidates: tuple[WatchCandidate, ...]
    provider_errors: tuple[str, ...] = ()
    scientific_validity_established: bool = False
    memory_changed: bool = False
    campaign_changed: bool = False

    @classmethod
    def create(cls, query: str, provider: str, result: ProviderResult,
               store: object, *, title_similarity_threshold: float = 0.85) -> "LiteratureWatchReport":
        if not query.strip():
            raise ValueError("A non-empty literature watch query is required.")
        if not 0.5 <= title_similarity_threshold <= 1.0:
            raise ValueError("Title similarity threshold must be between 0.5 and 1.0.")
        known_sources = store._all_source_records()
        memories = store.collective_memory_items(limit=500)
        candidates = []
        for source_id, raw in zip(result.source_ids, result.evidence):
            evidence = raw.strip()
            provider_name = provider
            match = re.match(r"^\[([^]]+)\]\s*(.*)$", evidence)
            if match:
                provider_name, evidence = match.group(1), match.group(2)
            parts = [part.strip() for part in evidence.split("|")]
            title = parts[0] if parts else ""
            if not title:
                continue
            doi_match = re.search(r"\bDOI:\s*([^|]+)", evidence, re.IGNORECASE)
            doi = _normalize_doi(doi_match.group(1)) if doi_match else ""
            url_match = re.search(r"\bURL:\s*(https?://\S+)", evidence, re.IGNORECASE)
            url = url_match.group(1).rstrip(".,)") if url_match else ""
            exact = []
            similar = []
            for known in known_sources:
                same_doi = bool(doi and _normalize_doi(known.get("doi", "")) == doi)
                if same_doi:
                    exact.append(known["source_id"])
                elif _title_similarity(title, known.get("title", "")) >= title_similarity_threshold:
                    similar.append(known["source_id"])
            title_terms = _tokens(title)
            related_memory = []
            for memory in memories:
                memory_terms = _tokens(memory.get("topic", "") + " " + memory.get("statement", ""))
                if title_terms and len(title_terms & memory_terms) / len(title_terms) >= 0.35:
                    related_memory.append(memory["memory_id"])
            classification = "possible_duplicate" if exact else (
                "possible_title_match" if similar else "candidate_for_review"
            )
            provenance_record = next(
                (
                    item for item in getattr(result, "provenance", ())
                    if isinstance(item, dict) and item.get("identity") == source_id
                ),
                None,
            )
            observations = tuple(
                item for item in (provenance_record or {}).get("provider_records", [])
                if isinstance(item, dict)
            )
            if not observations:
                observations = ({
                    "identity": source_id,
                    "provider": provider_name,
                    "source_id": source_id,
                    "evidence": raw,
                },)

            observed_fields = {"title": set(), "year": set(), "doi": set()}
            for observation in observations:
                observed_text = re.sub(r"^\[[^]]+\]\s*", "", str(observation.get("evidence", "")))
                observed_parts = [part.strip() for part in observed_text.split("|")]
                if observed_parts and observed_parts[0]:
                    observed_fields["title"].add(re.sub(r"\s+", " ", observed_parts[0]).casefold())
                year_match = re.search(r"\b(?:19|20)\d{2}\b", observed_text)
                if year_match:
                    observed_fields["year"].add(year_match.group(0))
                doi_value = re.search(r"\bDOI:\s*([^|]+)", observed_text, re.IGNORECASE)
                if doi_value:
                    normalized_doi = _normalize_doi(doi_value.group(1))
                    if normalized_doi and normalized_doi not in {"unavailable", "unknown"}:
                        observed_fields["doi"].add(normalized_doi)
            metadata_conflicts = tuple(sorted(
                field for field, values in observed_fields.items() if len(values) > 1
            ))
            provider_names = sorted({
                str(item.get("provider", "")).strip()
                for item in observations if str(item.get("provider", "")).strip()
            })
            candidates.append(WatchCandidate(
                candidate_id=str(uuid.uuid4()), provider="+".join(provider_names) or provider_name,
                source_id=source_id, title=title, doi=doi, url=url,
                duplicate_source_ids=tuple(sorted(set(exact))),
                similar_source_ids=tuple(sorted(set(similar))),
                related_memory_ids=tuple(sorted(set(related_memory))),
                classification=classification,
                provider_observations=observations,
                metadata_conflicts=metadata_conflicts,
            ))
        return cls(
            watch_id=str(uuid.uuid4()), query=query.strip(),
            created_at=datetime.now(timezone.utc).isoformat(),
            provider=provider, provider_summary=result.summary,
            candidates=tuple(candidates),
        )


class LiteratureWatchService:
    """Runs a metadata search and stores a review report; it never promotes findings."""
    def __init__(self, provider: LiteratureProvider, store: object):
        self.provider, self.store = provider, store

    def run(self, query: str) -> LiteratureWatchReport:
        result = self.provider.investigate(query, "literature_watch")
        report = LiteratureWatchReport.create(query, self.provider.name, result, self.store)
        self.store.save_literature_watch(report)
        return report


def report_to_dict(report: LiteratureWatchReport) -> dict:
    return asdict(report)

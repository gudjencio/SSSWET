from dataclasses import dataclass
import re
from typing import Protocol


@dataclass(frozen=True)
class ProviderResult:
    summary: str
    evidence: tuple[str, ...] = ()
    uncertainty: float = 1.0
    source_ids: tuple[str, ...] = ()


class ResearchProvider(Protocol):
    name: str

    def investigate(self, objective: str, strategy: str) -> ProviderResult:
        ...


@dataclass(frozen=True)
class CorpusDocument:
    source_id: str
    title: str
    text: str
    url: str = ""

    def __post_init__(self) -> None:
        if not self.source_id.strip() or not self.title.strip() or not self.text.strip():
            raise ValueError("Corpus documents require a source ID, title and text.")


class LocalCorpusProvider:
    """Search a caller-supplied document corpus without inventing findings."""

    name = "local-document-corpus"

    def __init__(self, documents: list[CorpusDocument] | None = None, max_results: int = 5):
        self.documents = list(documents or [])
        self.max_results = max(1, max_results)

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return {
            token for token in re.findall(r"[\w-]{2,}", text.casefold())
            if token not in {"the", "and", "for", "with", "that", "this", "les", "des", "une", "pour", "dans"}
        }

    def investigate(self, objective: str, strategy: str) -> ProviderResult:
        query_tokens = self._tokens(objective)
        if not query_tokens:
            return ProviderResult("No searchable terms were found in the research objective.")

        ranked: list[tuple[float, CorpusDocument]] = []
        for document in self.documents:
            document_tokens = self._tokens(document.title + " " + document.text)
            overlap = query_tokens & document_tokens
            if not overlap:
                continue
            score = len(overlap) / max(1, len(query_tokens))
            ranked.append((score, document))

        ranked.sort(key=lambda item: (-item[0], item[1].source_id))
        selected = ranked[:self.max_results]
        if not selected:
            return ProviderResult(
                "No matching documents were found in the supplied local corpus.",
                uncertainty=1.0,
            )

        evidence = tuple(
            f"[{doc.source_id}] {doc.title}: " +
            re.sub(r"\s+", " ", doc.text).strip()[:500]
            for _, doc in selected
        )
        source_ids = tuple(doc.source_id for _, doc in selected)
        return ProviderResult(
            summary=f"Found {len(selected)} potentially relevant document(s) in the supplied corpus. Relevance is lexical, not scientific validation.",
            evidence=evidence,
            uncertainty=1.0,
            source_ids=source_ids,
        )


class DeterministicDemoProvider:
    """Safe local provider used until real research/model providers are configured."""

    name = "deterministic-demo"

    def investigate(self, objective: str, strategy: str) -> ProviderResult:
        return ProviderResult(
            summary=f"Demo research pass for: {objective}",
            evidence=(f"Strategy recorded: {strategy}",),
            uncertainty=1.0,
        )


class CrossrefProvider:
    """Retrieve scholarly publication metadata from the public Crossref API.

    This provider discovers bibliographic records; it does not read or validate
    full papers and never treats publication metadata as proof of a claim.
    """

    name = "crossref-literature-search"
    endpoint = "https://api.crossref.org/works"

    def __init__(self, max_results: int = 5, timeout: float = 12.0, mailto: str = ""):
        self.max_results = max(1, min(int(max_results), 20))
        self.timeout = max(2.0, min(float(timeout), 30.0))
        self.mailto = mailto.strip()

    def investigate(self, objective: str, strategy: str) -> ProviderResult:
        from urllib.error import HTTPError, URLError
        from urllib.parse import urlencode
        from urllib.request import Request, urlopen
        import json

        query = objective.strip()
        if not query:
            return ProviderResult("The literature search objective is empty.", uncertainty=1.0)

        parameters = {"query.bibliographic": query, "rows": self.max_results}
        if self.mailto:
            parameters["mailto"] = self.mailto
        url = self.endpoint + "?" + urlencode(parameters)
        request = Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "SSSWET/0.1 (scholarly metadata discovery; contact: " +
                (self.mailto or "no-contact-provided") + ")",
            },
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            return ProviderResult(
                f"Crossref literature search unavailable: {type(exc).__name__}. No result was inferred.",
                uncertainty=1.0,
            )

        message = payload.get("message", {}) if isinstance(payload, dict) else {}
        items = message.get("items", []) if isinstance(message, dict) else []
        evidence: list[str] = []
        source_ids: list[str] = []
        for item in items[:self.max_results]:
            if not isinstance(item, dict):
                continue
            titles = item.get("title") or []
            title = str(titles[0]).strip() if titles else ""
            if not title:
                continue
            doi = str(item.get("DOI", "")).strip()
            url_value = str(item.get("URL", "")).strip()
            publisher = str(item.get("publisher", "")).strip()
            date_parts = (
                item.get("published-print", {}).get("date-parts")
                or item.get("published-online", {}).get("date-parts")
                or item.get("created", {}).get("date-parts")
                or []
            )
            year = date_parts[0][0] if date_parts and date_parts[0] else "date unavailable"
            authors = item.get("author") or []
            author_names = [
                " ".join(part for part in (author.get("given"), author.get("family")) if part)
                for author in authors[:4] if isinstance(author, dict)
            ]
            author_text = ", ".join(author_names) or "authors unavailable"
            identity = doi or url_value
            if not identity:
                continue
            source_ids.append(identity)
            evidence.append(
                f"{title} | {author_text} | {year} | {publisher or 'publisher unavailable'} "
                f"| DOI: {doi or 'unavailable'} | URL: {url_value}"
            )

        if not evidence:
            return ProviderResult(
                "Crossref returned no usable bibliographic records for this query.",
                uncertainty=1.0,
            )
        return ProviderResult(
            summary=(
                f"Crossref returned {len(evidence)} bibliographic record(s). "
                "These are discovery leads only; abstracts, full texts, methods and claims "
                "must be reviewed independently."
            ),
            evidence=tuple(evidence),
            uncertainty=1.0,
            source_ids=tuple(source_ids),
        )
